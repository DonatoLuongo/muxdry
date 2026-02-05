from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from products.models import Product


@login_required
@require_POST
def submit_review_view(request):
    """Vista para enviar una reseña desde la página del producto (solo usuarios autenticados)."""
    product_id = request.POST.get('product_id')
    product_slug = request.POST.get('product_slug', '')
    if not product_id:
        messages.error(request, 'Producto no indicado.')
        return redirect('products:product_detail', slug=product_slug) if product_slug else redirect('home')
    product = get_object_or_404(Product, pk=product_id)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'Ya has enviado una reseña para este producto.')
        return redirect('products:product_detail', slug=product.slug)
    rating = request.POST.get('rating')
    title = (request.POST.get('title') or '').strip() or 'Mi opinión'
    comment = (request.POST.get('comment') or '').strip()
    if not rating or not comment:
        messages.error(request, 'Indica una calificación (1-5) y escribe tu comentario.')
        return redirect('products:product_detail', slug=product.slug)
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError('Rating fuera de rango')
    except (ValueError, TypeError):
        messages.error(request, 'La calificación debe ser un número del 1 al 5.')
        return redirect('products:product_detail', slug=product.slug)
    if len(title) > 200:
        title = title[:200]
    Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        title=title,
        comment=comment,
        approved=True,
    )
    messages.success(request, 'Tu reseña se ha guardado correctamente.')
    return redirect('products:product_detail', slug=product.slug)


class ReviewViewSet(viewsets.ModelViewSet):
    """API para reseñas"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        # CORREGIDO: Usar 'approved=True' en lugar de 'is_active=True'
        queryset = Review.objects.filter(approved=True).select_related('user', 'product')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Si es admin, mostrar todas las reseñas
        if self.request.user.is_staff:
            queryset = Review.objects.all().select_related('user', 'product')
        
        return queryset
    
    def get_permissions(self):
        """Permitir lectura pública de reseñas"""
        if self.action in ['list', 'retrieve', 'product_reviews']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)', permission_classes=[AllowAny])
    def product_reviews(self, request, product_id=None):
        """Obtener reseñas de un producto específico"""
        # CORREGIDO: Cambiar 'activo' por el nombre correcto del campo
        # Primero verifica si el producto existe
        product = get_object_or_404(Product, id=product_id)
        
        # Obtener las más recientes y mejor calificadas
        sort_by = request.query_params.get('sort', 'recent')  # 'recent' o 'rating'
        limit = int(request.query_params.get('limit', 3))
        
        # CORREGIDO: Usar 'approved=True' en lugar de 'is_active=True'
        queryset = Review.objects.filter(product=product, approved=True).select_related('user')
        
        if sort_by == 'rating':
            queryset = queryset.order_by('-rating', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Limitar resultados
        reviews = queryset[:limit]
        total_reviews = queryset.count()
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response({
            'reviews': serializer.data,
            'total': total_reviews,
            'showing': len(reviews),
            'has_more': total_reviews > limit
        })
    
    @action(detail=True, methods=['put', 'patch'])
    def update_review(self, request, pk=None):
        """Actualizar reseña existente"""
        review = self.get_object()
        
        if review.user != request.user:
            return Response(
                {'error': 'No tienes permiso para actualizar esta reseña'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = ReviewSerializer(review)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_review(self, request, pk=None):
        """Eliminar reseña (soft delete)"""
        review = self.get_object()
        
        if review.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permiso para eliminar esta reseña'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # CORREGIDO: Cambiar a 'approved=False' en lugar de 'is_active=False'
        review.approved = False
        review.save()
        return Response({'message': 'Reseña eliminada'})
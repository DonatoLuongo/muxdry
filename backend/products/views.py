from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product, Category

# Mapeo slug -> template para productos estáticos
PRODUCT_TEMPLATES = {
    'barra-am': 'products/Barra-AM.html',
    'duradry-barra': 'products/Barra-AM.html',
    'xerac-ac': 'products/Xerac-AC.html',
    'xerac': 'products/Xerac-AC.html',
    'drysol': 'products/Drysol.html',
    'wash': 'products/Wash.html',
    'duradry-wash': 'products/Wash.html',
    'desodorante-corporal': 'products/Desodorante-Corporal.html',
}


def information_view(request):
    """Página de información, términos, privacidad."""
    return render(request, 'information.html')


def contact_view(request):
    """Recibe el formulario de contacto y envía email al ADMIN_EMAIL."""
    if request.method != 'POST':
        return redirect('/#contacto-footer')
    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    subject = (request.POST.get('subject') or '').strip()
    body = (request.POST.get('message') or '').strip()
    if not name or not email or not body:
        messages.warning(request, 'Por favor completa nombre, email y mensaje.')
        return redirect('/#contacto-footer')
    admin_email = getattr(settings, 'ADMIN_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    if not admin_email:
        messages.warning(request, 'El formulario de contacto no está configurado. Intenta más tarde.')
        return redirect('/#contacto-footer')
    subject_line = f"[MUXDRY Contacto] {subject or 'Sin asunto'}"
    message_body = f"Nombre: {name}\nEmail: {email}\n\nMensaje:\n{body}"
    try:
        send_mail(
            subject_line,
            message_body,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
        messages.success(request, 'Mensaje enviado correctamente. Te responderemos pronto.')
    except Exception:
        messages.error(request, 'No se pudo enviar el mensaje. Intenta de nuevo más tarde.')
    return redirect('/#contacto-footer')


def home_view(request):
    products = Product.objects.all().order_by('-is_featured', '-created_at')
    # Productos para carrusel "Más demandado": destacados o los de más ventas (hasta 4 slides)
    viral_products = list(Product.objects.filter(is_featured=True)[:4])
    if not viral_products:
        viral_products = list(Product.objects.order_by('-sales_count')[:4])
    if not viral_products and products:
        viral_products = list(products[:4])
    context = {
        'products': products,
        'featured_products': Product.objects.filter(is_featured=True)[:8],
        'best_sellers': Product.objects.filter(is_best_seller=True).order_by('-sales_count')[:4],
        'featured_product': Product.objects.filter(is_featured=True).first(),
        'viral_products': viral_products,
        'categories': Category.objects.all(),
        'banners': [
            {'image': 'assets/Banner/mux-1.png', 'alt': 'Oferta 1'},
            {'image': 'assets/Banner/mux-2.png', 'alt': 'Oferta 2'},
            {'image': 'assets/Banner/mux-3.png', 'alt': 'Oferta 3'},
        ]
    }
    return render(request, 'index.html', context)


def product_detail_view(request, slug):
    """Detalle de producto por slug (template genérico) con reseñas paginadas."""
    from reviews.models import Review
    product = get_object_or_404(Product, slug=slug)
    reviews_qs = Review.objects.filter(product=product, approved=True).select_related('user').order_by('-created_at')
    paginator = Paginator(reviews_qs, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    context = {
        'product': product,
        'reviews_page': page_obj,
        'user_can_review': request.user.is_authenticated and not user_has_reviewed,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'products/detail.html', context)


def category_view(request, slug):
    """Lista productos por categoría."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'index.html', {
        'category': category,
        'products': products,
        'categories': Category.objects.all(),
    })


def search_view(request):
    """Búsqueda de productos."""
    q = request.GET.get('q', '').strip()
    if q:
        products = Product.objects.filter(name__icontains=q).order_by('-is_featured', '-created_at')
    else:
        products = Product.objects.none()
    return render(request, 'index.html', {
        'search_query': q,
        'products': products,
        'categories': Category.objects.all(),
    })


def product_barra_view(request):
    """Página del producto Barra AM."""
    return render(request, 'products/Barra-AM.html')


def product_xerac_view(request):
    """Página del producto Xerac AC."""
    return render(request, 'products/Xerac-AC.html')


def product_drysol_view(request):
    """Página del producto Drysol."""
    return render(request, 'products/Drysol.html')


def product_wash_view(request):
    """Página del producto Wash."""
    return render(request, 'products/Wash.html')


def product_desodorante_view(request):
    """Página del producto Desodorante Corporal."""
    return render(request, 'products/Desodorante-Corporal.html')
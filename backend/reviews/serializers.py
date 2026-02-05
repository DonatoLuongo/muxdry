from rest_framework import serializers
from .models import Review
from django.contrib.auth import get_user_model
from orders.models import OrderItem

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información del usuario
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'user', 'user_email', 'user_name', 'product', 'rating', 
            'title', 'comment', 'verified_purchase', 'approved',
            'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'user_email', 'user_name', 'verified_purchase', 
                          'approved', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuario no autenticado.")
            
        user = request.user
        product = attrs.get('product')
        
        if not product:
            raise serializers.ValidationError("Producto requerido.")
        
        # Verificar si el usuario ha comprado el producto (para verified_purchase)
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status='delivered',  # Solo pedidos entregados
            product=product
        ).exists()
        
        # Si no ha comprado, aún puede reseñar pero no será verified_purchase
        attrs['verified_purchase'] = has_purchased
        
        # Verificar si ya existe una reseña
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "Ya has reseñado este producto. Puedes actualizar tu reseña existente."
            )
        
        return attrs
    
    def create(self, validated_data):
        # Asignar automáticamente el usuario actual
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar reseñas"""
    class Meta:
        model = Review
        fields = ('rating', 'title', 'comment')
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 1 y 5.")
        return value
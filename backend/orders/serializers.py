from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total']

    def get_total(self, obj):
        return obj.total

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'payment_method', 'payment_method_display', 'payment_status',
            'subtotal', 'shipping', 'tax', 'total',
            'shipping_name', 'shipping_address', 'shipping_city',
            'shipping_phone', 'shipping_email', 'notes',
            'items', 'created_at', 'updated_at',
            'paid_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'order_number', 'user', 'status', 'subtotal', 'shipping', 'tax', 'total',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    payment_method = serializers.CharField(max_length=20, default='transfer')
    shipping_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_phone = serializers.CharField(max_length=20)
    shipping_email = serializers.EmailField()
    notes = serializers.CharField(required=False, allow_blank=True)
    shipping = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

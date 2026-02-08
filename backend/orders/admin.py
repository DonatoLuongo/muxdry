from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem, Cart, CartItem, OrderMessage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_total_display',)
    
    def item_total_display(self, obj):
        return f"${float(obj.total):.2f}" if obj.pk else "-"
    item_total_display.short_description = 'Total'


class OrderMessageInline(admin.TabularInline):
    model = OrderMessage
    extra = 1
    fields = ('message', 'is_from_admin', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'status_display', 'total', 'payment_method_display',
        'items_count', 'created_at', 'status_color'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__username', 'shipping_email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
    inlines = [OrderItemInline, OrderMessageInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('order_number', 'user', 'status', 'total', 'payment_method', 'payment_status')
        }),
        ('Datos del Cliente', {
            'fields': ('document',)
        }),
        ('Información de Envío', {
            'fields': ('shipping_type', 'shipping_agency', 'office_pickup', 'central_address',
                      'shipping_name', 'shipping_address', 'shipping_city', 
                      'shipping_phone', 'shipping_email')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Estado'
    
    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = 'Método de Pago'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'
    
    def status_color(self, obj):
        colors = {
            'pending': '#ffc107',      # Amarillo
            'confirmed': '#17a2b8',    # Cyan
            'processing': '#007bff',   # Azul
            'shipped': '#28a745',      # Verde
            'delivered': '#20c997',    # Verde claro
            'cancelled': '#dc3545',    # Rojo
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_color.short_description = 'Estado (Color)'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = 'Marcar como Procesando'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = 'Marcar como Enviado'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = 'Marcar como Entregado'
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = 'Marcar como Cancelado'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, OrderMessage) and not obj.sender_id:
                obj.sender = request.user
            obj.save()
        formset.save_m2m()


@admin.register(OrderMessage)
class OrderMessageAdmin(admin.ModelAdmin):
    list_display = ('order', 'sender', 'is_from_admin', 'created_at', 'read_at')
    list_filter = ('is_from_admin',)
    search_fields = ('order__order_number',)  # message está encriptado, no buscable


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_price', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'item_total', 'created_at_display')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('item_total_display', 'created_at_display')
    
    def item_total(self, obj):
        return f"${obj.total:.2f}"
    item_total.short_description = 'Total'
    
    def item_total_display(self, obj):
        return f"${obj.total:.2f}"
    item_total_display.short_description = 'Total'
    
    def created_at_display(self, obj):
        return obj.order.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Fecha del Pedido'
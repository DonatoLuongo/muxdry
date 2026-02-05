from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'approved', 'verified_purchase', 'created_at')
    list_filter = ('rating', 'approved', 'verified_purchase', 'created_at')
    search_fields = ('user__email', 'product__name', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at', 'verified_purchase')
    fieldsets = (
        ('Información de la Reseña', {
            'fields': ('user', 'product', 'rating', 'title', 'comment')
        }),
        ('Verificación', {
            'fields': ('verified_purchase', 'approved'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Método para mostrar el nombre del producto
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Producto'
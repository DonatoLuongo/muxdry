# backend/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Desregistra el User por defecto si quieres personalizarlo (opcional)
# admin.site.unregister(User)

# Registra UserProfile como inline en User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fk_name = 'user'

# Crea un UserAdmin personalizado que incluya UserProfile
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    # Puedes agregar campos personalizados a la vista de lista
    list_display = UserAdmin.list_display + ('get_phone', 'get_email_verified')
    
    def get_phone(self, instance):
        return instance.profile.phone if hasattr(instance, 'profile') else '-'
    get_phone.short_description = 'Teléfono'
    
    def get_email_verified(self, instance):
        if hasattr(instance, 'profile'):
            return '✅' if instance.profile.email_verified else '❌'
        return '-'
    get_email_verified.short_description = 'Email Verificado'
    
    # Sobreescribe get_inline_instances para mostrar solo cuando hay objeto
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Desregistra el UserAdmin por defecto y registra el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# También puedes registrar UserProfile directamente si quieres
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country', 'email_verified')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    list_filter = ('email_verified', 'country')
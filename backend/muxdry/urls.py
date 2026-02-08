from django.contrib import admin

# Panel admin: solo superusuarios (Gestor BD). URL no obvia para mayor seguridad.
_original_has_permission = admin.site.has_permission

def _secure_admin_has_permission(request):
    return _original_has_permission(request) and getattr(request.user, 'is_superuser', False)

admin.site.has_permission = _secure_admin_has_permission

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from muxdry.views import health_check_view, preview_404_view
from products.views import home_view, information_view, contact_view
from accounts.views import RegisterAPIView, LoginAPIView, ProfileAPIView, LogoutAPIView, SyncSessionAPIView

urlpatterns = [
    path('panel-interno-mux/', admin.site.urls),  # Admin Django: solo is_superuser
    path('health/', health_check_view),
    path('404/', preview_404_view),
    path('', home_view, name='home'),
    path('information/', information_view, name='information'),
    path('contacto/', contact_view, name='contact'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    # API JWT (para login.js)
    path('api/accounts/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/accounts/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/accounts/profile/', ProfileAPIView.as_view(), name='api_profile'),
    path('api/accounts/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/accounts/sync-session/', SyncSessionAPIView.as_view(), name='api_sync_session'),
    # URLs amigables (compatibilidad con frontend)
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='login_redirect'),
    path('autenticado/perfil/', RedirectView.as_view(url='/accounts/perfil/', permanent=False), name='perfil_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'muxdry.views.custom_404_view'

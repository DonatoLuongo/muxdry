from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Vistas HTML
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.edit_profile_view, name='edit_profile'),
    path('perfil/cambiar-password/', views.change_password_view, name='change_password'),
    path('perfil/conceder-admin/', views.grant_staff_view, name='grant_staff'),
]

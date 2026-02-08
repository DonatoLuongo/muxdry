from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm

urlpatterns = [
    # Vistas HTML
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/editar/', views.edit_profile_view, name='edit_profile'),
    path('perfil/editar-ubicacion/', views.edit_location_view, name='edit_location'),
    path('perfil/cambiar-password/', views.change_password_view, name='change_password'),
    path('perfil/conceder-admin/', views.grant_staff_view, name='grant_staff'),
    # Restablecer contraseña
    path('restablecer-contraseña/', auth_views.PasswordResetView.as_view(
        form_class=CustomPasswordResetForm,
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset'),
    path('restablecer-contraseña/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('restablecer-contraseña/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete'),
    ), name='password_reset_confirm'),
    path('restablecer-contraseña/completado/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]

from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, logout
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order, Cart


# ============= Vistas HTML (templates) =============

def login_view(request):
    """Renderiza la página de login/registro. El POST real va a la API (rate limited ahí)."""
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'accounts/login.html')


def register_view(request):
    """Redirige al login con formulario de registro activo."""
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login' + '?register=true')


@login_required
def profile_view(request):
    """Perfil del usuario con pedidos y carrito. Filtros historial: period, date, q."""
    from django.utils import timezone
    from datetime import timedelta

    cart, _ = Cart.objects.get_or_create(user=request.user)
    pedidos_actuales = Order.objects.filter(
        user=request.user,
        status__in=['pending', 'confirmed', 'processing', 'shipped']
    ).prefetch_related('items__product').order_by('-created_at')

    historial_pedidos = Order.objects.filter(
        user=request.user,
        status='delivered'
    ).prefetch_related('items__product').order_by('-created_at')

    # Filtros historial
    period = request.GET.get('period')
    date_param = request.GET.get('date')
    q = request.GET.get('q', '').strip()
    if period == '3m':
        since = timezone.now() - timedelta(days=90)
        historial_pedidos = historial_pedidos.filter(created_at__gte=since)
    elif period == 'year':
        since = timezone.now() - timedelta(days=365)
        historial_pedidos = historial_pedidos.filter(created_at__gte=since)
    if date_param:
        historial_pedidos = historial_pedidos.filter(created_at__date=date_param)
    if q:
        historial_pedidos = historial_pedidos.filter(
            models.Q(order_number__icontains=q) | models.Q(notes__icontains=q)
        )
    from django.core.paginator import Paginator
    paginator = Paginator(historial_pedidos, 18)
    page = request.GET.get('page', 1)
    page_obj_historial = paginator.get_page(page)
    historial_pedidos = page_obj_historial.object_list

    user_profile = getattr(request.user, 'profile', None)
    password_cooldown = None
    if user_profile and user_profile.last_password_change:
        from django.utils import timezone
        from datetime import timedelta
        elapsed = timezone.now() - user_profile.last_password_change
        if elapsed < timedelta(hours=48):
            remaining = timedelta(hours=48) - elapsed
            password_cooldown = int(remaining.total_seconds() // 3600)
    context = {
        'user_profile': user_profile,
        'password_cooldown_hours': password_cooldown,
        'pedidos_actuales': pedidos_actuales,
        'historial_pedidos': historial_pedidos,
        'page_obj_historial': page_obj_historial,
        'cart': cart,
        'historial_period': period,
        'historial_date': date_param,
        'historial_q': q,
    }
    return render(request, 'accounts/perfil.html', context)


@login_required
def edit_profile_view(request):
    """Editar perfil: nombre, apellido, email, teléfono (opcional)."""
    from .models import UserProfile
    if request.method == 'POST':
        request.user.first_name = (request.POST.get('first_name') or '').strip()
        request.user.last_name = (request.POST.get('last_name') or '').strip()
        request.user.email = (request.POST.get('email') or '').strip()
        request.user.save()
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = (request.POST.get('phone') or '').strip()
        profile.save()
        messages.success(request, 'Datos actualizados correctamente.')
        return redirect(reverse('profile') + '?tab=settings')
    return redirect(reverse('profile') + '?tab=settings')


@login_required
def grant_staff_view(request):
    """Administradores y Gestor BD: conceder is_staff a un usuario por email."""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect(reverse('profile') + '?tab=settings')
    if request.method != 'POST':
        return redirect(reverse('profile') + '?tab=settings')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    email = (request.POST.get('admin_email') or '').strip()
    email_confirm = (request.POST.get('admin_email_confirm') or '').strip()
    if not email:
        messages.error(request, 'Indica el correo del usuario a promover.')
        return redirect(reverse('profile') + '?tab=settings')
    if email != email_confirm:
        messages.error(request, 'Los correos no coinciden. Verifica e intenta de nuevo.')
        return redirect(reverse('profile') + '?tab=settings')
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, f'No existe ningún usuario con el correo "{email}".')
        return redirect(reverse('profile') + '?tab=settings')
    if user.is_staff:
        messages.info(request, f'"{user.email}" ya es administrador.')
        return redirect(reverse('profile') + '?tab=settings')
    user.is_staff = True
    user.save()
    messages.success(request, f'Se ha concedido acceso de administrador a "{user.email}".')
    return redirect(reverse('profile') + '?tab=settings')


@login_required
def edit_location_view(request):
    """Editar ubicación: capital, ciudad, dirección corta."""
    from .models import UserProfile
    if request.method == 'POST':
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.capital = (request.POST.get('capital') or '').strip()
        profile.city = (request.POST.get('city') or '').strip()
        profile.short_address = (request.POST.get('short_address') or '').strip()
        profile.save()
        messages.success(request, 'Datos de ubicación actualizados correctamente.')
        return redirect(reverse('profile') + '?tab=settings')
    return redirect(reverse('profile') + '?tab=settings')


@login_required
def change_password_view(request):
    """Cambiar contraseña: cooldown 48h entre cambios."""
    from .models import UserProfile
    from django.utils import timezone
    from datetime import timedelta

    _settings_url = reverse('profile') + '?tab=settings'
    if request.method != 'POST':
        return redirect(_settings_url)
    current = request.POST.get('current_password', '')
    new1 = request.POST.get('new_password', '')
    new2 = request.POST.get('new_password_confirm', '')
    if not request.user.check_password(current):
        messages.error(request, 'La contraseña actual no es correcta.')
        return redirect(_settings_url)
    if not new1 or new1 != new2:
        messages.error(request, 'La nueva contraseña no coincide o está vacía.')
        return redirect(_settings_url)
    if len(new1) < 8:
        messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        return redirect(_settings_url)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.last_password_change:
        cooldown = timedelta(hours=48)
        if timezone.now() - profile.last_password_change < cooldown:
            remaining = cooldown - (timezone.now() - profile.last_password_change)
            hours = int(remaining.total_seconds() // 3600)
            messages.error(
                request,
                f'Solo puedes cambiar la contraseña una vez cada 48 horas. '
                f'Vuelve a intentar en {hours} horas.'
            )
            return redirect(_settings_url)
    request.user.set_password(new1)
    request.user.save()
    profile.last_password_change = timezone.now()
    profile.save()
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Contraseña actualizada correctamente. Inicia sesión de nuevo.')
    return redirect(reverse('login') + '?next=/accounts/perfil/?tab=settings')


# ============= API JWT (para login.js) =============

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()


@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST', block=False), name='dispatch')
class RegisterAPIView(generics.CreateAPIView):
    """API: Registro de usuario con JWT. Rate limit: 5/15min por IP."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Demasiados intentos. Espera 15 minutos e intenta de nuevo.'},
                status=429,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST', block=False), name='dispatch')
class LoginAPIView(TokenObtainPairView):
    """API: Login con JWT. Espera email y password. Rate limit: 5/15min por IP."""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Demasiados intentos. Espera 15 minutos e intenta de nuevo.'},
                status=429,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """API: Obtener/actualizar perfil (requiere JWT)."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutAPIView(APIView):
    """API: Cerrar sesión (blacklist refresh token)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                try:
                    token.blacklist()
                except Exception:
                    pass  # Si no hay blacklist, ignorar
            return Response({"message": "Sesión cerrada"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SyncSessionAPIView(APIView):
    """API: Crear sesión Django desde JWT (para que /accounts/perfil/ funcione)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken
        access = request.data.get("access")
        if not access:
            return Response({"error": "Token requerido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = AccessToken(access)
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
            login(request, user)
            return Response({"message": "Sesión creada"})
        except (InvalidToken, User.DoesNotExist) as e:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

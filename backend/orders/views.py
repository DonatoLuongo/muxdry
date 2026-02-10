from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction, models
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Order, OrderItem, Cart, CartItem, OrderMessage
from .serializers import OrderSerializer, CreateOrderSerializer
from products.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    """API para pedidos"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Usuarios solo ven sus propios pedidos, admins ven todos"""
        queryset = Order.objects.filter(user=self.request.user).prefetch_related('items')
        if self.request.user.is_staff:
            queryset = Order.objects.all().prefetch_related('items')
        return queryset
    
    @action(detail=False, methods=['post'], url_path='create-from-cart')
    def create_from_cart(self, request):
        """Crear pedido desde el carrito"""
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response(
                {'error': 'El carrito está vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar stock (asumiendo que Product tiene campo stock)
        for item in cart_items:
            if hasattr(item.product, 'stock') and item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuficiente para {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        with transaction.atomic():
            subtotal = cart.total_price
            shipping = serializer.validated_data.get('shipping', 0)
            tax = serializer.validated_data.get('tax', 0)
            total = subtotal + shipping + tax

            order = Order.objects.create(
                user=request.user,
                status='pending',
                payment_method=serializer.validated_data.get('payment_method', 'transfer'),
                shipping_name=serializer.validated_data.get('shipping_name', ''),
                shipping_address=serializer.validated_data.get('shipping_address', ''),
                shipping_city=serializer.validated_data.get('shipping_city', ''),
                shipping_phone=serializer.validated_data.get('shipping_phone', ''),
                shipping_email=serializer.validated_data.get('shipping_email', request.user.email or ''),
                notes=serializer.validated_data.get('notes', ''),
                subtotal=subtotal,
                shipping=shipping,
                tax=tax,
                total=total,
            )
            
            # Crear items del pedido
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
                # Reducir stock si existe
                if hasattr(cart_item.product, 'stock'):
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
            
            # Vaciar carrito
            cart.items.all().delete()
        
        # Enviar notificación al admin
        try:
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            send_mail(
                subject=f'Nuevo Pedido: {order.order_number}',  # CORREGIDO: era 'numero_pedido'
                message=f'Se ha recibido un nuevo pedido:\n\n'
                       f'Número de Pedido: {order.order_number}\n'
                       f'Usuario: {order.user.email}\n'
                       f'Total: ${float(order.total):.2f}\n'
                       f'Items: {order.items.count()}\n\n'
                       f'Accede al panel de administración para procesarlo.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
        except Exception:
            pass  # No fallar si el email no se puede enviar
        
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='current')
    def current_orders(self, request):
        """Pedidos actuales (pendientes y procesando)"""
        orders = self.get_queryset().filter(
            status__in=['pending', 'processing']  # CORREGIDO: usando strings
        )
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='history')
    def order_history(self, request):
        """Historial de compras (completados)"""
        status_filter = request.query_params.get('status', 'delivered')  # 'delivered' en lugar de 'completado'
        date_filter = request.query_params.get('date', None)
        
        queryset = self.get_queryset().filter(status=status_filter)
        
        if date_filter == '3months':
            from datetime import timedelta
            three_months_ago = timezone.now() - timedelta(days=90)
            queryset = queryset.filter(created_at__gte=three_months_ago)
        elif date_filter:
            # Fecha específica (formato: YYYY-MM-DD)
            queryset = queryset.filter(created_at__date=date_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='details')
    def order_details(self, request, pk=None):
        """Detalles de un pedido específico"""
        order = self.get_object()
        serializer = self.get_serializer(order)
        return Response(serializer.data)


# --- Vistas HTML (carrito y crear pedido) ---

@login_required
def add_to_cart_view(request):
    """Añade un producto al carrito (POST product_id, opcional quantity). Redirige a 'next' o al carrito."""
    if request.method != 'POST':
        return redirect('orders:cart')
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1) or 1)
    if not product_id or quantity < 1:
        messages.warning(request, 'Cantidad no válida.')
        return redirect(request.META.get('HTTP_REFERER', '/') or 'home')
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()
    messages.success(request, f'"{product.name}" añadido al carrito.')
    next_url = request.POST.get('next', '').strip()
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        sep = '&' if '?' in next_url else '?'
        return redirect(next_url + sep + 'cart_added=1')
    from urllib.parse import urlparse
    referer = request.META.get('HTTP_REFERER') or ''
    parsed = urlparse(referer)
    same_origin = not parsed.netloc or parsed.netloc == request.get_host()
    if same_origin and referer and 'orders/carrito' not in referer and 'products/producto' not in referer:
        path = parsed.path or '/'
        qs = parsed.query
        sep = '&' if qs else '?'
        new_qs = (qs + '&' if qs else '') + 'cart_added=1'
        return redirect(path + '?' + new_qs)
    return redirect(referer or 'home')


def _staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(_staff_required, login_url='/accounts/login/')
def admin_orders_view(request):
    """Panel de solicitudes de pedidos: solo staff. Lista todos los pedidos y permite cambiar estado."""
    from django.core.paginator import Paginator
    from django.utils import timezone
    from datetime import timedelta

    # Actualizar estado si POST
    if request.method == 'POST' and request.POST.get('order_id') and request.POST.get('new_status'):
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        order = Order.objects.filter(pk=order_id).first()
        if order and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'shipped':
                order.shipped_at = order.shipped_at or timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = order.delivered_at or timezone.now()
            order.save()
            messages.success(request, f'Pedido {order.order_number} actualizado a {order.get_status_display()}.')
        qs = request.GET.urlencode()
        return redirect('orders:admin_orders' + ('?' + qs if qs else ''))

    orders_qs = Order.objects.all().select_related('user').prefetch_related('items__product').order_by('-created_at')
    status_filter = request.GET.get('status')
    period = request.GET.get('period')
    q = request.GET.get('q', '').strip()
    if status_filter and status_filter in dict(Order.STATUS_CHOICES):
        orders_qs = orders_qs.filter(status=status_filter)
    if period == '3m':
        since = timezone.now() - timedelta(days=90)
        orders_qs = orders_qs.filter(created_at__gte=since)
    elif period == 'year':
        since = timezone.now() - timedelta(days=365)
        orders_qs = orders_qs.filter(created_at__gte=since)
    if q:
        orders_qs = orders_qs.filter(
            models.Q(order_number__icontains=q) | models.Q(user__email__icontains=q) | models.Q(notes__icontains=q)
        )
    paginator = Paginator(orders_qs, 18)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    orders_list = page_obj.object_list
    order_ids = [o.id for o in orders_list]
    unread_client_counts = dict(
        OrderMessage.objects.filter(
            order_id__in=order_ids,
            is_from_admin=False,
            read_by_admin_at__isnull=True
        ).values('order_id').annotate(c=Count('id')).values_list('order_id', 'c')
    )
    orders_with_unread = [(o, unread_client_counts.get(o.id, 0)) for o in orders_list]
    context = {
        'orders': orders_list,
        'orders_with_unread': orders_with_unread,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'period_filter': period,
        'q_filter': q,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/admin_orders.html', context)


@login_required
def current_orders_view(request):
    """Página HTML con pedidos actuales. Filtros: period, date, q. Paginación por 10."""
    from django.core.paginator import Paginator
    from django.utils import timezone
    from datetime import timedelta

    pedidos_qs = Order.objects.filter(
        user=request.user,
        status__in=['pending', 'confirmed', 'processing', 'shipped']
    ).prefetch_related('items__product').order_by('-created_at')

    # Filtros
    period = request.GET.get('period')
    date_param = request.GET.get('date')
    q = request.GET.get('q', '').strip()
    if period == '3m':
        since = timezone.now() - timedelta(days=90)
        pedidos_qs = pedidos_qs.filter(created_at__gte=since)
    elif period == 'year':
        since = timezone.now() - timedelta(days=365)
        pedidos_qs = pedidos_qs.filter(created_at__gte=since)
    if date_param:
        pedidos_qs = pedidos_qs.filter(created_at__date=date_param)
    if q:
        pedidos_qs = pedidos_qs.filter(
            models.Q(order_number__icontains=q) | models.Q(notes__icontains=q)
        )

    paginator = Paginator(pedidos_qs, 18)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    pedidos = page_obj.object_list

    from django.db.models import Count
    order_ids = [p.id for p in pedidos]
    unread_counts = dict(
        OrderMessage.objects.filter(order_id__in=order_ids, is_from_admin=True, read_at__isnull=True)
        .values('order_id').annotate(c=Count('id')).values_list('order_id', 'c')
    )
    pedidos_with_unread = [(p, unread_counts.get(p.id, 0)) for p in pedidos]

    context = {
        'pedidos': pedidos,
        'pedidos_with_unread': pedidos_with_unread,
        'page_obj': page_obj,
        'filtro_period': period,
        'filtro_date': date_param,
        'filtro_q': q,
    }
    return render(request, 'orders/current_orders.html', context)


@login_required
def cancel_order_view(request):
    """Cancela un pedido (usuario ya no interesado). POST order_id. Notifica al admin."""
    if request.method != 'POST':
        return redirect('orders:current_orders')
    order_id = request.POST.get('order_id')
    reason = (request.POST.get('reason') or '').strip() or 'Usuario indica que ya no está interesado'
    if not order_id:
        return redirect('orders:current_orders')
    order = Order.objects.filter(pk=order_id, user=request.user).first()
    if not order:
        messages.warning(request, 'Pedido no encontrado.')
        return redirect('orders:current_orders')
    if order.status not in ['pending', 'confirmed']:
        messages.warning(request, 'Este pedido no puede cancelarse.')
        return redirect('orders:current_orders')
    order.status = 'cancelled'
    order.notes = (order.notes or '') + f'\n[Cancelado por usuario] {reason}'
    order.save()
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f'Pedido cancelado por usuario: {order.order_number}',
                message=(
                    f'El usuario {request.user.email} ha cancelado el pedido {order.order_number}.\n\n'
                    f'Motivo: {reason}\n\n'
                    'Revisa el panel de administración.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except Exception:
        pass
    messages.success(request, f'Pedido {order.order_number} cancelado. Se ha notificado al administrador.')
    return redirect('orders:current_orders')


@login_required
def cart_view(request):
    """Página HTML del carrito: listar ítems, total y botón Realizar solicitud. Paginación por 10."""
    from django.core.paginator import Paginator
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items_all = cart.items.select_related('product').all()
    paginator = Paginator(items_all, 18)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    items = page_obj.object_list
    # Total usa todos los ítems, no solo la página actual
    total = cart.total_price
    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'page_obj': page_obj,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def remove_cart_item_view(request):
    """Elimina un ítem del carrito. POST item_id (CartItem pk)."""
    if request.method != 'POST':
        return redirect('orders:cart')
    item_id = request.POST.get('item_id')
    if not item_id:
        return redirect('orders:cart')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(pk=item_id).first()
    if item:
        item.delete()
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect(request.META.get('HTTP_REFERER') or 'orders:cart')


@login_required
def update_cart_item_view(request):
    """Actualiza cantidad de un ítem. POST item_id y quantity (o delta +1/-1)."""
    if request.method != 'POST':
        return redirect('orders:cart')
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    delta = request.POST.get('delta')  # +1 o -1
    if not item_id:
        return redirect('orders:cart')
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(pk=item_id).first()
    if not item:
        return redirect('orders:cart')
    if delta:
        try:
            d = int(delta)
            item.quantity = max(1, item.quantity + d)
        except ValueError:
            pass
    elif quantity is not None:
        try:
            q = int(quantity)
            if q < 1:
                item.delete()
                messages.success(request, 'Producto eliminado del carrito.')
                return redirect(request.META.get('HTTP_REFERER') or 'orders:cart')
            item.quantity = q
        except ValueError:
            pass
    item.save()
    messages.success(request, 'Carrito actualizado.')
    return redirect(request.META.get('HTTP_REFERER') or 'orders:cart')


@login_required
def create_order_from_cart_view(request):
    """Crea Order desde el carrito con formulario extendido (datos, pago, envío)."""
    if request.method != 'POST':
        return redirect('orders:cart')
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('product').all()
    if not cart_items.exists():
        messages.warning(request, 'El carrito está vacío.')
        return redirect('orders:cart')

    first_name = (request.POST.get('first_name') or '').strip() or (request.user.first_name or '')
    last_name = (request.POST.get('last_name') or '').strip() or (request.user.last_name or '')
    document = (request.POST.get('document') or '').strip()
    payment_method = request.POST.get('payment_method') or 'transfer'
    shipping_type = request.POST.get('shipping_type') or 'delivery_caracas'
    shipping_agency = (request.POST.get('shipping_agency') or '').strip()
    office_pickup = request.POST.get('office_pickup') == 'on'
    central_address = (request.POST.get('central_address') or '').strip()
    shipping_address = (request.POST.get('shipping_address') or '').strip()
    shipping_city = (request.POST.get('shipping_city') or '').strip()
    shipping_phone = (request.POST.get('shipping_phone') or '').strip()
    notes = (request.POST.get('notes') or '').strip()
    shipping_name = f"{first_name} {last_name}".strip() or request.user.get_full_name() or request.user.username

    subtotal = cart.total_price
    shipping = 0
    tax = 0
    total = subtotal + shipping + tax
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            status='pending',
            payment_method=payment_method,
            document=document,
            shipping_type=shipping_type,
            shipping_agency=shipping_agency or '',
            office_pickup=office_pickup,
            central_address=central_address,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_phone=shipping_phone,
            shipping_email=request.user.email or '',
            notes=notes,
            subtotal=subtotal,
            shipping=shipping,
            tax=tax,
            total=total,
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
        cart.items.all().delete()
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f'Nuevo Pedido: {order.order_number}',
                message=(
                    f'Nuevo pedido recibido.\n\n'
                    f'Número: {order.order_number}\n'
                    f'Usuario: {order.user.email}\n'
                    f'Total: ${float(order.total):.2f}\n'
                    f'Ítems: {order.items.count()}\n\n'
                    'Revisa el panel de administración.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except Exception:
        pass
    messages.success(
        request,
        '¡Solicitud enviada exitosamente! Será atendida lo antes posible. '
        'Puedes ver el progreso en Mis pedidos.'
    )
    return redirect('orders:current_orders')


@login_required
def create_order_single_item_view(request):
    """Crea un pedido solo con el ítem indicado del carrito (comprar solo ese producto). Usa el mismo formulario que create_order_from_cart."""
    if request.method != 'POST':
        return redirect('orders:cart')
    item_id = request.POST.get('item_id')
    if not item_id:
        messages.warning(request, 'No se indicó el producto.')
        return redirect('orders:cart')
    cart = get_object_or_404(Cart, user=request.user)
    item = cart.items.filter(pk=item_id).select_related('product').first()
    if not item:
        messages.warning(request, 'El producto no está en tu carrito.')
        return redirect('orders:cart')
    product_name = item.product.name
    qty = item.quantity
    subtotal = item.total_price
    shipping = 0
    tax = 0
    total = subtotal + shipping + tax

    first_name = (request.POST.get('first_name') or '').strip() or (request.user.first_name or '')
    last_name = (request.POST.get('last_name') or '').strip() or (request.user.last_name or '')
    document = (request.POST.get('document') or '').strip()
    payment_method = request.POST.get('payment_method') or 'transfer'
    shipping_type = request.POST.get('shipping_type') or 'delivery_caracas'
    shipping_agency = (request.POST.get('shipping_agency') or '').strip()
    office_pickup = request.POST.get('office_pickup') == 'on'
    central_address = (request.POST.get('central_address') or '').strip()
    shipping_address = (request.POST.get('shipping_address') or '').strip()
    shipping_city = (request.POST.get('shipping_city') or '').strip()
    shipping_phone = (request.POST.get('shipping_phone') or '').strip()
    notes = (request.POST.get('notes') or '').strip()
    shipping_name = f"{first_name} {last_name}".strip() or request.user.get_full_name() or request.user.username

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            status='pending',
            payment_method=payment_method,
            document=document,
            shipping_type=shipping_type,
            shipping_agency=shipping_agency or '',
            office_pickup=office_pickup,
            central_address=central_address,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_phone=shipping_phone,
            shipping_email=request.user.email or '',
            subtotal=subtotal,
            shipping=shipping,
            tax=tax,
            total=total,
            notes=notes,
        )
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=qty,
            price=item.product.price,
        )
        item.delete()
    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if admin_email:
            send_mail(
                subject=f'Nuevo Pedido (solo producto): {order.order_number}',
                message=(
                    f'Nuevo pedido (solo un producto).\n\n'
                    f'Número: {order.order_number}\n'
                    f'Usuario: {order.user.email}\n'
                    f'Producto: {product_name} x {qty}\n'
                    f'Total: ${float(order.total):.2f}\n\n'
                    'Revisa el panel de administración.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
    except Exception:
        pass
    messages.success(request, f'Pedido {order.order_number} realizado (solo ese producto).')
    return redirect('orders:current_orders')


def _order_detail_data(order):
    """Helper para serializar detalle de pedido incluyendo mensajes."""
    items = [{'name': i.product.name, 'quantity': i.quantity, 'price': str(i.price), 'total': str(i.total)} for i in order.items.all()]
    msgs = []
    for m in order.messages.all().order_by('created_at'):
        d = {'id': m.id, 'message': m.message, 'is_from_admin': m.is_from_admin, 'created_at': m.created_at.strftime('%d/%m/%Y %H:%M')}
        d['image_url'] = m.image.url if m.image else None
        msgs.append(d)
    return {
        'order_number': order.order_number,
        'created_at': order.created_at.strftime('%d/%m/%Y %H:%M'),
        'status': order.get_status_display(),
        'payment_method': order.get_payment_method_display(),
        'document': order.document or '—',
        'shipping_type': dict(Order.SHIPPING_TYPE_CHOICES).get(order.shipping_type, order.shipping_type or '—'),
        'shipping_agency': dict(Order.SHIPPING_AGENCY_CHOICES).get(order.shipping_agency, order.shipping_agency or '—'),
        'office_pickup': order.office_pickup,
        'central_address': order.central_address or '—',
        'shipping_name': order.shipping_name or '—',
        'shipping_address': order.shipping_address or '—',
        'shipping_city': order.shipping_city or '—',
        'shipping_phone': order.shipping_phone or '—',
        'notes': order.notes or '—',
        'total': str(order.total),
        'items': items,
        'messages': msgs,
        'user_email': order.user.email,
        'payment_reference': order.payment_reference or '',
    }


@login_required
def order_detail_json_view(request, order_id):
    """Devuelve detalles del pedido en JSON (para modal Ver mi pedido)."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return JsonResponse(_order_detail_data(order))


@login_required
def order_messages_json_view(request, order_id):
    """Devuelve mensajes del pedido y marca como leídos."""
    from django.utils import timezone
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    msgs = list(order.messages.all().order_by('created_at'))
    msgs_list = []
    for m in msgs:
        d = {
            'id': m.id,
            'message': m.message,
            'is_from_admin': m.is_from_admin,
            'created_at': m.created_at.strftime('%d/%m/%Y %H:%M'),
            'read': m.read_at is not None,
        }
        if m.image:
            d['image_url'] = m.image.url
        else:
            d['image_url'] = None
        msgs_list.append(d)
    order.messages.filter(is_from_admin=True, read_at__isnull=True).update(read_at=timezone.now())
    return JsonResponse({'messages': msgs_list})


@login_required
@user_passes_test(_staff_required, login_url='/accounts/login/')
def admin_order_detail_json_view(request, order_id):
    """Admin: devuelve detalles de cualquier pedido. ?mark_client_read=1 marca mensajes del cliente como leídos."""
    order = get_object_or_404(Order, pk=order_id)
    if request.GET.get('mark_client_read'):
        order.messages.filter(is_from_admin=False, read_by_admin_at__isnull=True).update(read_by_admin_at=timezone.now())
    data = _order_detail_data(order)
    return JsonResponse(data)


@login_required
@user_passes_test(_staff_required, login_url='/accounts/login/')
def admin_send_message_view(request):
    """Admin envía mensaje al cliente. POST order_id, message."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    order_id = request.POST.get('order_id')
    message = (request.POST.get('message') or '').strip()
    if not order_id or not message:
        return JsonResponse({'error': 'order_id y message requeridos'}, status=400)
    order = get_object_or_404(Order, pk=order_id)
    OrderMessage.objects.create(order=order, sender=request.user, message=message, is_from_admin=True)
    return JsonResponse({'ok': True})


@login_required
def client_send_message_view(request, order_id):
    """Cliente responde en el chat del pedido. POST message (opcional), image (opcional). order_id viene de la URL."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    message = (request.POST.get('message') or '').strip()
    image = request.FILES.get('image')
    if not message and not image:
        return JsonResponse({'error': 'Debes incluir un mensaje o una imagen (comprobante de pago)'}, status=400)
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    # Validar imagen: solo PNG o JPG, máximo 10MB
    if image:
        allowed_types = ('image/png', 'image/jpeg', 'image/jpg')
        if image.content_type not in allowed_types:
            return JsonResponse({'error': 'Solo se permiten imágenes PNG o JPG.'}, status=400)
        if image.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'La imagen no debe superar 10 MB.'}, status=400)
    msg_text = message or '(Comprobante de pago adjunto)'
    msg = OrderMessage.objects.create(
        order=order,
        sender=request.user,
        message=msg_text,
        is_from_admin=False,
        image=image,
    )
    data = {'ok': True, 'message_id': msg.id}
    if msg.image:
        data['image_url'] = msg.image.url
    return JsonResponse(data)


def _can_view_invoice(request, order):
    """Solo pedidos entregados; cliente dueño del pedido o staff."""
    if order.status != 'delivered':
        return False
    return order.user_id == request.user.id or request.user.is_staff


@login_required
def invoice_view(request, order_id):
    """Vista de factura (solo pedidos entregados). Cliente o admin."""
    order = get_object_or_404(Order, pk=order_id)
    if not _can_view_invoice(request, order):
        return redirect('orders:current_orders')
    user = order.user
    client_name = user.get_full_name() or user.username or order.shipping_name or 'Cliente'
    client_email = order.shipping_email or user.email or ''
    client_phone = getattr(user.profile, 'phone', None) if hasattr(user, 'profile') else None
    if not client_phone:
        client_phone = order.shipping_phone or ''
    logo_path = static('assets/Logotipos/Logo2.svg')
    logo_url = request.build_absolute_uri(logo_path) if logo_path else ''
    seal_path = static('assets/Logotipos/Logo_MUX_seal.png')
    seal_url = request.build_absolute_uri(seal_path) if seal_path else logo_url
    back_url = request.META.get('HTTP_REFERER') or (request.build_absolute_uri('/orders/mis-pedidos/panel-admin/') if request.user.is_staff else request.build_absolute_uri('/orders/mis-pedidos/'))
    context = {
        'order': order,
        'company_name': getattr(settings, 'COMPANY_NAME', 'MULTIVENTAS XIMAREN C.A.'),
        'company_rif': getattr(settings, 'COMPANY_RIF', 'J-12345678-9'),
        'company_phone': getattr(settings, 'COMPANY_PHONE', '(58) 412-991-4914'),
        'company_email': getattr(settings, 'COMPANY_EMAIL', 'informacion@muxdry.com'),
        'company_address': getattr(settings, 'COMPANY_ADDRESS', 'Caracas, Av. Andrés Bello, Torre Centro Andrés Bello, Piso 15'),
        'client_name': client_name,
        'client_email': client_email,
        'client_phone': client_phone,
        'logo_url': logo_url,
        'seal_url': seal_url,
        'back_url': back_url,
    }
    return render(request, 'orders/invoice.html', context)


@login_required
@user_passes_test(_staff_required, login_url='/accounts/login/')
def admin_set_payment_reference_view(request):
    """Admin: guarda el número de referencia del comprobante en el pedido. POST order_id, payment_reference."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    order_id = request.POST.get('order_id')
    ref = (request.POST.get('payment_reference') or '').strip()
    if not order_id:
        return JsonResponse({'error': 'order_id requerido'}, status=400)
    order = get_object_or_404(Order, pk=order_id)
    order.payment_reference = ref[:120]
    order.save(update_fields=['payment_reference'])
    return JsonResponse({'ok': True, 'payment_reference': order.payment_reference})


@login_required
def unread_count_json_view(request):
    """Devuelve conteo de mensajes no leídos para actualizar badges del header."""
    data = {}
    if request.user.is_staff:
        count = OrderMessage.objects.filter(
            is_from_admin=False,
            read_by_admin_at__isnull=True
        ).count()
        data['admin_unread'] = count
    else:
        count = OrderMessage.objects.filter(
            order__user=request.user,
            is_from_admin=True,
            read_at__isnull=True
        ).count()
        data['client_unread'] = count
    return JsonResponse(data)
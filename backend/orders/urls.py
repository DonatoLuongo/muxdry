from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    OrderViewSet, cart_view, create_order_from_cart_view, create_order_single_item_view,
    add_to_cart_view, current_orders_view, admin_orders_view, remove_cart_item_view,
    update_cart_item_view, cancel_order_view,
    order_detail_json_view, order_messages_json_view, admin_order_detail_json_view, admin_send_message_view,
    client_send_message_view, unread_count_json_view,
)

app_name = 'orders'

router = SimpleRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('mis-pedidos/', current_orders_view, name='current_orders'),
    path('mis-pedidos/panel-admin/', admin_orders_view, name='admin_orders'),
    path('mis-pedidos/cancelar/', cancel_order_view, name='cancel_order'),
    path('carrito/', cart_view, name='cart'),
    path('carrito/agregar/', add_to_cart_view, name='add_to_cart'),
    path('carrito/eliminar/', remove_cart_item_view, name='remove_cart_item'),
    path('carrito/actualizar/', update_cart_item_view, name='update_cart_item'),
    path('carrito/realizar-pedido/', create_order_from_cart_view, name='create_order_from_cart'),
    path('carrito/comprar-solo-item/', create_order_single_item_view, name='create_order_single_item'),
    path('pedido/<int:order_id>/detalle/', order_detail_json_view, name='order_detail_json'),
    path('pedido/<int:order_id>/mensajes/', order_messages_json_view, name='order_messages_json'),
    path('mis-pedidos/panel-admin/pedido/<int:order_id>/detalle/', admin_order_detail_json_view, name='admin_order_detail_json'),
    path('mis-pedidos/panel-admin/enviar-mensaje/', admin_send_message_view, name='admin_send_message'),
    path('pedido/<int:order_id>/responder/', client_send_message_view, name='client_send_message'),
    path('api/unread-count/', unread_count_json_view, name='unread_count_json'),
    path('', include(router.urls)),
]

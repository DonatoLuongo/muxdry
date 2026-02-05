from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('producto/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('categoria/<slug:slug>/', views.category_view, name='category'),
    path('buscar/', views.search_view, name='search'),
    # Rutas nombradas para templates estáticos
    path('barra-am/', views.product_barra_view, name='product_barra'),
    path('xerac-ac/', views.product_xerac_view, name='product_xerac'),
    path('drysol/', views.product_drysol_view, name='product_drysol'),
    path('wash/', views.product_wash_view, name='product_wash'),
    path('desodorante-corporal/', views.product_desodorante_view, name='product_desodorante'),
]
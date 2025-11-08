from django.urls import path
from . import views_cliente

app_name = 'cliente'

urlpatterns = [
    path('dashboard/', views_cliente.dashboard_cliente, name='dashboard'),
    path('checkout/', views_cliente.checkout, name='checkout'),
    path('pedido/<int:pedido_id>/', views_cliente.detalle_pedido_cliente, name='pedido_detalle'),
    path('mis-pedidos/', views_cliente.mis_pedidos, name='mis_pedidos'),
]
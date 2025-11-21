# usuarios/urls_comerciante.py
from django.urls import path
from . import views_comerciante

app_name = 'comerciante'

urlpatterns = [
    path('dashboard/', views_comerciante.dashboard_comerciante, name='dashboard'),
    path('pedidos/', views_comerciante.pedidos_comerciante, name='pedidos'),
    path('pedidos/<int:pedido_id>/', views_comerciante.detalle_pedido_comerciante, name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/actualizar/', views_comerciante.actualizar_estado_pedido, name='actualizar_estado'),
    path('productos/', views_comerciante.productos_comerciante, name='productos'),
    path('clientes/', views_comerciante.clientes_comerciante, name='clientes'),
    path('reportes/', views_comerciante.reportes_comerciante, name='reportes'),
    path('configuracion/', views_comerciante.configuracion_comerciante, name='configuracion'),
]
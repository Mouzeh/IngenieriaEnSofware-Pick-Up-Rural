from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.lista_pedidos, name='lista'),
    path('json/', views.api_pedidos_json_viewer, name='json_viewer'),
    path('crear/', views.crear_pedido, name='crear'),
    path('<int:pk>/', views.detalle_pedido, name='detalle'),
    path('<int:pk>/actualizar/', views.actualizar_estado_pedido, name='actualizar_estado'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]
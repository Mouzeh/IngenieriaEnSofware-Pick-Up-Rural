from django.urls import path
from . import views

urlpatterns = [
    # API endpoints JSON
    path('', views.lista_productos, name='lista_productos'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('<int:pk>/actualizar-stock/', views.actualizar_stock, name='actualizar_stock'),
    
    # Vistas HTML (para el formulario)
    path('formulario/agregar/', views.formulario_agregar_producto, name='formulario_agregar'),
    path('crear/', views.crear_producto, name='crear_producto'),
]
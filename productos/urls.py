# productos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Página catálogo (si se incluye con prefijo /productos/)
    path('', views.lista_productos, name='lista_productos'),
    path('<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('agregar/', views.formulario_agregar_producto, name='formulario_agregar_producto'),
    path('crear/', views.crear_producto_formulario, name='crear_producto_formulario'),

    # Endpoints pensados para API (si se incluye con prefijo /api/productos/)
    path('buscar/', views.buscar_productos, name='buscar_productos'),
]

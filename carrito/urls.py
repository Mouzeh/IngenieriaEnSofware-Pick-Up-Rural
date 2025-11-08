from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('agregar/', views.agregar_al_carrito, name='agregar'),
    path('actualizar/', views.actualizar_cantidad, name='actualizar'),
    path('eliminar/', views.eliminar_del_carrito, name='eliminar'),
    path('ver/', views.ver_carrito, name='ver'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    path('finalizar/', views.finalizar_compra, name='finalizar'),
]
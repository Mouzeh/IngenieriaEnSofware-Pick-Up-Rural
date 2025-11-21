from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/negocios/', views.listar_negocios, name='listar_negocios'),
    path('api/negocios/crear/', views.crear_negocio, name='crear_negocio'),
    path('api/negocios/<int:negocio_id>/estado/', views.cambiar_estado_negocio, name='cambiar_estado'),
    path('api/negocios/<int:negocio_id>/eliminar/', views.eliminar_negocio, name='eliminar_negocio'),
]
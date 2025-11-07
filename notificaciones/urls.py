from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('<int:pk>/leer/', views.marcar_leida, name='marcar_leida'),
    path('no-leidas/', views.notificaciones_no_leidas, name='no_leidas'),
]
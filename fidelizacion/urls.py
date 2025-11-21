# fidelizacion/urls.py
from django.urls import path
from . import views

app_name = 'fidelizacion'

urlpatterns = [
    path('dashboard/', views.dashboard_fidelidad, name='dashboard_fidelidad'),
    path('premios/canjear/<int:premio_id>/', views.canjear_puntos, name='canjear_puntos'),
]
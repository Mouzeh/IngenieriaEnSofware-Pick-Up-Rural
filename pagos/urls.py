from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('crear/', views.crear_pago, name='crear'),
    path('<int:pk>/verificar/', views.verificar_pago, name='verificar'),
    path('webpay/iniciar/', views.iniciar_webpay, name='iniciar_webpay'),
    path('webpay/retorno/', views.retorno_webpay, name='retorno_webpay'),
]
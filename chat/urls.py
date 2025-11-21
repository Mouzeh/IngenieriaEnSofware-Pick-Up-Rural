# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Vista principal del chat
    path('pedido/<int:pedido_id>/', views.chat_pedido, name='chat_pedido'),
    
    # APIs para el chat en tiempo real
    path('api/<int:pedido_id>/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('api/<int:pedido_id>/mensajes/', views.obtener_mensajes, name='obtener_mensajes'),
    
    # Lista de chats para comerciante
    path('comerciante/lista/', views.lista_chats_comerciante, name='lista_chats_comerciante'),
]
# chat/admin.py
from django.contrib import admin
from .models import Conversacion, Mensaje

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'fecha_creacion', 'activa', 'total_mensajes']
    list_filter = ['activa', 'fecha_creacion']
    search_fields = ['pedido__numero_pedido', 'pedido__cliente__username']
    
    def total_mensajes(self, obj):
        return obj.mensajes.count()
    total_mensajes.short_description = 'Total Mensajes'

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'conversacion', 'mensaje_preview', 'fecha_envio', 'leido', 'tipo']
    list_filter = ['leido', 'tipo', 'fecha_envio']
    search_fields = ['mensaje', 'usuario__username', 'conversacion__pedido__numero_pedido']
    readonly_fields = ['fecha_envio']
    
    def mensaje_preview(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_preview.short_description = 'Mensaje'
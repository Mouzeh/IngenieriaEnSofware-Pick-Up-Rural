from django.contrib import admin
from .models import Pedido, DetallePedido, HistorialEstadoPedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal', 'notas')

class HistorialEstadoPedidoInline(admin.TabularInline):
    model = HistorialEstadoPedido
    extra = 0
    readonly_fields = ('fecha', 'estado_anterior', 'estado_nuevo', 'usuario')
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'cliente', 'negocio', 'estado', 'metodo_entrega', 'total', 'fecha_pedido')
    list_filter = ('estado', 'metodo_entrega', 'negocio', 'fecha_pedido')
    search_fields = ('numero_pedido', 'cliente__username', 'telefono_contacto')
    readonly_fields = ('numero_pedido', 'fecha_pedido', 'subtotal', 'total')
    inlines = [DetallePedidoInline, HistorialEstadoPedidoInline]
    date_hierarchy = 'fecha_pedido'
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'cliente', 'negocio', 'estado', 'fecha_pedido')
        }),
        ('Método de Entrega', {
            'fields': ('metodo_entrega', 'direccion_entrega', 'referencia_direccion', 'telefono_contacto', 'fecha_estimada_retiro')
        }),
        ('Montos', {
            'fields': ('subtotal', 'costo_envio', 'descuento', 'total')
        }),
        ('Notas', {
            'fields': ('notas_cliente', 'notas_internas'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_confirmado', 'marcar_preparando', 'marcar_listo', 'marcar_completado']
    
    def marcar_confirmado(self, request, queryset):
        queryset.update(estado='confirmado')
        self.message_user(request, "Pedidos marcados como confirmados")
    marcar_confirmado.short_description = "Marcar como Confirmado"
    
    def marcar_preparando(self, request, queryset):
        queryset.update(estado='preparando')
        self.message_user(request, "Pedidos marcados como en preparación")
    marcar_preparando.short_description = "Marcar como Preparando"
    
    def marcar_listo(self, request, queryset):
        queryset.update(estado='listo')
        self.message_user(request, "Pedidos marcados como listos")
    marcar_listo.short_description = "Marcar como Listo"
    
    def marcar_completado(self, request, queryset):
        from django.utils import timezone
        queryset.update(estado='completado', fecha_completado=timezone.now())
        self.message_user(request, "Pedidos marcados como completados")
    marcar_completado.short_description = "Marcar como Completado"

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__estado',)
    search_fields = ('pedido__numero_pedido', 'producto__nombre')
    readonly_fields = ('subtotal',)
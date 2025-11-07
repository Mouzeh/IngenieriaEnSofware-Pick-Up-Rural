# notificaciones/admin.py
from django.contrib import admin
from notificaciones.models import Notificacion, ConfiguracionNotificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username', 'titulo', 'mensaje')
    readonly_fields = ('fecha_creacion', 'fecha_lectura')
    date_hierarchy = 'fecha_creacion'
    
    actions = ['marcar_como_leida']
    
    def marcar_como_leida(self, request, queryset):
        for notif in queryset:
            notif.marcar_como_leida()
        self.message_user(request, f"{queryset.count()} notificaciones marcadas como leídas")
    marcar_como_leida.short_description = "Marcar como leída"

@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'notif_email', 'notif_push', 'notif_pedido_nuevo')
    list_filter = ('notif_email', 'notif_push')
    search_fields = ('usuario__username',)


# pagos/admin.py
from django.contrib import admin
from pagos.models import Pago, HistorialPago

class HistorialPagoInline(admin.TabularInline):
    model = HistorialPago
    extra = 0
    readonly_fields = ('fecha', 'estado_anterior', 'estado_nuevo')
    can_delete = False

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('codigo_transaccion', 'pedido', 'metodo_pago', 'estado', 'monto', 'fecha_pago')
    list_filter = ('metodo_pago', 'estado', 'fecha_pago')
    search_fields = ('codigo_transaccion', 'pedido__numero_pedido', 'numero_transferencia')
    readonly_fields = ('codigo_transaccion', 'fecha_pago', 'fecha_aprobacion')
    inlines = [HistorialPagoInline]
    date_hierarchy = 'fecha_pago'
    
    fieldsets = (
        ('Información General', {
            'fields': ('codigo_transaccion', 'pedido', 'metodo_pago', 'estado', 'monto')
        }),
        ('WebPay', {
            'fields': ('token_ws', 'orden_compra'),
            'classes': ('collapse',)
        }),
        ('Transferencia', {
            'fields': ('numero_transferencia', 'banco_origen', 'comprobante'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_pago', 'fecha_aprobacion')
        }),
        ('Información Adicional', {
            'fields': ('datos_respuesta', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['aprobar_pagos']
    
    def aprobar_pagos(self, request, queryset):
        for pago in queryset:
            if pago.estado == 'pendiente':
                pago.aprobar_pago()
        self.message_user(request, "Pagos aprobados exitosamente")
    aprobar_pagos.short_description = "Aprobar pagos seleccionados"
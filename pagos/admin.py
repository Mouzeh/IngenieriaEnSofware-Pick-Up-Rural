# pagos/admin.py (archivo separado)
from django.contrib import admin
from django.apps import apps

# Obtener modelos sin import circular
Pago = apps.get_model('pagos', 'Pago')
HistorialPago = apps.get_model('pagos', 'HistorialPago')

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
# notificaciones/admin.py
from django.contrib import admin
from django.apps import apps

# Obtener los modelos sin importar directamente para evitar circular imports
Notificacion = apps.get_model('notificaciones', 'Notificacion')
ConfiguracionNotificacion = apps.get_model('notificaciones', 'ConfiguracionNotificacion')

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
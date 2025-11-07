from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Negocio

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'telefono', 'activo', 'fecha_registro')
    list_filter = ('tipo_usuario', 'activo', 'fecha_registro')
    search_fields = ('username', 'email', 'telefono', 'first_name', 'last_name')
    ordering = ('-fecha_registro',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'telefono', 'direccion', 'comuna', 'region', 'foto_perfil', 'activo')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'telefono', 'email')
        }),
    )

@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'telefono', 'activo', 'acepta_pickup', 'acepta_delivery')
    list_filter = ('activo', 'acepta_pickup', 'acepta_delivery', 'fecha_creacion')
    search_fields = ('nombre', 'propietario__username', 'telefono', 'email')
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('propietario', 'nombre', 'descripcion', 'logo')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Horarios', {
            'fields': ('horario_apertura', 'horario_cierre', 'dias_atencion')
        }),
        ('Configuración de Entrega', {
            'fields': ('acepta_pickup', 'acepta_delivery', 'radio_entrega_km', 'costo_delivery')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
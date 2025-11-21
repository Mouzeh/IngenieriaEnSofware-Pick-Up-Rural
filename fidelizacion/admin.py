# fidelizacion/admin.py
from django.contrib import admin
from .models import ProgramaFidelidad, ClienteFidelidad, Premio, CanjePuntos

@admin.register(ProgramaFidelidad)
class ProgramaFidelidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'puntos_por_peso', 'puntos_minimos_canje', 'activo']
    list_filter = ['activo']

@admin.register(ClienteFidelidad)
class ClienteFidelidadAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'programa', 'puntos_acumulados', 'puntos_disponibles', 'nivel']
    list_filter = ['nivel', 'programa']
    search_fields = ['cliente__username', 'cliente__email']

@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'programa', 'puntos_requeridos', 'stock', 'activo']
    list_filter = ['activo', 'programa']
    search_fields = ['nombre', 'descripcion']

@admin.register(CanjePuntos)
class CanjePuntosAdmin(admin.ModelAdmin):
    list_display = ['cliente_fidelidad', 'premio', 'puntos_usados', 'fecha_canje', 'estado']
    list_filter = ['estado', 'fecha_canje']
    readonly_fields = ['fecha_canje']
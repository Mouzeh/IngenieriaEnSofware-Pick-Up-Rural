from django.contrib import admin
from .models import Carrito, ItemCarrito

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ('subtotal', 'fecha_agregado')
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'negocio', 'cantidad_items', 'subtotal', 'activo', 'fecha_actualizacion')
    list_filter = ('activo', 'negocio', 'fecha_creacion')
    search_fields = ('usuario__username', 'negocio__nombre')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'cantidad_items', 'subtotal', 'total')
    inlines = [ItemCarritoInline]
    
    fieldsets = (
        ('Información del Carrito', {
            'fields': ('usuario', 'negocio', 'activo')
        }),
        ('Totales', {
            'fields': ('cantidad_items', 'subtotal', 'total')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_agregado')
    list_filter = ('fecha_agregado',)
    search_fields = ('carrito__usuario__username', 'producto__nombre')
    readonly_fields = ('subtotal', 'fecha_agregado')
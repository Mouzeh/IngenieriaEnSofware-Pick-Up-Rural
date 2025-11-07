from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'negocio', 'categoria', 'precio_actual', 'stock', 'stock_bajo', 'activo')
    list_filter = ('negocio', 'categoria', 'activo', 'destacado', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    inlines = [ImagenProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('negocio', 'categoria', 'codigo', 'nombre', 'descripcion')
        }),
        ('Precios', {
            'fields': ('precio', 'precio_oferta')
        }),
        ('Inventario', {
            'fields': ('stock', 'stock_minimo', 'unidad_medida', 'peso')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Configuración', {
            'fields': ('destacado', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def precio_actual(self, obj):
        return obj.precio_actual
    precio_actual.short_description = 'Precio Actual'
    
    def stock_bajo(self, obj):
        return obj.stock_bajo
    stock_bajo.boolean = True
    stock_bajo.short_description = 'Stock Bajo'
from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'nombre', 'negocio', 'precio_actual', 
        'stock', 'tipo_almacenamiento', 'activo'
    ]
    list_filter = [
        'negocio', 'categoria', 'tipo_almacenamiento', 
        'activo', 'destacado'
    ]
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    # NUEVO: Campos para editar
    fieldsets = (
        ('Información Básica', {
            'fields': ('negocio', 'categoria', 'codigo', 'nombre', 'descripcion')
        }),
        ('Precios y Stock', {
            'fields': ('precio', 'precio_oferta', 'stock', 'stock_minimo')
        }),
        ('Almacenamiento y Perecederos', {
            'fields': (
                'tipo_almacenamiento', 
                'temperatura_ideal', 
                'vida_util_horas',
                'requiere_embalaje_especial'
            )
        }),
        ('Medidas y Presentación', {
            'fields': ('unidad_medida', 'peso', 'imagen', 'destacado')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'orden']
    list_filter = ['producto']
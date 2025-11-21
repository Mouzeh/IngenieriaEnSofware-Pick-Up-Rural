from django.db import models
from usuarios.models import Negocio


# ============================================================
# CATEGORÍA DE PRODUCTOS
# ============================================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Nombre del icono")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ============================================================
# PRODUCTOS
# ============================================================
class Producto(models.Model):

    # Nuevos tipos de almacenamiento
    TIPO_ALMACENAMIENTO_CHOICES = [
        ('ambiente', '🌡️ Temperatura Ambiente'),
        ('refrigerado', '❄️ Refrigerado (2-8°C)'),
        ('congelado', '🧊 Congelado (-18°C)'),
        ('fresco', '🥬 Fresco (caducidad corta)'),
    ]

    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5, help_text="Alerta de stock bajo")

    unidad_medida = models.CharField(max_length=20, default='unidad', help_text="Ej: kg, litros, unidad")
    peso = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Peso en gramos")

    # ========================================================
    # CAMPOS NUEVOS PARA PERECEDEROS
    # ========================================================
    tipo_almacenamiento = models.CharField(
        max_length=20,
        choices=TIPO_ALMACENAMIENTO_CHOICES,
        default='ambiente',
        verbose_name='Requisito de Almacenamiento'
    )

    temperatura_ideal = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Temperatura Ideal (°C)'
    )

    vida_util_horas = models.IntegerField(
        null=True,
        blank=True,
        help_text="Vida útil en horas desde la preparación"
    )

    requiere_embalaje_especial = models.BooleanField(
        default=False,
        help_text="Requiere hielo o embalaje especial"
    )

    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['negocio', 'activo']),
            models.Index(fields=['tipo_almacenamiento']),  # índice útil para reportes
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    # ========================================================
    # PROPIEDADES CALCULADAS
    # ========================================================
    @property
    def precio_actual(self):
        """Retorna el precio final según si hay oferta o no."""
        return self.precio_oferta if self.precio_oferta else self.precio
    
    @property
    def hay_stock(self):
        return self.stock > 0
    
    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo

    # ========================================================
    # PROPIEDADES PARA TEMPLATES (NO usar en queries!)
    # ========================================================
    @property
    def es_perecedero(self):
        """Indica si el producto requiere condiciones especiales de conservación."""
        return self.tipo_almacenamiento != 'ambiente'
    
    @property
    def requiere_refrigeracion(self):
        """Si necesita frío para su conservación."""
        return self.tipo_almacenamiento in ['refrigerado', 'congelado']
    
    @property
    def es_prioritario(self):
        """Productos que deben prepararse primero."""
        return self.tipo_almacenamiento in ['fresco', 'refrigerado']


# ============================================================
# GALERÍA DE IMÁGENES DE PRODUCTOS
# ============================================================
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_adicionales')
    imagen = models.ImageField(upload_to='productos/galeria/')
    descripcion = models.CharField(max_length=200, blank=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['orden']
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"

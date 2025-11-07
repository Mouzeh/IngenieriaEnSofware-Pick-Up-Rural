from django.db import models
from django.core.validators import MinValueValidator
from usuarios.models import Usuario, Negocio
from productos.models import Producto
import uuid

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo para Retirar/Entregar'),
        ('en_camino', 'En Camino'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_ENTREGA = [
        ('pickup', 'Retiro en Tienda'),
        ('delivery', 'Entrega a Domicilio'),
    ]
    
    numero_pedido = models.CharField(max_length=20, unique=True, editable=False)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='pedidos')
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_entrega = models.CharField(max_length=10, choices=METODO_ENTREGA)
    
    # Información de entrega
    direccion_entrega = models.TextField(blank=True)
    referencia_direccion = models.TextField(blank=True)
    telefono_contacto = models.CharField(max_length=15)
    
    # Fechas
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_estimada_retiro = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notas
    notas_cliente = models.TextField(blank=True)
    notas_internas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['numero_pedido']),
            models.Index(fields=['cliente', 'estado']),
            models.Index(fields=['negocio', 'estado']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            self.numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_pedido} - {self.cliente.username}"
    
    def calcular_total(self):
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal + self.costo_envio - self.descuento
        self.save()

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.estado_anterior} → {self.estado_nuevo}"
from django.db import models
from pedidos.models import Pedido
import uuid

class Pago(models.Model):
    METODO_PAGO = [
        ('webpay', 'WebPay'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    ]
    
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    codigo_transaccion = models.CharField(max_length=100, unique=True, editable=False)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO, default='pendiente')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Para WebPay
    token_ws = models.CharField(max_length=100, blank=True)
    orden_compra = models.CharField(max_length=100, blank=True)
    
    # Para transferencias
    numero_transferencia = models.CharField(max_length=100, blank=True)
    comprobante = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    banco_origen = models.CharField(max_length=100, blank=True)
    
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    datos_respuesta = models.JSONField(null=True, blank=True, help_text="Respuesta del gateway de pago")
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']
        indexes = [
            models.Index(fields=['codigo_transaccion']),
            models.Index(fields=['pedido', 'estado']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.codigo_transaccion:
            self.codigo_transaccion = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_transaccion} - {self.pedido.numero_pedido}"
    
    def aprobar_pago(self):
        from django.utils import timezone
        self.estado = 'aprobado'
        self.fecha_aprobacion = timezone.now()
        self.save()
        
        # Actualizar estado del pedido
        self.pedido.estado = 'confirmado'
        self.pedido.save()

class HistorialPago(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Historial de Pago'
        verbose_name_plural = 'Historial de Pagos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.pago.codigo_transaccion} - {self.estado_anterior} → {self.estado_nuevo}"
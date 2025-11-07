from django.db import models
from usuarios.models import Usuario
from pedidos.models import Pedido

class Notificacion(models.Model):
    TIPO_NOTIFICACION = [
        ('pedido_nuevo', 'Nuevo Pedido'),
        ('pedido_confirmado', 'Pedido Confirmado'),
        ('pedido_preparando', 'Pedido en Preparación'),
        ('pedido_listo', 'Pedido Listo'),
        ('pedido_en_camino', 'Pedido en Camino'),
        ('pedido_completado', 'Pedido Completado'),
        ('pedido_cancelado', 'Pedido Cancelado'),
        ('stock_bajo', 'Stock Bajo'),
        ('sistema', 'Notificación del Sistema'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TIPO_NOTIFICACION)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"
    
    def marcar_como_leida(self):
        if not self.leida:
            from django.utils import timezone
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()

class ConfiguracionNotificacion(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='config_notificaciones')
    notif_pedido_nuevo = models.BooleanField(default=True)
    notif_pedido_confirmado = models.BooleanField(default=True)
    notif_pedido_listo = models.BooleanField(default=True)
    notif_pedido_en_camino = models.BooleanField(default=True)
    notif_pedido_completado = models.BooleanField(default=True)
    notif_promociones = models.BooleanField(default=True)
    notif_email = models.BooleanField(default=True)
    notif_push = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Configuración de Notificación'
        verbose_name_plural = 'Configuraciones de Notificaciones'
    
    def __str__(self):
        return f"Config de {self.usuario.username}"
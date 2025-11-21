# chat/models.py
from django.db import models
from usuarios.models import Usuario
from pedidos.models import Pedido

class Conversacion(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='conversacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Chat - {self.pedido.numero_pedido}"

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, default='texto', choices=[
        ('texto', 'Texto'),
        ('sistema', 'Sistema'),
        ('imagen', 'Imagen')
    ])
    
    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['fecha_envio']
    
    def __str__(self):
        return f"{self.usuario.username}: {self.mensaje[:50]}..."
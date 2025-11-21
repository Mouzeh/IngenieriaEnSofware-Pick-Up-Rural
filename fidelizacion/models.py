# fidelizacion/models.py
from django.db import models
from usuarios.models import Usuario
from pedidos.models import Pedido

class ProgramaFidelidad(models.Model):
    nombre = models.CharField(max_length=100, default="Programa Pick Up Rural")
    descripcion = models.TextField(default="Acumula puntos con tus compras y canjéalos por premios")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    puntos_por_peso = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    puntos_minimos_canje = models.IntegerField(default=100)
    
    class Meta:
        verbose_name = 'Programa de Fidelidad'
        verbose_name_plural = 'Programas de Fidelidad'
    
    def __str__(self):
        return self.nombre

class ClienteFidelidad(models.Model):
    cliente = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='fidelidad')
    programa = models.ForeignKey(ProgramaFidelidad, on_delete=models.CASCADE, default=1)
    puntos_acumulados = models.IntegerField(default=0)
    puntos_canjeados = models.IntegerField(default=0)
    nivel = models.CharField(max_length=20, default='bronce', choices=[
        ('bronce', '🥉 Bronce'),
        ('plata', '🥈 Plata'), 
        ('oro', '🥇 Oro'),
        ('diamante', '💎 Diamante')
    ])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente Fidelidad'
        verbose_name_plural = 'Clientes Fidelidad'
    
    def __str__(self):
        return f"{self.cliente.username} - {self.nivel}"
    
    @property
    def puntos_disponibles(self):
        return self.puntos_acumulados - self.puntos_canjeados
    
    def actualizar_nivel(self):
        puntos_totales = self.puntos_acumulados
        
        if puntos_totales >= 5000:
            self.nivel = 'diamante'
        elif puntos_totales >= 2000:
            self.nivel = 'oro'
        elif puntos_totales >= 500:
            self.nivel = 'plata'
        else:
            self.nivel = 'bronce'
        
        self.save()

class Premio(models.Model):
    programa = models.ForeignKey(ProgramaFidelidad, on_delete=models.CASCADE, related_name='premios', default=1)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    puntos_requeridos = models.IntegerField()
    stock = models.IntegerField(default=-1)  # -1 para ilimitado
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='premios/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Premio'
        verbose_name_plural = 'Premios'
        ordering = ['puntos_requeridos']
    
    def __str__(self):
        return f"{self.nombre} ({self.puntos_requeridos} pts)"

class CanjePuntos(models.Model):
    cliente_fidelidad = models.ForeignKey(ClienteFidelidad, on_delete=models.CASCADE, related_name='canjes')
    premio = models.ForeignKey(Premio, on_delete=models.CASCADE)
    puntos_usados = models.IntegerField()
    fecha_canje = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado')
    ])
    
    class Meta:
        verbose_name = 'Canje de Puntos'
        verbose_name_plural = 'Canjes de Puntos'
        ordering = ['-fecha_canje']
    
    def __str__(self):
        return f"Canje {self.cliente_fidelidad.cliente.username} - {self.premio.nombre}"
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('cliente', 'Cliente'),
        ('comerciante', 'Comerciante'),
        ('admin', 'Administrador'),
    ]
    
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_usuario_display()}"

class Negocio(models.Model):
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='negocios')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='negocios/', null=True, blank=True)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    dias_atencion = models.CharField(max_length=100, help_text="Ej: Lunes a Sábado")
    radio_entrega_km = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    costo_delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    acepta_pickup = models.BooleanField(default=True)
    acepta_delivery = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
    
    def __str__(self):
        return self.nombre
from django.db import models
from django.core.validators import MinValueValidator
from usuarios.models import Usuario, Negocio
from productos.models import Producto

class Carrito(models.Model):
    """Carrito de compras de un cliente"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carritos')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='carritos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        unique_together = ['usuario', 'negocio', 'activo']
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"Carrito de {self.usuario.username} - {self.negocio.nombre}"
    
    @property
    def cantidad_items(self):
        """Total de items en el carrito"""
        return self.items.aggregate(total=models.Sum('cantidad'))['total'] or 0
    
    @property
    def subtotal(self):
        """Subtotal del carrito"""
        total = sum(item.subtotal for item in self.items.all())
        return total
    
    @property
    def total(self):
        """Total del carrito (subtotal + envío si aplica)"""
        return self.subtotal
    
    def vaciar(self):
        """Vaciar todos los items del carrito"""
        self.items.all().delete()
    
    def convertir_a_pedido(self, metodo_entrega, direccion_entrega='', telefono_contacto='', notas=''):
        """Convierte el carrito en un pedido real"""
        from pedidos.models import Pedido, DetallePedido
        from django.db import transaction
        
        with transaction.atomic():
            # Crear el pedido
            pedido = Pedido.objects.create(
                cliente=self.usuario,
                negocio=self.negocio,
                estado='pendiente',
                metodo_entrega=metodo_entrega,
                direccion_entrega=direccion_entrega,
                telefono_contacto=telefono_contacto or self.usuario.telefono,
                notas_cliente=notas
            )
            
            # Crear los detalles del pedido
            for item in self.items.all():
                # Verificar stock
                if item.producto.stock < item.cantidad:
                    raise ValueError(f"Stock insuficiente para {item.producto.nombre}")
                
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario
                )
                
                # Reducir stock
                item.producto.stock -= item.cantidad
                item.producto.save()
            
            # Calcular totales del pedido
            pedido.calcular_total()
            
            # Desactivar el carrito
            self.activo = False
            self.save()
            
            return pedido

class ItemCarrito(models.Model):
    """Item individual dentro del carrito"""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ['carrito', 'producto']
        ordering = ['fecha_agregado']
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    @property
    def subtotal(self):
        """Subtotal del item"""
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        # Guardar el precio actual del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_actual
        super().save(*args, **kwargs)
        
        # Actualizar fecha del carrito
        self.carrito.save()
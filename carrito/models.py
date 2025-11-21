from django.db import models
from django.core.validators import MinValueValidator
from usuarios.models import Usuario, Negocio
from productos.models import Producto
from productos.services import ServicioPerecederos, ValidadorPerecederos   # 👈 NUEVO

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
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"Carrito de {self.usuario.username} - {self.negocio.nombre}"
    
    def save(self, *args, **kwargs):
        # Si este carrito está activo, desactivar otros carritos activos del mismo usuario-negocio
        if self.activo and self.pk:
            Carrito.objects.filter(
                usuario=self.usuario, 
                negocio=self.negocio, 
                activo=True
            ).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)
    
    @property
    def cantidad_items(self):
        return self.items.aggregate(total=models.Sum('cantidad'))['total'] or 0
    
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total(self):
        return self.subtotal
    
    def vaciar(self):
        self.items.all().delete()

    # 📌 NUEVA VERSIÓN COMPLETA DEL MÉTODO
    def convertir_a_pedido(self, metodo_entrega, direccion_entrega='', telefono_contacto='', notas=''):
        """Convierte el carrito en un pedido real con validación de perecederos"""
        from pedidos.models import Pedido, DetallePedido
        from django.db import transaction
        
        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                cliente=self.usuario,
                negocio=self.negocio,
                estado='pendiente',
                metodo_entrega=metodo_entrega,
                direccion_entrega=direccion_entrega,
                telefono_contacto=telefono_contacto or self.usuario.telefono,
                notas_cliente=notas
            )
            
            # Crear detalles del pedido
            for item in self.items.all():
                if item.producto.stock < item.cantidad:
                    raise ValueError(f"Stock insuficiente para {item.producto.nombre}")
                
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario
                )
                
                # Actualizar stock
                item.producto.stock -= item.cantidad
                item.producto.save()
            
            # 🔥 NUEVO: Validación de productos perecederos
            productos_perecederos = ServicioPerecederos.verificar_condiciones_pedido(pedido)
            
            if productos_perecederos:
                notas_perecederos = "⚠️ PRODUCTOS PERECEDEROS: "
                for prod in productos_perecederos:
                    notas_perecederos += f"{prod['producto']} ({prod['tipo_almacenamiento']}), "
                
                pedido.notas_internas = notas_perecederos.rstrip(', ')
                pedido.save()

                # 🔥 Priorizar pedido si requiere frío
                if any(prod['tipo_almacenamiento'] in ['Refrigerado', 'Congelado'] for prod in productos_perecederos):
                    # Aquí puedes cambiar estado, encolar, enviar alerta, etc.
                    pass
            
            # Calcular totales
            pedido.calcular_total()
            
            # Finalizar carrito
            self.items.all().delete()
            self.activo = False
            self.save()
            
            return pedido


class ItemCarrito(models.Model):
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
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_actual
        super().save(*args, **kwargs)
        self.carrito.save()

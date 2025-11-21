# fidelizacion/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from pedidos.models import Pedido
from .models import ClienteFidelidad, ProgramaFidelidad

@receiver(post_save, sender=Pedido)
def agregar_puntos_por_pedido(sender, instance, created, **kwargs):
    """Agregar puntos cuando un pedido se completa"""
    if instance.estado == 'completado':
        try:
            cliente_fidelidad = ClienteFidelidad.objects.get(cliente=instance.cliente)
            programa = cliente_fidelidad.programa
            
            # 1 punto por cada $100 gastado
            puntos_ganados = int(instance.total / 100 * float(programa.puntos_por_peso))
            
            if puntos_ganados > 0:
                cliente_fidelidad.puntos_acumulados += puntos_ganados
                cliente_fidelidad.actualizar_nivel()
                cliente_fidelidad.save()
                
        except ClienteFidelidad.DoesNotExist:
            # Crear automáticamente el registro de fidelidad si no existe
            programa_default = ProgramaFidelidad.objects.first()
            if not programa_default:
                programa_default = ProgramaFidelidad.objects.create(
                    nombre="Programa Pick Up Rural",
                    descripcion="Acumula puntos con tus compras y canjéalos por premios exclusivos",
                    puntos_por_peso=1.0,
                    puntos_minimos_canje=100
                )
            
            puntos_ganados = int(instance.total / 100 * float(programa_default.puntos_por_peso))
            
            ClienteFidelidad.objects.create(
                cliente=instance.cliente,
                programa=programa_default,
                puntos_acumulados=puntos_ganados
            )
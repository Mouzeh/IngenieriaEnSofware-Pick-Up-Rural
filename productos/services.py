from django.db import models
from django.utils import timezone
from django.db.models import Q
from .models import Producto
from pedidos.models import Pedido

class ServicioPerecederos:
    """Servicio para gestionar productos perecederos"""
    
    @staticmethod
    def obtener_pedidos_prioritarios(negocio=None):
        """Obtiene pedidos que contienen productos perecederos"""
        # CORREGIDO: Usar el campo real en lugar de la propiedad
        queryset = Pedido.objects.filter(
            estado__in=['pendiente', 'confirmado', 'preparando'],
            items__producto__tipo_almacenamiento__in=['refrigerado', 'congelado', 'fresco']
        ).distinct()
        
        if negocio:
            queryset = queryset.filter(negocio=negocio)
            
        return queryset.order_by('-fecha_pedido')
    
    @staticmethod
    def verificar_condiciones_pedido(pedido):
        """Verifica si un pedido requiere manejo especial"""
        productos_especiales = []
        
        for item in pedido.items.all():
            producto = item.producto
            # CORREGIDO: Usar el campo real
            if producto.tipo_almacenamiento != 'ambiente':
                productos_especiales.append({
                    'producto': producto.nombre,
                    'tipo_almacenamiento': producto.get_tipo_almacenamiento_display(),
                    'temperatura_ideal': producto.temperatura_ideal,
                    'requiere_embalaje_especial': producto.requiere_embalaje_especial,
                    'es_perecedero': producto.tipo_almacenamiento != 'ambiente',  # Para el template
                    'requiere_refrigeracion': producto.tipo_almacenamiento in ['refrigerado', 'congelado']
                })
        
        return productos_especiales
    
    @staticmethod
    def alertar_productos_refrigerados_pendientes():
        """Obtiene productos refrigerados en pedidos pendientes"""
        from django.db.models import Count
        
        # CORREGIDO: Usar campos reales
        pedidos_pendientes = Pedido.objects.filter(
            estado__in=['pendiente', 'confirmado'],
            items__producto__tipo_almacenamiento__in=['refrigerado', 'congelado']
        ).distinct()
        
        alertas = []
        for pedido in pedidos_pendientes:
            productos_refrigerados = pedido.items.filter(
                producto__tipo_almacenamiento__in=['refrigerado', 'congelado']
            )
            
            if productos_refrigerados.exists():
                alertas.append({
                    'pedido': pedido,
                    'productos_refrigerados': list(productos_refrigerados),
                    'tiempo_espera': timezone.now() - pedido.fecha_pedido
                })
        
        return alertas

class ValidadorPerecederos:
    """Valida condiciones para productos perecederos"""
    
    @staticmethod
    def validar_ventana_entrega(pedido):
        """Valida si el pedido está dentro de la ventana de entrega segura"""
        # CORREGIDO: Usar campo real
        productos_frescos = pedido.items.filter(
            producto__tipo_almacenamiento='fresco'
        )
        
        if productos_frescos.exists():
            tiempo_transcurrido = timezone.now() - pedido.fecha_pedido
            # Si han pasado más de 2 horas para productos frescos, es urgente
            return tiempo_transcurrido.total_seconds() < 7200  # 2 horas
        
        return True
    
    @staticmethod
    def recomendar_embalaje(pedido):
        """Recomienda el tipo de embalaje necesario"""
        recomendaciones = {
            'refrigerado': False,
            'congelado': False,
            'hielo_seco': False,
            'aislante': False
        }
        
        for item in pedido.items.all():
            producto = item.producto
            
            # CORREGIDO: Usar campo real
            if producto.tipo_almacenamiento == 'refrigerado':
                recomendaciones['refrigerado'] = True
                recomendaciones['aislante'] = True
            elif producto.tipo_almacenamiento == 'congelado':
                recomendaciones['congelado'] = True
                recomendaciones['hielo_seco'] = True
            elif producto.tipo_almacenamiento == 'fresco':
                recomendaciones['aislante'] = True
        
        return recomendaciones
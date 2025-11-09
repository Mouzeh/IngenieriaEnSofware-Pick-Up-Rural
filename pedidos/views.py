from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Pedido

@require_http_methods(["GET"])
def api_pedidos_json_viewer(request):
    """Vista HTML para visualizar el JSON de pedidos"""
    return render(request, 'api_pedidos_json.html')

@require_http_methods(["GET"])
def lista_pedidos(request):
    """Listar todos los pedidos"""
    # Si es una solicitud AJAX o API, devolver JSON
    if request.headers.get('Accept') == 'application/json' or 'api' in request.path:
        pedidos = Pedido.objects.select_related('cliente', 'negocio').values(
            'id', 'numero_pedido', 'cliente__username', 'negocio__nombre', 
            'estado', 'metodo_entrega', 'total', 'fecha_pedido'
        )
        return JsonResponse({'pedidos': list(pedidos)})
    
    # Si es una solicitud normal, mostrar la página HTML
    return render(request, 'catalogo_pedidos.html')

@require_http_methods(["POST"])
def crear_pedido(request):
    """Crear un nuevo pedido"""
    # TODO: Implementar lógica de creación de pedido
    return JsonResponse({'message': 'Pedido creado'}, status=201)

@require_http_methods(["GET"])
def detalle_pedido(request, pk):
    """Obtener detalle de un pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    data = {
        'id': pedido.id,
        'numero_pedido': pedido.numero_pedido,
        'cliente': pedido.cliente.username,
        'negocio': pedido.negocio.nombre,
        'estado': pedido.estado,
        'metodo_entrega': pedido.metodo_entrega,
        'total': float(pedido.total),
        'fecha_pedido': pedido.fecha_pedido.isoformat(),
    }
    return JsonResponse(data)

@require_http_methods(["PATCH", "POST"])
def actualizar_estado_pedido(request, pk):
    """Actualizar estado de un pedido"""
    try:
        pedido = get_object_or_404(Pedido, pk=pk)
        
        # Verificar permisos (solo el comerciante del negocio puede actualizar)
        if request.user.tipo_usuario == 'comerciante':
            if not hasattr(request.user, 'negocios') or pedido.negocio not in request.user.negocios.all():
                return JsonResponse({'error': 'No tienes permiso para actualizar este pedido'}, status=403)
        
        nuevo_estado = request.POST.get('estado')
        
        if not nuevo_estado:
            return JsonResponse({'error': 'Estado es requerido'}, status=400)
        
        estados_validos = ['pendiente', 'confirmado', 'preparando', 'listo', 'en_camino', 'completado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'error': 'Estado inválido'}, status=400)
        
        # Guardar estado anterior para el historial
        from pedidos.models import HistorialEstadoPedido
        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_anterior=pedido.estado,
            estado_nuevo=nuevo_estado,
            usuario=request.user
        )
        
        # Actualizar estado
        pedido.estado = nuevo_estado
        
        # Si el pedido se completa, actualizar fecha
        if nuevo_estado == 'completado':
            from django.utils import timezone
            pedido.fecha_completado = timezone.now()
        
        pedido.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Estado actualizado correctamente',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def mis_pedidos(request):
    """Listar pedidos del usuario autenticado"""
    try:
        # Filtrar pedidos según el tipo de usuario
        if request.user.tipo_usuario == 'cliente':
            pedidos = Pedido.objects.filter(cliente=request.user).select_related('negocio')
        elif request.user.tipo_usuario == 'comerciante':
            # Obtener pedidos de los negocios del comerciante
            if hasattr(request.user, 'negocios'):
                pedidos = Pedido.objects.filter(negocio__in=request.user.negocios.all()).select_related('cliente', 'negocio')
            else:
                pedidos = Pedido.objects.none()
        else:
            pedidos = Pedido.objects.none()
        
        # Preparar datos para respuesta JSON
        pedidos_data = []
        for pedido in pedidos:
            pedido_data = {
                'id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'estado': pedido.estado,
                'metodo_entrega': pedido.metodo_entrega,
                'total': float(pedido.total),
                'fecha_pedido': pedido.fecha_pedido.isoformat(),
                'fecha_completado': pedido.fecha_completado.isoformat() if pedido.fecha_completado else None,
            }
            
            # Agregar información adicional según el tipo de usuario
            if request.user.tipo_usuario == 'cliente':
                pedido_data['negocio'] = pedido.negocio.nombre
                pedido_data['direccion_negocio'] = pedido.negocio.direccion
            elif request.user.tipo_usuario == 'comerciante':
                pedido_data['cliente'] = pedido.cliente.username
                pedido_data['cliente_email'] = pedido.cliente.email
            
            pedidos_data.append(pedido_data)
        
        return JsonResponse({
            'pedidos': pedidos_data,
            'total': len(pedidos_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
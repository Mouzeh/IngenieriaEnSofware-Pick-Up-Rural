from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
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

@require_http_methods(["PATCH"])
def actualizar_estado_pedido(request, pk):
    """Actualizar estado de un pedido"""
    # TODO: Implementar lógica de actualización
    return JsonResponse({'message': 'Estado actualizado'})

@require_http_methods(["GET"])
def mis_pedidos(request):
    """Listar pedidos del usuario autenticado"""
    # TODO: Implementar con autenticación
    return JsonResponse({'pedidos': []})
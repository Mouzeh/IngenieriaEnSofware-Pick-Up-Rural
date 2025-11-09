from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pedidos.models import Pedido
from productos.models import Producto
from usuarios.models import Negocio

@login_required
def dashboard_comerciante(request):
    """Dashboard principal del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    return render(request, 'comerciante/dashboard.html')

@login_required
def pedidos_comerciante(request):
    """Gestión de pedidos del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    return render(request, 'comerciante/pedidos.html')

@login_required
def productos_comerciante(request):
    """Gestión de productos del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    return render(request, 'comerciante/productos.html')

@login_required
def clientes_comerciante(request):
    """Lista de clientes del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    return render(request, 'comerciante/clientes.html')

@login_required
def reportes_comerciante(request):
    """Reportes y estadísticas del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    return render(request, 'comerciante/reportes.html')

@login_required
def configuracion_comerciante(request):
    """Configuración del negocio"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener o crear negocio del comerciante
    negocio = Negocio.objects.filter(propietario=request.user).first()
    
    return render(request, 'comerciante/configuracion.html', {
        'negocio': negocio
    })

@login_required
def actualizar_estado_pedido(request, pedido_id):
    """Actualizar estado de un pedido"""
    if request.user.tipo_usuario != 'comerciante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener el negocio del comerciante
        negocio = Negocio.objects.filter(propietario=request.user).first()
        if not negocio:
            return JsonResponse({'error': 'No tienes un negocio asociado'}, status=400)
        
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=pedido_id, negocio=negocio)
        
        # Obtener nuevo estado
        nuevo_estado = request.POST.get('estado')
        
        if not nuevo_estado:
            return JsonResponse({'error': 'Estado requerido'}, status=400)
        
        # Validar estado
        estados_validos = ['pendiente', 'confirmado', 'preparando', 'listo', 'en_camino', 'completado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'error': 'Estado inválido'}, status=400)
        
        # Actualizar estado
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        
        # Si se completa, guardar fecha
        if nuevo_estado == 'completado':
            from django.utils import timezone
            pedido.fecha_completado = timezone.now()
        
        pedido.save()
        
        # Crear registro en historial
        from pedidos.models import HistorialEstadoPedido
        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            usuario=request.user,
            comentario=f'Estado actualizado por {request.user.username}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Estado actualizado correctamente',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
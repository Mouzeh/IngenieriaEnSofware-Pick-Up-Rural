# notificaciones/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Notificacion
import json

@login_required
@require_http_methods(["GET"])
def lista_notificaciones(request):
    """Listar todas las notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).select_related('pedido', 'pedido__negocio').order_by('-fecha_creacion')[:20]
    
    data = [{
        'id': n.id,
        'tipo': n.tipo,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'leida': n.leida,
        'fecha_creacion': n.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
        'pedido_id': n.pedido.id if n.pedido else None,
        'pedido_numero': n.pedido.numero_pedido if n.pedido else None,
    } for n in notificaciones]
    
    return JsonResponse({
        'notificaciones': data,
        'count': len(data)
    })

@login_required
@require_http_methods(["POST"])
def marcar_leida(request, pk):
    """Marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.marcar_como_leida()
    
    return JsonResponse({
        'success': True,
        'message': 'Notificación marcada como leída'
    })

@login_required
@require_http_methods(["GET"])
def notificaciones_no_leidas(request):
    """Obtener notificaciones no leídas (para polling)"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).select_related('pedido', 'pedido__negocio').order_by('-fecha_creacion')[:10]
    
    data = [{
        'id': n.id,
        'tipo': n.tipo,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'fecha_creacion': n.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
        'pedido_id': n.pedido.id if n.pedido else None,
        'pedido_numero': n.pedido.numero_pedido if n.pedido else None,
    } for n in notificaciones]
    
    return JsonResponse({
        'notificaciones': data,
        'count': len(data)
    })

@login_required
@require_http_methods(["POST"])
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    count = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)
    
    return JsonResponse({
        'success': True,
        'message': f'{count} notificaciones marcadas como leídas',
        'count': count
    })

@login_required
@require_http_methods(["DELETE"])
def eliminar_notificacion(request, pk):
    """Eliminar una notificación"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Notificación eliminada'
    })
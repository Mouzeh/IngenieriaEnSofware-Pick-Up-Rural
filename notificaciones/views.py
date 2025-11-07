from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notificacion

@require_http_methods(["GET"])
def lista_notificaciones(request):
    """Listar todas las notificaciones del usuario"""
    # TODO: Implementar con autenticación
    return JsonResponse({'notificaciones': []})

@require_http_methods(["POST"])
def marcar_leida(request, pk):
    """Marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, pk=pk)
    notificacion.marcar_como_leida()
    return JsonResponse({'message': 'Notificación marcada como leída'})

@require_http_methods(["GET"])
def notificaciones_no_leidas(request):
    """Obtener notificaciones no leídas"""
    # TODO: Implementar con autenticación
    return JsonResponse({'notificaciones': [], 'count': 0})
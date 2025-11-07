from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Pago

@require_http_methods(["POST"])
def crear_pago(request):
    """Crear un nuevo pago"""
    # TODO: Implementar lógica de creación de pago
    return JsonResponse({'message': 'Pago creado'}, status=201)

@require_http_methods(["GET"])
def verificar_pago(request, pk):
    """Verificar estado de un pago"""
    pago = get_object_or_404(Pago, pk=pk)
    data = {
        'id': pago.id,
        'codigo_transaccion': pago.codigo_transaccion,
        'estado': pago.estado,
        'monto': float(pago.monto),
        'metodo_pago': pago.metodo_pago,
    }
    return JsonResponse(data)

@require_http_methods(["POST"])
def iniciar_webpay(request):
    """Iniciar proceso de pago con WebPay"""
    # TODO: Implementar integración con WebPay
    return JsonResponse({'message': 'WebPay iniciado'})

@require_http_methods(["GET", "POST"])
def retorno_webpay(request):
    """URL de retorno de WebPay"""
    # TODO: Implementar lógica de retorno de WebPay
    return JsonResponse({'message': 'Retorno de WebPay'})
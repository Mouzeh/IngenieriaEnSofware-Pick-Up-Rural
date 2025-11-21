# fidelizacion/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ClienteFidelidad, Premio, CanjePuntos, ProgramaFidelidad
from pedidos.models import Pedido

@login_required
def dashboard_fidelidad(request):
    """Dashboard del cliente con su estado de fidelidad"""
    try:
        cliente_fidelidad = ClienteFidelidad.objects.get(cliente=request.user)
    except ClienteFidelidad.DoesNotExist:
        # Si no existe, crear automáticamente
        programa_default = ProgramaFidelidad.objects.first()
        if not programa_default:
            # Crear programa por defecto si no existe
            programa_default = ProgramaFidelidad.objects.create(
                nombre="Programa Pick Up Rural",
                descripcion="Acumula puntos con tus compras y canjéalos por premios exclusivos",
                puntos_por_peso=1.0,
                puntos_minimos_canje=100
            )
        
        cliente_fidelidad = ClienteFidelidad.objects.create(
            cliente=request.user,
            programa=programa_default,
            puntos_acumulados=0
        )
    
    premios_disponibles = Premio.objects.filter(
        programa=cliente_fidelidad.programa,
        activo=True,
        puntos_requeridos__lte=cliente_fidelidad.puntos_disponibles
    )
    
    canjes_recientes = CanjePuntos.objects.filter(
        cliente_fidelidad=cliente_fidelidad
    ).select_related('premio').order_by('-fecha_canje')[:5]
    
    context = {
        'cliente_fidelidad': cliente_fidelidad,
        'premios_disponibles': premios_disponibles,
        'canjes_recientes': canjes_recientes,
    }
    
    return render(request, 'fidelizacion/dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def canjear_puntos(request, premio_id):
    """Canjear puntos por un premio"""
    premio = get_object_or_404(Premio, id=premio_id, activo=True)
    cliente_fidelidad = get_object_or_404(ClienteFidelidad, cliente=request.user)
    
    # Validaciones
    if cliente_fidelidad.puntos_disponibles < premio.puntos_requeridos:
        return JsonResponse({'error': 'Puntos insuficientes'}, status=400)
    
    if premio.stock == 0:
        return JsonResponse({'error': 'Premio agotado'}, status=400)
    
    # Crear canje
    canje = CanjePuntos.objects.create(
        cliente_fidelidad=cliente_fidelidad,
        premio=premio,
        puntos_usados=premio.puntos_requeridos,
        estado='pendiente'
    )
    
    # Actualizar stock si no es ilimitado
    if premio.stock > 0:
        premio.stock -= 1
        premio.save()
    
    # Actualizar puntos del cliente
    cliente_fidelidad.puntos_canjeados += premio.puntos_requeridos
    cliente_fidelidad.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': f'¡Canje exitoso! Has canjeado {premio.puntos_requeridos} puntos por {premio.nombre}',
        'puntos_restantes': cliente_fidelidad.puntos_disponibles
    })
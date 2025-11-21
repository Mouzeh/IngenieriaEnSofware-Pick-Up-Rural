from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from usuarios.models import Negocio, Usuario

# Servicio para detectar productos perecederos
from productos.services import ServicioPerecederos


# ============================================================
# DASHBOARD COMERCIANTE — COMPLETO Y ACTUALIZADO
# ============================================================
@login_required
def dashboard_comerciante(request):
    """Dashboard principal del comerciante con estadísticas + priorización de perecederos."""
    
    # Asegurarse de que es comerciante
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener negocio o enviar error
    negocio = get_object_or_404(Negocio, propietario=request.user)
    
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Query base de pedidos
    pedidos = Pedido.objects.filter(negocio=negocio)

    # Estadísticas
    stats = {
        'total_pedidos': pedidos.count(),
        'pedidos_pendientes': pedidos.filter(estado__in=[
            'pendiente', 'confirmado', 'preparando'
        ]).count(),
        'pedidos_hoy': pedidos.filter(
            fecha_pedido__date=hoy.date()
        ).count(),
        'ventas_mes': pedidos.filter(
            fecha_pedido__gte=inicio_mes,
            estado__in=['completado', 'listo', 'en_camino']
        ).aggregate(total=Sum('total'))['total'] or 0,
        'total_productos': Producto.objects.filter(
            negocio=negocio, activo=True
        ).count(),
        'productos_stock_bajo': Producto.objects.filter(
            negocio=negocio, stock__lte=10, stock__gt=0
        ).count(),
    }

    # Últimos pedidos
    pedidos_recientes = pedidos.select_related('cliente')\
                               .prefetch_related('items__producto')[:5]

    # Productos con bajo stock
    productos_stock_bajo = Producto.objects.filter(
        negocio=negocio, stock__lte=10, stock__gt=0
    )[:10]

    # =======================================================
    # 🚨 PRIORIDAD PERECEDEROS
    # =======================================================
    servicio_perecederos = ServicioPerecederos()
    pedidos_prioritarios = servicio_perecederos.obtener_pedidos_prioritarios(negocio)

    # Marcar propiedades adicionales para templates
    for pedido in pedidos_prioritarios:
        # ¿Es urgente (más de una hora desde creación)?
        tiempo_transcurrido = timezone.now() - pedido.fecha_pedido
        pedido.es_urgente = tiempo_transcurrido > timedelta(hours=1)

        # Tiene productos perecederos
        pedido.tiene_perecederos = True

    # =======================================================
    # CONTEXTO FINAL
    # =======================================================
    context = {
        'negocio': negocio,
        'stats': stats,
        'pedidos_recientes': pedidos_recientes,
        'productos_stock_bajo': productos_stock_bajo,
        'pedidos_prioritarios': pedidos_prioritarios,  # 🔥 PARA EL DASHBOARD
    }

    return render(request, 'comerciante/dashboard.html', context)


# ============================================================
# VISTA: LISTA DE PEDIDOS DEL COMERCIANTE
# ============================================================
@login_required
def pedidos_comerciante(request):
    """Gestión de pedidos del comerciante con filtro por estado y fecha."""
    
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    negocio = get_object_or_404(Negocio, propietario=request.user)

    estado = request.GET.get('estado', 'all')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    pedidos = Pedido.objects.filter(negocio=negocio)\
                            .select_related('cliente')\
                            .prefetch_related('items__producto')\
                            .order_by('-fecha_pedido')

    if estado != 'all':
        pedidos = pedidos.filter(estado=estado)

    if fecha_desde:
        pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_desde)

    if fecha_hasta:
        pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_hasta)

    stats_estados = {
        'all': Pedido.objects.filter(negocio=negocio).count(),
        'pendiente': Pedido.objects.filter(negocio=negocio, estado='pendiente').count(),
        'confirmado': Pedido.objects.filter(negocio=negocio, estado='confirmado').count(),
        'preparando': Pedido.objects.filter(negocio=negocio, estado='preparando').count(),
        'listo': Pedido.objects.filter(negocio=negocio, estado='listo').count(),
        'en_camino': Pedido.objects.filter(negocio=negocio, estado='en_camino').count(),
        'completado': Pedido.objects.filter(negocio=negocio, estado='completado').count(),
        'cancelado': Pedido.objects.filter(negocio=negocio, estado='cancelado').count(),
    }

    return render(request, 'comerciante/pedidos.html', {
        'negocio': negocio,
        'pedidos': pedidos,
        'stats_estados': stats_estados,
        'filtro_actual': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    })


# ============================================================
# DETALLE DE PEDIDO
# ============================================================
@login_required
def detalle_pedido_comerciante(request, pedido_id):
    """Información completa de un pedido específico."""
    
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    pedido = get_object_or_404(
        Pedido.objects.select_related('cliente', 'negocio')
                      .prefetch_related('items__producto', 'historial'),
        id=pedido_id,
        negocio__propietario=request.user
    )

    return render(request, 'comerciante/detalle_pedido.html', {
        'pedido': pedido,
        'items': pedido.items.all(),
        'historial': pedido.historial.all().order_by('-fecha'),
    })


# ============================================================
# GESTIÓN DE PRODUCTOS DEL COMERCIANTE
# ============================================================
@login_required
def productos_comerciante(request):
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    negocio = get_object_or_404(Negocio, propietario=request.user)
    productos = Producto.objects.filter(negocio=negocio).order_by('-id')

    return render(request, 'comerciante/productos.html', {
        'negocio': negocio,
        'productos': productos,
    })


# ============================================================
# CLIENTES DEL COMERCIANTE
# ============================================================
@login_required
def clientes_comerciante(request):
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    negocio = get_object_or_404(Negocio, propietario=request.user)

    clientes = Usuario.objects.filter(
        pedidos__negocio=negocio,
        tipo_usuario='cliente'
    ).annotate(
        total_pedidos=Count('pedidos'),
        ultimo_pedido=Sum('pedidos__fecha_pedido'),
        total_gastado=Sum('pedidos__total')
    ).distinct().order_by('-ultimo_pedido')

    return render(request, 'comerciante/clientes.html', {
        'negocio': negocio,
        'clientes': clientes,
    })


# ============================================================
# REPORTES DEL COMERCIANTE
# ============================================================
@login_required
def reportes_comerciante(request):
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    negocio = get_object_or_404(Negocio, propietario=request.user)

    hoy = timezone.now()
    ultimos_30 = hoy - timedelta(days=30)

    pedidos_30 = Pedido.objects.filter(
        negocio=negocio,
        fecha_pedido__gte=ultimos_30
    )

    reportes = {
        'ventas_30_dias': pedidos_30.aggregate(total=Sum('total'))['total'] or 0,
        'pedidos_30_dias': pedidos_30.count(),
        'productos_vendidos': DetallePedido.objects.filter(
            pedido__negocio=negocio,
            pedido__fecha_pedido__gte=ultimos_30
        ).aggregate(total=Sum('cantidad'))['total'] or 0,
    }

    return render(request, 'comerciante/reportes.html', {
        'negocio': negocio,
        'reportes': reportes,
    })


# ============================================================
# CONFIGURACIÓN DEL NEGOCIO
# ============================================================
@login_required
def configuracion_comerciante(request):
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')

    negocio, created = Negocio.objects.get_or_create(propietario=request.user)

    if request.method == 'POST':
        negocio.nombre = request.POST.get('nombre', negocio.nombre)
        negocio.descripcion = request.POST.get('descripcion', negocio.descripcion)
        negocio.direccion = request.POST.get('direccion', negocio.direccion)
        negocio.telefono = request.POST.get('telefono', negocio.telefono)
        negocio.email = request.POST.get('email', negocio.email)
        negocio.horario_atencion = request.POST.get('horario_atencion', negocio.horario_atencion)
        negocio.activo = request.POST.get('activo') == 'on'
        negocio.save()
        return redirect('configuracion_comerciante')

    return render(request, 'comerciante/configuracion.html', {
        'negocio': negocio
    })


# ============================================================
# ACTUALIZAR ESTADO (AJAX)
# ============================================================
@login_required
def actualizar_estado_pedido(request, pedido_id):
    if request.user.tipo_usuario != 'comerciante':
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    negocio = get_object_or_404(Negocio, propietario=request.user)
    pedido = get_object_or_404(Pedido, id=pedido_id, negocio=negocio)

    nuevo_estado = request.POST.get('estado')
    if not nuevo_estado:
        return JsonResponse({'error': 'Estado requerido'}, status=400)

    estados_validos = [
        'pendiente', 'confirmado', 'preparando',
        'listo', 'en_camino', 'completado', 'cancelado'
    ]

    if nuevo_estado not in estados_validos:
        return JsonResponse({'error': 'Estado inválido'}, status=400)

    estado_anterior = pedido.estado
    pedido.estado = nuevo_estado

    if nuevo_estado == 'completado':
        pedido.fecha_completado = timezone.now()

    pedido.save()

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
        'nuevo_estado': nuevo_estado,
        'estado_display': pedido.get_estado_display()
    })

# usuarios/views_comerciante.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from usuarios.models import Negocio

@login_required
def dashboard_comerciante(request):
    """Dashboard principal del comerciante con estadísticas"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener el negocio del comerciante
    try:
        negocio = Negocio.objects.get(propietario=request.user)
    except Negocio.DoesNotExist:
        return render(request, 'comerciante/error.html', {
            'mensaje': 'No tienes un negocio registrado. Por favor, configura tu negocio primero.'
        })
    
    # Estadísticas del dashboard
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    pedidos = Pedido.objects.filter(negocio=negocio)
    
    stats = {
        'total_pedidos': pedidos.count(),
        'pedidos_pendientes': pedidos.filter(estado__in=['pendiente', 'confirmado', 'preparando']).count(),
        'pedidos_hoy': pedidos.filter(fecha_pedido__date=hoy.date()).count(),
        'ventas_mes': pedidos.filter(
            fecha_pedido__gte=inicio_mes, 
            estado__in=['completado', 'listo', 'en_camino']
        ).aggregate(total=Sum('total'))['total'] or 0,
        'total_productos': Producto.objects.filter(negocio=negocio, activo=True).count(),
        'productos_stock_bajo': Producto.objects.filter(
            negocio=negocio, 
            stock__lte=10, 
            stock__gt=0
        ).count(),
    }
    
    # Pedidos recientes
    pedidos_recientes = pedidos.select_related('cliente').prefetch_related('items__producto')[:5]
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        negocio=negocio, 
        stock__lte=10, 
        stock__gt=0
    )[:10]
    
    context = {
        'negocio': negocio,
        'stats': stats,
        'pedidos_recientes': pedidos_recientes,
        'productos_stock_bajo': productos_stock_bajo,
    }
    
    return render(request, 'comerciante/dashboard.html', context)

@login_required
def pedidos_comerciante(request):
    """Gestión de pedidos del comerciante con filtros"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener el negocio del comerciante
    try:
        negocio = Negocio.objects.get(propietario=request.user)
    except Negocio.DoesNotExist:
        return render(request, 'comerciante/error.html', {
            'mensaje': 'No tienes un negocio registrado.'
        })
    
    # Filtros
    estado = request.GET.get('estado', 'all')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Base queryset
    pedidos = Pedido.objects.filter(negocio=negocio).select_related(
        'cliente'
    ).prefetch_related(
        'items__producto'
    ).order_by('-fecha_pedido')
    
    # Aplicar filtros
    if estado != 'all':
        pedidos = pedidos.filter(estado=estado)
    
    if fecha_desde:
        pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_desde)
    
    if fecha_hasta:
        pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_hasta)
    
    # Estadísticas por estado
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
    
    context = {
        'negocio': negocio,
        'pedidos': pedidos,
        'stats_estados': stats_estados,
        'filtro_actual': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'comerciante/pedidos.html', context)

@login_required
def detalle_pedido_comerciante(request, pedido_id):
    """Vista detallada de un pedido específico"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener el pedido verificando que pertenezca al negocio del comerciante
    pedido = get_object_or_404(
        Pedido.objects.select_related('cliente', 'negocio').prefetch_related(
            'items__producto',
            'historial'
        ),
        id=pedido_id,
        negocio__propietario=request.user  # ¡IMPORTANTE! Seguridad
    )
    
    # Obtener items del pedido
    items = pedido.items.all().select_related('producto')
    
    # Historial de estados
    historial = pedido.historial.all().order_by('-fecha')
    
    context = {
        'pedido': pedido,
        'items': items,
        'historial': historial,
    }
    
    return render(request, 'comerciante/detalle_pedido.html', context)

@login_required
def productos_comerciante(request):
    """Gestión de productos del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    try:
        negocio = Negocio.objects.get(propietario=request.user)
    except Negocio.DoesNotExist:
        return render(request, 'comerciante/error.html', {
            'mensaje': 'No tienes un negocio registrado.'
        })
    
    productos = Producto.objects.filter(negocio=negocio).order_by('-id')
    
    context = {
        'negocio': negocio,
        'productos': productos,
    }
    
    return render(request, 'comerciante/productos.html', context)

@login_required
def clientes_comerciante(request):
    """Lista de clientes que han comprado en el negocio"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    try:
        negocio = Negocio.objects.get(propietario=request.user)
    except Negocio.DoesNotExist:
        return render(request, 'comerciante/error.html', {
            'mensaje': 'No tienes un negocio registrado.'
        })
    
    # Clientes que han realizado pedidos en este negocio
    from django.db.models import Count, Max
    clientes = Usuario.objects.filter(
        pedidos__negocio=negocio,
        tipo_usuario='cliente'
    ).annotate(
        total_pedidos=Count('pedidos'),
        ultimo_pedido=Max('pedidos__fecha_pedido'),
        total_gastado=Sum('pedidos__total')
    ).distinct().order_by('-ultimo_pedido')
    
    context = {
        'negocio': negocio,
        'clientes': clientes,
    }
    
    return render(request, 'comerciante/clientes.html', context)

@login_required
def reportes_comerciante(request):
    """Reportes y estadísticas del comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    try:
        negocio = Negocio.objects.get(propietario=request.user)
    except Negocio.DoesNotExist:
        return render(request, 'comerciante/error.html', {
            'mensaje': 'No tienes un negocio registrado.'
        })
    
    # Lógica para reportes (puedes expandir esto)
    hoy = timezone.now()
    ultimos_30_dias = hoy - timedelta(days=30)
    
    pedidos_30_dias = Pedido.objects.filter(
        negocio=negocio,
        fecha_pedido__gte=ultimos_30_dias
    )
    
    reportes = {
        'ventas_30_dias': pedidos_30_dias.aggregate(total=Sum('total'))['total'] or 0,
        'pedidos_30_dias': pedidos_30_dias.count(),
        'productos_vendidos': DetallePedido.objects.filter(
            pedido__negocio=negocio,
            pedido__fecha_pedido__gte=ultimos_30_dias
        ).aggregate(total=Sum('cantidad'))['total'] or 0,
    }
    
    context = {
        'negocio': negocio,
        'reportes': reportes,
    }
    
    return render(request, 'comerciante/reportes.html', context)

@login_required
def configuracion_comerciante(request):
    """Configuración del negocio"""
    if request.user.tipo_usuario != 'comerciante':
        return redirect('/cliente/dashboard/')
    
    # Obtener o crear negocio del comerciante
    negocio, created = Negocio.objects.get_or_create(propietario=request.user)
    
    if request.method == 'POST':
        # Actualizar configuración del negocio
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

# Mantén tu función actualizar_estado_pedido existente
@login_required
def actualizar_estado_pedido(request, pedido_id):
    """Actualizar estado de un pedido"""
    if request.user.tipo_usuario != 'comerciante':
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener el negocio del comerciante
        negocio = Negocio.objects.get(propietario=request.user)
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
            'nuevo_estado': nuevo_estado,
            'estado_display': pedido.get_estado_display()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from django.shortcuts import render
from django.http import JsonResponse
from usuarios.models import Usuario, Negocio
from productos.models import Producto, Categoria
from pedidos.models import Pedido
from pagos.models import Pago

def home(request):
    """Página de inicio con estadísticas del sistema"""
    
    # Obtener estadísticas
    stats = {
        'usuarios': Usuario.objects.count(),
        'negocios': Negocio.objects.filter(activo=True).count(),
        'productos': Producto.objects.filter(activo=True).count(),
        'categorias': Categoria.objects.filter(activo=True).count(),
        'pedidos_totales': Pedido.objects.count(),
        'pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
        'pedidos_confirmados': Pedido.objects.filter(estado='confirmado').count(),
        'pedidos_completados': Pedido.objects.filter(estado='completado').count(),
        'pagos_aprobados': Pago.objects.filter(estado='aprobado').count(),
    }
    
    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.select_related('cliente', 'negocio').order_by('-fecha_pedido')[:5]
    
    context = {
        'stats': stats,
        'ultimos_pedidos': ultimos_pedidos,
    }
    
    return render(request, 'home.html', context)

def api_status(request):
    """Endpoint para verificar el estado de la API"""
    return JsonResponse({
        'status': 'online',
        'message': '¡API Pick Up Rural funcionando correctamente!',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'usuarios': '/api/usuarios/',
            'productos': '/api/productos/',
            'pedidos': '/api/pedidos/',
            'notificaciones': '/api/notificaciones/',
            'pagos': '/api/pagos/',
        }
    })
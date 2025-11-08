from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from pedidos.models import Pedido

@login_required
def dashboard_cliente(request):
    """Dashboard principal del cliente"""
    if request.user.tipo_usuario != 'cliente':
        return redirect('/comerciante/dashboard/')
    
    return render(request, 'cliente/dashboard.html')

@login_required
def checkout(request):
    """Página de checkout"""
    if request.user.tipo_usuario != 'cliente':
        return redirect('/comerciante/dashboard/')
    
    negocio_id = request.GET.get('negocio_id')
    if not negocio_id:
        return redirect('/cliente/dashboard/')
    
    return render(request, 'cliente/checkout.html')

@login_required
def detalle_pedido_cliente(request, pedido_id):
    """Ver detalle de un pedido"""
    if request.user.tipo_usuario != 'cliente':
        return redirect('/comerciante/dashboard/')
    
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    return render(request, 'cliente/pedido_detalle.html', {
        'pedido': pedido
    })

@login_required
def mis_pedidos(request):
    """Lista de pedidos del cliente"""
    if request.user.tipo_usuario != 'cliente':
        return redirect('/comerciante/dashboard/')
    
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    
    return render(request, 'cliente/mis_pedidos.html', {
        'pedidos': pedidos
    })
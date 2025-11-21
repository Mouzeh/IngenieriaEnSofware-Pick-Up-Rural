# chat/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Conversacion, Mensaje
from pedidos.models import Pedido

@login_required
def chat_pedido(request, pedido_id):
    """Vista principal del chat para un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos: cliente o comerciante del pedido
    if request.user != pedido.cliente and request.user != pedido.negocio.propietario:
        return render(request, 'chat/error.html', {
            'error': 'No tienes permisos para ver este chat'
        }, status=403)
    
    # Obtener o crear conversación
    conversacion, created = Conversacion.objects.get_or_create(pedido=pedido)
    
    # Marcar mensajes como leídos
    if request.user == pedido.negocio.propietario:
        conversacion.mensajes.filter(leido=False).exclude(usuario=request.user).update(leido=True)
    
    context = {
        'pedido': pedido,
        'conversacion': conversacion,
        'mensajes': conversacion.mensajes.all().select_related('usuario'),
        'es_comerciante': request.user == pedido.negocio.propietario,
    }
    
    return render(request, 'chat/chat_pedido.html', context)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def enviar_mensaje(request, pedido_id):
    """API para enviar mensaje"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar permisos
    if request.user != pedido.cliente and request.user != pedido.negocio.propietario:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    mensaje_texto = request.POST.get('mensaje', '').strip()
    
    if not mensaje_texto:
        return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)
    
    # Obtener conversación
    conversacion, created = Conversacion.objects.get_or_create(pedido=pedido)
    
    # Crear mensaje
    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        usuario=request.user,
        mensaje=mensaje_texto
    )
    
    return JsonResponse({
        'success': True,
        'mensaje': {
            'id': mensaje.id,
            'texto': mensaje.mensaje,
            'fecha': mensaje.fecha_envio.isoformat(),
            'usuario': mensaje.usuario.username,
            'es_mio': True
        }
    })

@login_required
def obtener_mensajes(request, pedido_id):
    """API para obtener mensajes nuevos"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.user != pedido.cliente and request.user != pedido.negocio.propietario:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    ultimo_mensaje_id = request.GET.get('ultimo_id', 0)
    
    try:
        conversacion = Conversacion.objects.get(pedido=pedido)
        mensajes = conversacion.mensajes.filter(id__gt=ultimo_mensaje_id).select_related('usuario')
        
        # Marcar como leídos si es comerciante
        if request.user == pedido.negocio.propietario:
            mensajes.filter(leido=False).exclude(usuario=request.user).update(leido=True)
        
        mensajes_data = []
        for mensaje in mensajes:
            mensajes_data.append({
                'id': mensaje.id,
                'texto': mensaje.mensaje,
                'fecha': mensaje.fecha_envio.isoformat(),
                'usuario': mensaje.usuario.username,
                'es_mio': mensaje.usuario == request.user,
                'leido': mensaje.leido
            })
        
        return JsonResponse({'mensajes': mensajes_data})
    
    except Conversacion.DoesNotExist:
        return JsonResponse({'mensajes': []})

@login_required
def lista_chats_comerciante(request):
    """Lista de chats para el comerciante"""
    if request.user.tipo_usuario != 'comerciante':
        return render(request, 'chat/error.html', {
            'error': 'Solo los comerciantes pueden acceder a esta vista'
        }, status=403)
    
    # Obtener conversaciones de los pedidos del comerciante
    from usuarios.models import Negocio
    try:
        negocio = Negocio.objects.get(propietario=request.user)
        pedidos_con_chat = Pedido.objects.filter(
            negocio=negocio,
            conversacion__isnull=False
        ).select_related('cliente', 'conversacion').prefetch_related('conversacion__mensajes').order_by('-fecha_pedido')
        
        # Contar mensajes no leídos para cada chat
        chats_con_info = []
        for pedido in pedidos_con_chat:
            mensajes_no_leidos = pedido.conversacion.mensajes.filter(leido=False).exclude(usuario=request.user).count()
            ultimo_mensaje = pedido.conversacion.mensajes.last()
            
            chats_con_info.append({
                'pedido': pedido,
                'mensajes_no_leidos': mensajes_no_leidos,
                'ultimo_mensaje': ultimo_mensaje,
                'total_mensajes': pedido.conversacion.mensajes.count()
            })
        
        context = {
            'chats': chats_con_info,
            'negocio': negocio
        }
        
        return render(request, 'chat/lista_chats.html', context)
    
    except Negocio.DoesNotExist:
        return render(request, 'chat/error.html', {
            'error': 'No tienes un negocio registrado'
        }, status=400)
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Carrito, ItemCarrito
from productos.models import Producto
from usuarios.models import Negocio

@login_required
@require_http_methods(["POST"])
def agregar_al_carrito(request):
    """Agregar un producto al carrito"""
    try:
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        negocio_id = request.POST.get('negocio_id')
        
        if not all([producto_id, negocio_id]):
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
        
        producto = get_object_or_404(Producto, id=producto_id, activo=True)
        negocio = get_object_or_404(Negocio, id=negocio_id, activo=True)
        
        # Verificar stock disponible
        if producto.stock < cantidad:
            return JsonResponse({
                'error': f'Stock insuficiente. Solo hay {producto.stock} disponibles'
            }, status=400)
        
        # Obtener o crear carrito activo
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user,
            negocio=negocio,
            activo=True
        )
        
        # Verificar si el producto ya está en el carrito
        item, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad, 'precio_unitario': producto.precio_actual}
        )
        
        if not item_created:
            # Si ya existe, actualizar cantidad
            nueva_cantidad = item.cantidad + cantidad
            if producto.stock < nueva_cantidad:
                return JsonResponse({
                    'error': f'Stock insuficiente. Solo puedes agregar {producto.stock - item.cantidad} más'
                }, status=400)
            item.cantidad = nueva_cantidad
            item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{producto.nombre} agregado al carrito',
            'carrito': {
                'cantidad_items': carrito.cantidad_items,
                'subtotal': float(carrito.subtotal),
                'total': float(carrito.total)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def actualizar_cantidad(request):
    """Actualizar cantidad de un item en el carrito"""
    try:
        item_id = request.POST.get('item_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad < 1:
            return JsonResponse({'error': 'La cantidad debe ser al menos 1'}, status=400)
        
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        
        # Verificar stock
        if item.producto.stock < cantidad:
            return JsonResponse({
                'error': f'Stock insuficiente. Solo hay {item.producto.stock} disponibles'
            }, status=400)
        
        item.cantidad = cantidad
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cantidad actualizada',
            'item': {
                'cantidad': item.cantidad,
                'subtotal': float(item.subtotal)
            },
            'carrito': {
                'cantidad_items': item.carrito.cantidad_items,
                'subtotal': float(item.carrito.subtotal),
                'total': float(item.carrito.total)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def eliminar_del_carrito(request):
    """Eliminar un item del carrito"""
    try:
        item_id = request.POST.get('item_id')
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        
        carrito = item.carrito
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto eliminado del carrito',
            'carrito': {
                'cantidad_items': carrito.cantidad_items,
                'subtotal': float(carrito.subtotal),
                'total': float(carrito.total)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def ver_carrito(request):
    """Ver el carrito del usuario"""
    negocio_id = request.GET.get('negocio_id')
    
    if negocio_id:
        carrito = Carrito.objects.filter(
            usuario=request.user,
            negocio_id=negocio_id,
            activo=True
        ).first()
    else:
        carrito = Carrito.objects.filter(
            usuario=request.user,
            activo=True
        ).first()
    
    if not carrito:
        return JsonResponse({
            'carrito': None,
            'items': [],
            'cantidad_items': 0,
            'subtotal': 0,
            'total': 0
        })
    
    items = []
    for item in carrito.items.select_related('producto', 'producto__categoria'):
        items.append({
            'id': item.id,
            'producto': {
                'id': item.producto.id,
                'codigo': item.producto.codigo,
                'nombre': item.producto.nombre,
                'imagen': item.producto.imagen.url if item.producto.imagen else None,
                'stock': item.producto.stock
            },
            'cantidad': item.cantidad,
            'precio_unitario': float(item.precio_unitario),
            'subtotal': float(item.subtotal),
            'fecha_agregado': item.fecha_agregado.isoformat()
        })
    
    return JsonResponse({
        'carrito': {
            'id': carrito.id,
            'negocio': {
                'id': carrito.negocio.id,
                'nombre': carrito.negocio.nombre
            }
        },
        'items': items,
        'cantidad_items': carrito.cantidad_items,
        'subtotal': float(carrito.subtotal),
        'total': float(carrito.total)
    })

@login_required
@require_http_methods(["POST"])
def vaciar_carrito(request):
    """Vaciar todo el carrito"""
    try:
        negocio_id = request.POST.get('negocio_id')
        carrito = get_object_or_404(
            Carrito,
            usuario=request.user,
            negocio_id=negocio_id,
            activo=True
        )
        
        carrito.vaciar()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito vaciado'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def finalizar_compra(request):
    """Convertir carrito en pedido"""
    try:
        negocio_id = request.POST.get('negocio_id')
        metodo_entrega = request.POST.get('metodo_entrega')
        direccion_entrega = request.POST.get('direccion_entrega', '')
        telefono_contacto = request.POST.get('telefono_contacto', '')
        notas = request.POST.get('notas', '')
        
        if not metodo_entrega or metodo_entrega not in ['pickup', 'delivery']:
            return JsonResponse({'error': 'Método de entrega inválido'}, status=400)
        
        if metodo_entrega == 'delivery' and not direccion_entrega:
            return JsonResponse({'error': 'La dirección es requerida para delivery'}, status=400)
        
        carrito = get_object_or_404(
            Carrito,
            usuario=request.user,
            negocio_id=negocio_id,
            activo=True
        )
        
        if carrito.cantidad_items == 0:
            return JsonResponse({'error': 'El carrito está vacío'}, status=400)
        
        # Convertir carrito a pedido
        pedido = carrito.convertir_a_pedido(
            metodo_entrega=metodo_entrega,
            direccion_entrega=direccion_entrega,
            telefono_contacto=telefono_contacto,
            notas=notas
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'pedido': {
                'id': pedido.id,
                'numero_pedido': pedido.numero_pedido,
                'total': float(pedido.total)
            }
        })
        
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
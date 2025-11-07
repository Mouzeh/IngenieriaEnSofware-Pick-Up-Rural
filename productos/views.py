from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria
from usuarios.models import Negocio
import json

@require_http_methods(["GET"])
def lista_productos(request):
    """Listar todos los productos activos"""
    productos = Producto.objects.filter(activo=True).select_related('categoria', 'negocio').values(
        'id', 'codigo', 'nombre', 'descripcion', 'precio', 'precio_oferta', 
        'stock', 'categoria__nombre', 'negocio__nombre'
    )
    return JsonResponse({'productos': list(productos)})

@require_http_methods(["GET"])
def detalle_producto(request, pk):
    """Obtener detalle de un producto"""
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    data = {
        'id': producto.id,
        'codigo': producto.codigo,
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': float(producto.precio),
        'precio_oferta': float(producto.precio_oferta) if producto.precio_oferta else None,
        'stock': producto.stock,
        'categoria': producto.categoria.nombre if producto.categoria else None,
        'negocio': producto.negocio.nombre,
    }
    return JsonResponse(data)

@require_http_methods(["GET"])
def lista_categorias(request):
    """Listar todas las categorías"""
    categorias = Categoria.objects.filter(activo=True).values('id', 'nombre', 'descripcion')
    return JsonResponse({'categorias': list(categorias)})

@require_http_methods(["GET"])
def productos_por_categoria(request, categoria_id):
    """Listar productos de una categoría específica"""
    productos = Producto.objects.filter(
        categoria_id=categoria_id, 
        activo=True
    ).values('id', 'codigo', 'nombre', 'precio', 'stock')
    return JsonResponse({'productos': list(productos)})

@login_required
def formulario_agregar_producto(request):
    """Renderizar el formulario para agregar productos"""
    try:
        # Obtener negocios y categorías para el formulario
        negocios = Negocio.objects.filter(activo=True)
        categorias = Categoria.objects.filter(activo=True)
        
        context = {
            'negocios': negocios,
            'categorias': categorias,
        }
        return render(request, 'agregar_producto.html', context)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def crear_producto(request):
    """Crear un nuevo producto desde el formulario"""
    try:
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        negocio_id = request.POST.get('negocio')
        categoria_id = request.POST.get('categoria')
        codigo = request.POST.get('codigo')
        precio_oferta = request.POST.get('precio_oferta')
        stock_minimo = request.POST.get('stock_minimo', 5)
        unidad_medida = request.POST.get('unidad_medida', 'unidad')
        peso = request.POST.get('peso')
        destacado = request.POST.get('destacado') == 'on'
        activo = request.POST.get('activo') == 'on'
        
        # Validaciones básicas
        if not all([nombre, precio, stock, negocio_id, categoria_id]):
            return JsonResponse({'error': 'Faltan campos obligatorios'}, status=400)
        
        # Obtener instancias
        negocio = get_object_or_404(Negocio, id=negocio_id)
        categoria = get_object_or_404(Categoria, id=categoria_id)
        
        # Generar código si no se proporciona
        if not codigo:
            from django.utils import timezone
            codigo = f"PROD{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear producto
        producto = Producto.objects.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            precio=float(precio),
            precio_oferta=float(precio_oferta) if precio_oferta else None,
            stock=int(stock),
            stock_minimo=int(stock_minimo),
            unidad_medida=unidad_medida,
            peso=float(peso) if peso else None,
            destacado=destacado,
            activo=activo,
            negocio=negocio,
            categoria=categoria
        )
        
        # Manejar imagen si se subió
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
            producto.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto creado exitosamente',
            'producto_id': producto.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def buscar_productos(request):
    """Buscar productos por nombre o código"""
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            activo=True
        ).filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        ).values('id', 'codigo', 'nombre', 'precio', 'stock')
        return JsonResponse({'productos': list(productos)})
    return JsonResponse({'productos': []})

@login_required
@require_http_methods(["POST"])
def actualizar_stock(request, pk):
    """Actualizar stock de un producto"""
    try:
        producto = get_object_or_404(Producto, pk=pk)
        data = json.loads(request.body)
        nuevo_stock = data.get('stock')
        
        if nuevo_stock is None:
            return JsonResponse({'error': 'Stock es requerido'}, status=400)
        
        producto.stock = int(nuevo_stock)
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Stock actualizado',
            'nuevo_stock': producto.stock
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
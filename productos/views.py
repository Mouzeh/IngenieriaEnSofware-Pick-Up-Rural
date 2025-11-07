# productos/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Producto, Categoria
from usuarios.models import Negocio
import json

@require_http_methods(["GET"])
def lista_productos(request):
    """Listar todos los productos activos.
    - Si la ruta empieza con /api/ o el Accept incluye application/json => devuelve JSON.
    - Si no, renderiza el catálogo HTML.
    """
    accept = request.headers.get('Accept', '')
    is_api = request.path.startswith('/api/') or ('application/json' in accept)

    if is_api:
        productos = Producto.objects.filter(activo=True).select_related('categoria', 'negocio').values(
            'id', 'codigo', 'nombre', 'descripcion', 'precio', 'precio_oferta',
            'stock', 'categoria__nombre', 'negocio__nombre'
        )
        return JsonResponse({'productos': list(productos)})

    # Render catálogo (template)
    return render(request, 'catalogo_productos.html')

@require_http_methods(["GET"])
def buscar_productos(request):
    """
    Buscar productos activos por texto libre (q) en nombre, descripcion, codigo,
    categoría o negocio. Devuelve JSON.
    """
    q = (request.GET.get('q') or '').strip()

    qs = Producto.objects.filter(activo=True).select_related('categoria', 'negocio')
    if q:
        qs = qs.filter(
            Q(nombre__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(codigo__icontains=q) |
            Q(categoria__nombre__icontains=q) |
            Q(negocio__nombre__icontains=q)
        )

    productos = qs.values(
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

@require_http_methods(["GET"])
def formulario_agregar_producto(request):
    """Mostrar formulario para agregar producto"""
    negocios = Negocio.objects.filter(activo=True)
    categorias = Categoria.objects.filter(activo=True)

    context = {
        'negocios': negocios,
        'categorias': categorias
    }
    return render(request, 'agregar_producto.html', context)

@require_http_methods(["POST"])
def crear_producto_formulario(request):
    """Crear producto desde formulario web"""
    try:
        negocio_id = request.POST.get('negocio')
        categoria_id = request.POST.get('categoria')
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio')
        precio_oferta = request.POST.get('precio_oferta')
        stock = request.POST.get('stock')
        stock_minimo = request.POST.get('stock_minimo', 5)
        unidad_medida = request.POST.get('unidad_medida')
        peso = request.POST.get('peso')
        destacado = request.POST.get('destacado') == 'on'
        activo = request.POST.get('activo') == 'on'

        if not all([negocio_id, codigo, nombre, precio, stock]):
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

        if Producto.objects.filter(codigo=codigo).exists():
            return JsonResponse({'error': 'El código ya existe'}, status=400)

        producto = Producto.objects.create(
            negocio_id=negocio_id,
            categoria_id=categoria_id if categoria_id else None,
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            precio_oferta=precio_oferta if precio_oferta else None,
            stock=stock,
            stock_minimo=stock_minimo,
            unidad_medida=unidad_medida,
            peso=peso if peso else None,
            destacado=destacado,
            activo=activo
        )

        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
            producto.save()

        return JsonResponse({
            'success': True,
            'message': 'Producto creado exitosamente',
            'producto_id': producto.id
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

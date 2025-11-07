from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Usuario, Negocio

@require_http_methods(["GET", "POST"])
def registro_usuario(request):
    """Registro de nuevo usuario"""
    if request.method == 'GET':
        return JsonResponse({'message': 'Endpoint de registro de usuario'})
    # TODO: Implementar lógica de registro
    return JsonResponse({'message': 'Usuario registrado'}, status=201)

@require_http_methods(["POST"])
def login_usuario(request):
    """Login de usuario"""
    # TODO: Implementar lógica de login
    return JsonResponse({'message': 'Login endpoint'})

@require_http_methods(["GET"])
def perfil_usuario(request):
    """Obtener perfil de usuario"""
    # TODO: Implementar lógica de perfil
    return JsonResponse({'message': 'Perfil de usuario'})

@require_http_methods(["GET"])
def lista_negocios(request):
    """Listar todos los negocios activos"""
    negocios = Negocio.objects.filter(activo=True).values(
        'id', 'nombre', 'descripcion', 'telefono', 'direccion'
    )
    return JsonResponse({'negocios': list(negocios)})
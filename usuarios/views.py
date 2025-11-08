from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import Usuario, Negocio
import json

@require_http_methods(["GET", "POST"])
def login_usuario(request):
    """Login de usuario"""
    if request.method == 'GET':
        # Si ya está autenticado, redirigir al home
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html')
    
    # POST - Procesar login
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        if not username or not password:
            return JsonResponse({'error': 'Usuario y contraseña son requeridos'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configurar sesión
            if not remember:
                request.session.set_expiry(0)  # Cerrar al cerrar navegador
            
            return JsonResponse({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'redirect': '/',
                'user': {
                    'username': user.username,
                    'tipo': user.tipo_usuario,
                    'nombre': user.get_full_name()
                }
            })
        else:
            return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET", "POST"])
def registro_usuario(request):
    """Registro de nuevo usuario"""
    if request.method == 'GET':
        return render(request, 'registro.html')
    
    # POST - Procesar registro
    try:
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefono = request.POST.get('telefono')
        tipo_usuario = request.POST.get('tipo_usuario', 'cliente')
        
        # Validaciones
        if not all([username, email, password, first_name, last_name]):
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
        
        if Usuario.objects.filter(username=username).exists():
            return JsonResponse({'error': 'El usuario ya existe'}, status=400)
        
        if Usuario.objects.filter(email=email).exists():
            return JsonResponse({'error': 'El email ya está registrado'}, status=400)
        
        if len(password) < 8:
            return JsonResponse({'error': 'La contraseña debe tener al menos 8 caracteres'}, status=400)
        
        # Crear usuario
        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            tipo_usuario=tipo_usuario
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET", "POST"])
@csrf_protect
def logout_usuario(request):
    """Cerrar sesión"""
    if request.method == 'POST':
        # Logout con POST (más seguro)
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente')
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Sesión cerrada', 'redirect': '/logout/confirmacion/'})
        
        return redirect('logout_confirmacion')
    
    else:
        # GET - Mostrar página de confirmación de logout
        if request.user.is_authenticated:
            return render(request, 'logout_confirmacion.html', {'show_logout_button': True})
        else:
            # Si ya está deslogueado, redirigir al login
            return redirect('login')

def logout_confirmacion(request):
    """Página de confirmación después del logout"""
    return render(request, 'logout_confirmacion.html', {'show_logout_button': False})

@require_http_methods(["GET"])
@login_required
def perfil_usuario(request):
    """Obtener perfil de usuario"""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'nombre_completo': user.get_full_name(),
        'tipo_usuario': user.tipo_usuario,
        'telefono': user.telefono,
        'direccion': user.direccion,
        'fecha_registro': user.fecha_registro.isoformat() if user.fecha_registro else None
    }
    return JsonResponse(data)

@require_http_methods(["GET"])
def lista_negocios(request):
    """Listar todos los negocios activos"""
    negocios = Negocio.objects.filter(activo=True).values(
        'id', 'nombre', 'descripcion', 'telefono', 'direccion'
    )
    return JsonResponse({'negocios': list(negocios)})
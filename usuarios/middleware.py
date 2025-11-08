from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedRedirectMiddleware:
    """
    Middleware para redirigir usuarios según su rol después del login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que no necesitan redirección
        exempt_urls = [
            '/login/', '/registro/', '/logout/', '/admin/', 
            '/api/', '/static/', '/media/'
        ]
        
        # Si el usuario está autenticado y está en la página de inicio
        if request.user.is_authenticated and request.path == '/':
            # Redirigir según el tipo de usuario
            if request.user.tipo_usuario == 'cliente':
                return redirect('/cliente/dashboard/')
            elif request.user.tipo_usuario == 'comerciante':
                return redirect('/comerciante/dashboard/')
        
        # Si es cliente intentando acceder a rutas de comerciante
        if request.user.is_authenticated and request.user.tipo_usuario == 'cliente':
            if request.path.startswith('/comerciante/'):
                return redirect('/cliente/dashboard/')
        
        # Si es comerciante intentando acceder a rutas de cliente
        if request.user.is_authenticated and request.user.tipo_usuario == 'comerciante':
            if request.path.startswith('/cliente/'):
                return redirect('/comerciante/dashboard/')
        
        response = self.get_response(request)
        return response
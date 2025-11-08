from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from productos.views import lista_productos
from pedidos.views import lista_pedidos
from usuarios.views import login_usuario, registro_usuario, logout_usuario, logout_confirmacion  # Agregar aquí

urlpatterns = [
    # Página principal y estado API
    path('', views.home, name='home'),
    path('api/', views.api_status, name='api_status'),
    
    # Autenticación personalizada
    path('login/', login_usuario, name='login'),
    path('registro/', registro_usuario, name='registro'),
    path('logout/', logout_usuario, name='logout'),
    path('logout/confirmacion/', logout_confirmacion, name='logout_confirmacion'),  # Cambiar aquí
    
    # URLs de autenticación de Django (backup/alternativa)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Catálogos
    path('productos/', lista_productos, name='catalogo_productos'),
    path('pedidos/', lista_pedidos, name='catalogo_pedidos'),
    
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # APIs de la aplicación
    path('api/usuarios/', include('usuarios.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/pedidos/', include('pedidos.urls')),
    path('api/notificaciones/', include('notificaciones.urls')),
    path('api/pagos/', include('pagos.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar el panel de administración
admin.site.site_header = "Pick Up Rural - Administración"
admin.site.site_title = "Pick Up Rural Admin"
admin.site.index_title = "Panel de Control"
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from productos.views import lista_productos

urlpatterns = [
    # Página principal y estado API
    path('', views.home, name='home'),
    path('api/', views.api_status, name='api_status'),

    # Catálogo de productos
    path('productos/', lista_productos, name='catalogo_productos'),

    # Panel de administración
    path('admin/', admin.site.urls),

    # URLs de autenticación de Django
    path('accounts/', include('django.contrib.auth.urls')),

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

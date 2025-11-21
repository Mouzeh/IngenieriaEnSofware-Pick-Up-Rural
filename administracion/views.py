from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from usuarios.models import Usuario, Negocio
import json

def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_staff or user.is_superuser or user.tipo_usuario == 'admin'

@login_required
@user_passes_test(es_administrador)
def dashboard(request):
    """Vista principal del dashboard de administración"""
    # Obtener estadísticas de comerciantes y negocios
    comerciantes = Usuario.objects.filter(tipo_usuario='comerciante')
    negocios = Negocio.objects.all()
    
    total_negocios = negocios.count()
    negocios_activos = negocios.filter(activo=True).count()
    negocios_pendientes = negocios.filter(activo=False).count()
    
    context = {
        'total_negocios': total_negocios,
        'negocios_activos': negocios_activos,
        'negocios_pendientes': negocios_pendientes,
    }
    
    return render(request, 'administracion/dashboard.html', context)

@login_required
@user_passes_test(es_administrador)
def listar_negocios(request):
    """API para listar todos los negocios con sus propietarios"""
    negocios = Negocio.objects.select_related('propietario').all()
    
    # Convertir a formato compatible con el frontend
    lista_negocios = []
    for negocio in negocios:
        lista_negocios.append({
            'id': negocio.id,
            'user__username': negocio.propietario.username,
            'user__email': negocio.propietario.email,
            'user__first_name': negocio.propietario.first_name,
            'user__last_name': negocio.propietario.last_name,
            'nombre_negocio': negocio.nombre,
            'telefono': negocio.telefono,
            'is_active': negocio.activo,
            'direccion': negocio.direccion,
            'propietario_id': negocio.propietario.id,
        })
    
    return JsonResponse(lista_negocios, safe=False)

@login_required
@user_passes_test(es_administrador)
@require_http_methods(["POST"])
def crear_negocio(request):
    """API para crear un nuevo negocio con su propietario"""
    try:
        data = json.loads(request.body)
        
        # Verificar si el email ya existe
        if Usuario.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'message': 'El email ya está registrado'
            }, status=400)
        
        # Separar nombre completo
        nombre_completo = data['owner'].split()
        first_name = nombre_completo[0] if len(nombre_completo) > 0 else ''
        last_name = ' '.join(nombre_completo[1:]) if len(nombre_completo) > 1 else ''
        
        # Crear usuario comerciante
        usuario = Usuario.objects.create_user(
            username=data['email'].split('@')[0],  # Usar parte antes del @
            email=data['email'],
            password=data['password'],
            first_name=first_name,
            last_name=last_name,
            tipo_usuario='comerciante',
            telefono=data.get('phone', ''),
            direccion=data.get('address', ''),
            activo=True
        )
        
        # Crear negocio asociado
        negocio = Negocio.objects.create(
            propietario=usuario,
            nombre=data.get('name', f"Negocio de {first_name}"),
            descripcion=data.get('description', ''),
            direccion=data.get('address', 'Sin dirección'),
            telefono=data.get('phone', ''),
            email=data['email'],
            horario_apertura='09:00',  # Valores por defecto
            horario_cierre='18:00',
            dias_atencion='Lunes a Sábado',
            activo=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Negocio y usuario creados exitosamente',
            'id': negocio.id,
            'usuario_id': usuario.id
        })
        
    except KeyError as e:
        return JsonResponse({
            'success': False,
            'message': f'Campo requerido faltante: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear negocio: {str(e)}'
        }, status=500)

@login_required
@user_passes_test(es_administrador)
@require_http_methods(["POST"])
def cambiar_estado_negocio(request, negocio_id):
    """Activar/desactivar un negocio"""
    try:
        negocio = get_object_or_404(Negocio, id=negocio_id)
        negocio.activo = not negocio.activo
        negocio.save()
        
        # También cambiar el estado del usuario propietario
        negocio.propietario.activo = negocio.activo
        negocio.propietario.save()
        
        return JsonResponse({
            'success': True,
            'status': 'active' if negocio.activo else 'inactive'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@user_passes_test(es_administrador)
@require_http_methods(["DELETE"])
def eliminar_negocio(request, negocio_id):
    """Eliminar un negocio y opcionalmente su propietario"""
    try:
        negocio = get_object_or_404(Negocio, id=negocio_id)
        propietario = negocio.propietario
        
        # Eliminar el negocio
        negocio.delete()
        
        # Si el propietario no tiene más negocios, se puede eliminar
        if not propietario.negocios.exists():
            propietario.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Negocio eliminado exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
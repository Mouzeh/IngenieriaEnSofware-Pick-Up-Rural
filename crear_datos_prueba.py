"""
Script para crear datos de prueba en la base de datos
Ejecutar con: python crear_datos_prueba.py
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickup_rural.settings')
django.setup()

from datetime import time, datetime, timedelta
from decimal import Decimal
from django.utils import timezone

from usuarios.models import Usuario, Negocio
from productos.models import Categoria, Producto
from pedidos.models import Pedido, DetallePedido
from pagos.models import Pago

def limpiar_datos():
    """Eliminar datos existentes (opcional)"""
    print("\n🗑️  ¿Deseas limpiar los datos existentes? (s/n): ", end="")
    respuesta = input().lower()
    
    if respuesta == 's':
        print("Limpiando datos...")
        Pago.objects.all().delete()
        DetallePedido.objects.all().delete()
        Pedido.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        Negocio.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        print("✅ Datos eliminados")

def crear_datos():
    print("\n" + "="*60)
    print("🚀 CREANDO DATOS DE PRUEBA - PICK UP RURAL")
    print("="*60)
    
    try:
        # 1. Crear usuarios
        print("\n👤 Creando usuarios...")
        
        # Verificar si ya existe el comerciante
        comerciante, created = Usuario.objects.get_or_create(
            username='comerciante1',
            defaults={
                'email': 'comerciante@tienda.cl',
                'tipo_usuario': 'comerciante',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'telefono': '+56912345678',
                'direccion': 'Calle Principal 123',
                'comuna': 'Valdivia',
                'region': 'Los Ríos'
            }
        )
        if created:
            comerciante.set_password('comerciante123')
            comerciante.save()
            print(f"✅ Comerciante creado: {comerciante.username}")
        else:
            print(f"ℹ️  Comerciante ya existe: {comerciante.username}")
        
        # Clientes
        cliente1, created = Usuario.objects.get_or_create(
            username='cliente1',
            defaults={
                'email': 'cliente1@email.cl',
                'tipo_usuario': 'cliente',
                'first_name': 'María',
                'last_name': 'González',
                'telefono': '+56987654321',
                'direccion': 'Av. Los Laureles 456',
                'comuna': 'Valdivia',
                'region': 'Los Ríos'
            }
        )
        if created:
            cliente1.set_password('cliente123')
            cliente1.save()
            print(f"✅ Cliente 1 creado: {cliente1.username}")
        else:
            print(f"ℹ️  Cliente 1 ya existe: {cliente1.username}")
        
        cliente2, created = Usuario.objects.get_or_create(
            username='cliente2',
            defaults={
                'email': 'cliente2@email.cl',
                'tipo_usuario': 'cliente',
                'first_name': 'Pedro',
                'last_name': 'Silva',
                'telefono': '+56956781234'
            }
        )
        if created:
            cliente2.set_password('cliente123')
            cliente2.save()
            print(f"✅ Cliente 2 creado: {cliente2.username}")
        else:
            print(f"ℹ️  Cliente 2 ya existe: {cliente2.username}")
        
        # 2. Crear negocio
        print("\n🏪 Creando negocio...")
        negocio, created = Negocio.objects.get_or_create(
            propietario=comerciante,
            nombre='Almacén Don Juanito',
            defaults={
                'descripcion': 'Almacén de abarrotes en zona rural. Productos frescos y de calidad.',
                'direccion': 'Camino Rural Km 5, Valdivia',
                'telefono': '+56912345678',
                'email': 'almacen@donjuanito.cl',
                'horario_apertura': time(8, 0),
                'horario_cierre': time(20, 0),
                'dias_atencion': 'Lunes a Sábado',
                'radio_entrega_km': Decimal('10.0'),
                'costo_delivery': Decimal('2000'),
                'acepta_pickup': True,
                'acepta_delivery': True,
                'activo': True
            }
        )
        if created:
            print(f"✅ Negocio creado: {negocio.nombre}")
        else:
            print(f"ℹ️  Negocio ya existe: {negocio.nombre}")
        
        # 3. Crear categorías
        print("\n📂 Creando categorías...")
        categorias_data = [
            {'nombre': 'Abarrotes', 'descripcion': 'Productos básicos de almacén', 'icono': '🛒'},
            {'nombre': 'Lácteos', 'descripcion': 'Leche, queso, yogurt', 'icono': '🥛'},
            {'nombre': 'Bebidas', 'descripcion': 'Bebidas y jugos', 'icono': '🥤'},
            {'nombre': 'Panadería', 'descripcion': 'Pan y productos de panadería', 'icono': '🍞'},
            {'nombre': 'Frutas y Verduras', 'descripcion': 'Productos frescos', 'icono': '🥬'},
            {'nombre': 'Carnes y Cecinas', 'descripcion': 'Productos cárnicos', 'icono': '🥩'},
        ]
        
        cats_creadas = []
        for cat_data in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={
                    'descripcion': cat_data['descripcion'],
                    'icono': cat_data['icono']
                }
            )
            cats_creadas.append(cat)
            status = "✅ Creada" if created else "ℹ️  Ya existe"
            print(f"{status}: {cat.nombre}")
        
        # 4. Crear productos
        print("\n📦 Creando productos...")
        productos_data = [
            # Abarrotes
            {'nombre': 'Arroz Grado 1', 'precio': 1500, 'stock': 50, 'unidad': 'kg', 'categoria': 0},
            {'nombre': 'Fideos Carozzi', 'precio': 800, 'stock': 100, 'unidad': 'unidad', 'categoria': 0},
            {'nombre': 'Azúcar Iansa', 'precio': 1200, 'stock': 40, 'unidad': 'kg', 'categoria': 0},
            {'nombre': 'Aceite Vegetal', 'precio': 2500, 'stock': 30, 'unidad': 'litro', 'categoria': 0},
            {'nombre': 'Harina Selecta', 'precio': 1000, 'stock': 60, 'unidad': 'kg', 'categoria': 0},
            
            # Lácteos
            {'nombre': 'Leche Entera 1L', 'precio': 900, 'stock': 45, 'unidad': 'litro', 'categoria': 1},
            {'nombre': 'Queso Mantecoso', 'precio': 3500, 'stock': 20, 'unidad': 'kg', 'categoria': 1},
            {'nombre': 'Yogurt Natural', 'precio': 1200, 'stock': 35, 'unidad': 'unidad', 'categoria': 1},
            
            # Bebidas
            {'nombre': 'Coca Cola 1.5L', 'precio': 1500, 'stock': 80, 'unidad': 'unidad', 'categoria': 2},
            {'nombre': 'Jugo Watts 1L', 'precio': 1100, 'stock': 50, 'unidad': 'unidad', 'categoria': 2},
            {'nombre': 'Agua Mineral 2L', 'precio': 800, 'stock': 100, 'unidad': 'unidad', 'categoria': 2},
            
            # Panadería
            {'nombre': 'Pan Hallulla', 'precio': 100, 'stock': 200, 'unidad': 'unidad', 'categoria': 3},
            {'nombre': 'Pan Marraqueta', 'precio': 100, 'stock': 200, 'unidad': 'unidad', 'categoria': 3},
            
            # Frutas y Verduras
            {'nombre': 'Tomate', 'precio': 1500, 'stock': 25, 'unidad': 'kg', 'categoria': 4},
            {'nombre': 'Lechuga', 'precio': 800, 'stock': 30, 'unidad': 'unidad', 'categoria': 4},
            {'nombre': 'Papa', 'precio': 1200, 'stock': 100, 'unidad': 'kg', 'categoria': 4},
            
            # Carnes
            {'nombre': 'Carne Molida', 'precio': 5500, 'stock': 15, 'unidad': 'kg', 'categoria': 5},
            {'nombre': 'Pollo Entero', 'precio': 3500, 'stock': 20, 'unidad': 'unidad', 'categoria': 5},
        ]
        
        productos_creados = []
        for i, prod_data in enumerate(productos_data, 1):
            categoria_idx = prod_data.pop('categoria')
            unidad = prod_data.pop('unidad')
            codigo = f'PROD{i:03d}'
            
            producto, created = Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'negocio': negocio,
                    'categoria': cats_creadas[categoria_idx],
                    'unidad_medida': unidad,
                    'destacado': (i % 5 == 0),
                    'activo': True,
                    **prod_data
                }
            )
            productos_creados.append(producto)
            status = "✅ Creado" if created else "ℹ️  Ya existe"
            print(f"{status}: {producto.nombre} - Stock: {producto.stock}")
        
        # 5. Crear pedidos de ejemplo
        print("\n📋 Creando pedidos de prueba...")
        
        # Pedido 1 - Pickup
        if not Pedido.objects.filter(cliente=cliente1, estado='confirmado').exists():
            pedido1 = Pedido.objects.create(
                cliente=cliente1,
                negocio=negocio,
                estado='confirmado',
                metodo_entrega='pickup',
                telefono_contacto=cliente1.telefono,
                fecha_estimada_retiro=timezone.now() + timedelta(hours=2),
                notas_cliente='Por favor preparar para las 15:00'
            )
            
            DetallePedido.objects.create(
                pedido=pedido1,
                producto=productos_creados[0],
                cantidad=2,
                precio_unitario=productos_creados[0].precio
            )
            
            DetallePedido.objects.create(
                pedido=pedido1,
                producto=productos_creados[5],
                cantidad=4,
                precio_unitario=productos_creados[5].precio
            )
            
            pedido1.calcular_total()
            print(f"✅ Pedido {pedido1.numero_pedido} creado - Total: ${pedido1.total}")
            
            # Crear pago para pedido1
            Pago.objects.create(
                pedido=pedido1,
                metodo_pago='transferencia',
                estado='aprobado',
                monto=pedido1.total,
                banco_origen='Banco Estado'
            )
            print(f"✅ Pago creado para {pedido1.numero_pedido}")
        else:
            print("ℹ️  Pedido 1 ya existe")
        
        # Pedido 2 - Delivery
        if not Pedido.objects.filter(cliente=cliente2, estado='preparando').exists():
            pedido2 = Pedido.objects.create(
                cliente=cliente2,
                negocio=negocio,
                estado='preparando',
                metodo_entrega='delivery',
                direccion_entrega='Calle Los Robles 789, Valdivia',
                referencia_direccion='Casa blanca con reja verde',
                telefono_contacto=cliente2.telefono,
                costo_envio=negocio.costo_delivery
            )
            
            DetallePedido.objects.create(
                pedido=pedido2,
                producto=productos_creados[8],
                cantidad=3,
                precio_unitario=productos_creados[8].precio
            )
            
            DetallePedido.objects.create(
                pedido=pedido2,
                producto=productos_creados[11],
                cantidad=10,
                precio_unitario=productos_creados[11].precio
            )
            
            pedido2.calcular_total()
            print(f"✅ Pedido {pedido2.numero_pedido} creado - Total: ${pedido2.total}")
            
            # Crear pago pendiente
            Pago.objects.create(
                pedido=pedido2,
                metodo_pago='efectivo',
                estado='pendiente',
                monto=pedido2.total
            )
            print(f"✅ Pago creado para {pedido2.numero_pedido}")
        else:
            print("ℹ️  Pedido 2 ya existe")
        
        print("\n" + "="*60)
        print("✨ ¡DATOS DE PRUEBA CREADOS EXITOSAMENTE!")
        print("="*60)
        print("\n📊 Resumen Final:")
        print(f"  • Usuarios: {Usuario.objects.count()}")
        print(f"  • Negocios: {Negocio.objects.count()}")
        print(f"  • Categorías: {Categoria.objects.count()}")
        print(f"  • Productos: {Producto.objects.count()}")
        print(f"  • Pedidos: {Pedido.objects.count()}")
        print(f"  • Pagos: {Pago.objects.count()}")
        
        print("\n🔑 Credenciales de Acceso:")
        print("  ┌─────────────────────────────────────┐")
        print("  │ Comerciante:                        │")
        print("  │   Usuario: comerciante1             │")
        print("  │   Password: comerciante123          │")
        print("  ├─────────────────────────────────────┤")
        print("  │ Clientes:                           │")
        print("  │   Usuario: cliente1                 │")
        print("  │   Password: cliente123              │")
        print("  │                                     │")
        print("  │   Usuario: cliente2                 │")
        print("  │   Password: cliente123              │")
        print("  └─────────────────────────────────────┘")
        
        print("\n🌐 Accede al admin en: http://127.0.0.1:8000/admin/")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error al crear datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    limpiar_datos()
    crear_datos()
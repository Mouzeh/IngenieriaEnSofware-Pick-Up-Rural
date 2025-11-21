import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickup_rural.settings')
django.setup()

from productos.models import Producto

def actualizar_productos_perecederos():
    print("🔄 Actualizando productos perecederos...")
    
    # Productos refrigerados (2-8°C)
    refrigerados = [
        'leche', 'yogurt', 'queso', 'mantequilla', 'crema', 
        'jamón', 'salchichas', 'embutidos', 'yogur', 'leche'
    ]
    
    # Productos congelados (-18°C)
    congelados = [
        'helado', 'congelado', 'pollo congelado', 'pescado congelado',
        'carne congelada', 'vegetales congelados', 'mariscos congelados'
    ]
    
    # Productos frescos (caducidad corta)
    frescos = [
        'pan', 'torta', 'pastel', 'ensalada', 'fruta', 'verdura',
        'tomate', 'lechuga', 'cebolla', 'zanahoria', 'manzana', 'plátano'
    ]
    
    productos_actualizados = 0
    
    for producto in Producto.objects.filter(activo=True):
        nombre_lower = producto.nombre.lower()
        
        # Asignar refrigerados
        if any(p in nombre_lower for p in refrigerados):
            if producto.tipo_almacenamiento != 'refrigerado':
                producto.tipo_almacenamiento = 'refrigerado'
                producto.temperatura_ideal = 4.0
                producto.vida_util_horas = 72
                producto.requiere_embalaje_especial = True
                producto.save()
                print(f"❄️ REFRIGERADO: {producto.nombre}")
                productos_actualizados += 1
        
        # Asignar congelados
        elif any(p in nombre_lower for p in congelados):
            if producto.tipo_almacenamiento != 'congelado':
                producto.tipo_almacenamiento = 'congelado'
                producto.temperatura_ideal = -18.0
                producto.vida_util_horas = 720
                producto.requiere_embalaje_especial = True
                producto.save()
                print(f"🧊 CONGELADO: {producto.nombre}")
                productos_actualizados += 1
        
        # Asignar frescos
        elif any(p in nombre_lower for p in frescos):
            if producto.tipo_almacenamiento != 'fresco':
                producto.tipo_almacenamiento = 'fresco'
                producto.vida_util_horas = 24
                producto.requiere_embalaje_especial = False
                producto.save()
                print(f"🥬 FRESCO: {producto.nombre}")
                productos_actualizados += 1
        
        # Los demás quedan como 'ambiente' (default)
    
    print(f"✅ ¡Actualización completada! {productos_actualizados} productos actualizados")

if __name__ == '__main__':
    actualizar_productos_perecederos()
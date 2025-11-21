# fidelizacion/apps.py
from django.apps import AppConfig

class FidelizacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fidelizacion'
    
    def ready(self):
        import fidelizacion.signals
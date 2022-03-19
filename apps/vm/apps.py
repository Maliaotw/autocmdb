from django.apps import AppConfig

class VmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vm'

    def ready(self):
        import vm.signal


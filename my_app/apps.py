from django.apps import AppConfig
from .priceUpdater.getPricesApi import func

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_app'

    def ready(self):
        func()

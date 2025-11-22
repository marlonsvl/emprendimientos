from django.apps import AppConfig


class GastronomiaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gastronomia'

    def ready(self):
        # import signals so they get registered
        import gastronomia.signals  # noqa

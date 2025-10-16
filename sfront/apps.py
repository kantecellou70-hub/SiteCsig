from django.apps import AppConfig


class SfrontConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sfront'
    verbose_name = 'Site Public CSIG'
    
    def ready(self):
        """Appelé quand l'application est prête"""
        try:
            import sfront.templatetags.math_filters
            import sfront.templatetags.test_simple
        except ImportError:
            pass

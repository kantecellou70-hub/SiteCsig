"""
Configuration des tests pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.conf import settings

# Configuration spécifique aux tests
TEST_SETTINGS = {
    'CELERY_ALWAYS_EAGER': True,
    'CELERY_EAGER_PROPAGATES_EXCEPTIONS': True,
    'CELERY_BROKER_URL': 'memory://',
    'CELERY_RESULT_BACKEND': 'cache+memory://',
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'root': {
            'handlers': ['null'],
        },
        'loggers': {
            'jobs': {
                'handlers': ['null'],
                'propagate': False,
            },
        },
    }
}

class JobsTestCase(TestCase):
    """Classe de base pour tous les tests de l'application jobs"""
    
    @classmethod
    def setUpTestData(cls):
        """Configuration des données de test partagées entre tous les tests"""
        super().setUpTestData()
        
        # Ici, vous pouvez ajouter des données de test communes
        # qui seront partagées entre tous les tests de la classe
    
    def setUp(self):
        """Configuration avant chaque test individuel"""
        super().setUp()
        
        # Nettoyer le cache avant chaque test
        from django.core.cache import cache
        cache.clear()
    
    def tearDown(self):
        """Nettoyage après chaque test individuel"""
        # Nettoyer le cache après chaque test
        from django.core.cache import cache
        cache.clear()
        
        super().tearDown()

class JobsTestCaseWithCelery(JobsTestCase):
    """Classe de base pour les tests nécessitant Celery"""
    
    @override_settings(**TEST_SETTINGS)
    def setUp(self):
        """Configuration avec Celery en mode eager"""
        super().setUp()
        
        # Configuration supplémentaire pour Celery si nécessaire
        from celery import current_app
        current_app.conf.update(TEST_SETTINGS)

class JobsTestCaseWithEmail(JobsTestCase):
    """Classe de base pour les tests nécessitant l'envoi d'emails"""
    
    def setUp(self):
        """Configuration avec le backend d'email en mémoire"""
        super().setUp()
        
        # Vérifier que le backend d'email est configuré pour les tests
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.locmem.EmailBackend')
    
    def get_sent_emails(self):
        """Récupérer tous les emails envoyés pendant le test"""
        from django.core import mail
        return mail.outbox
    
    def assert_email_sent(self, to_email=None, subject=None, body_contains=None):
        """Vérifier qu'un email a été envoyé avec les critères spécifiés"""
        emails = self.get_sent_emails()
        
        if not emails:
            self.fail("Aucun email n'a été envoyé")
        
        if to_email:
            matching_emails = [e for e in emails if to_email in e.to]
            if not matching_emails:
                self.fail(f"Aucun email n'a été envoyé à {to_email}")
            emails = matching_emails
        
        if subject:
            matching_emails = [e for e in emails if subject in e.subject]
            if not matching_emails:
                self.fail(f"Aucun email avec le sujet '{subject}' n'a été trouvé")
            emails = matching_emails
        
        if body_contains:
            matching_emails = [e for e in emails if body_contains in e.body]
            if not matching_emails:
                self.fail(f"Aucun email contenant '{body_contains}' dans le corps n'a été trouvé")
            emails = matching_emails
        
        return emails[0] if emails else None

class JobsTestCaseWithCache(JobsTestCase):
    """Classe de base pour les tests nécessitant le cache"""
    
    def setUp(self):
        """Configuration avec le cache en mémoire"""
        super().setUp()
        
        # Vérifier que le cache est configuré pour les tests
        self.assertEqual(settings.CACHES['default']['BACKEND'], 
                        'django.core.cache.backends.locmem.LocMemCache')
    
    def clear_cache(self):
        """Nettoyer le cache"""
        from django.core.cache import cache
        cache.clear()
    
    def set_cache_value(self, key, value, timeout=None):
        """Définir une valeur en cache"""
        from django.core.cache import cache
        cache.set(key, value, timeout=timeout)
    
    def get_cache_value(self, key, default=None):
        """Récupérer une valeur du cache"""
        from django.core.cache import cache
        return cache.get(key, default)
    
    def assert_cache_has_key(self, key):
        """Vérifier qu'une clé existe en cache"""
        value = self.get_cache_value(key)
        self.assertIsNotNone(value, f"La clé '{key}' n'existe pas en cache")
    
    def assert_cache_not_has_key(self, key):
        """Vérifier qu'une clé n'existe pas en cache"""
        value = self.get_cache_value(key)
        self.assertIsNone(value, f"La clé '{key}' existe en cache avec la valeur: {value}")

class JobsTestCaseWithDatabase(JobsTestCase):
    """Classe de base pour les tests nécessitant des opérations de base de données"""
    
    def setUp(self):
        """Configuration avec la base de données de test"""
        super().setUp()
        
        # Vérifier que nous utilisons la base de données de test
        self.assertTrue(settings.DATABASES['default']['NAME'].endswith('_test'))
    
    def create_test_user(self, username='testuser', email='test@example.com', **kwargs):
        """Créer un utilisateur de test"""
        from django.contrib.auth.models import User
        
        user_data = {
            'username': username,
            'email': email,
            'password': 'testpass123',
            **kwargs
        }
        
        return User.objects.create_user(**user_data)
    
    def create_test_superuser(self, username='admin', email='admin@example.com', **kwargs):
        """Créer un superutilisateur de test"""
        from django.contrib.auth.models import User
        
        user_data = {
            'username': username,
            'email': email,
            'password': 'adminpass123',
            'is_staff': True,
            'is_superuser': True,
            **kwargs
        }
        
        return User.objects.create_user(**user_data)
    
    def assert_model_exists(self, model_class, **filters):
        """Vérifier qu'un modèle existe avec les filtres spécifiés"""
        try:
            instance = model_class.objects.get(**filters)
            self.assertIsNotNone(instance)
            return instance
        except model_class.DoesNotExist:
            self.fail(f"Le modèle {model_class.__name__} avec les filtres {filters} n'existe pas")
    
    def assert_model_not_exists(self, model_class, **filters):
        """Vérifier qu'un modèle n'existe pas avec les filtres spécifiés"""
        try:
            instance = model_class.objects.get(**filters)
            self.fail(f"Le modèle {model_class.__name__} avec les filtres {filters} existe: {instance}")
        except model_class.DoesNotExist:
            pass  # C'est ce que nous attendons

class JobsTestCaseWithSignals(JobsTestCase):
    """Classe de base pour les tests nécessitant des signaux"""
    
    def setUp(self):
        """Configuration avec les signaux"""
        super().setUp()
        
        # Ici, vous pouvez ajouter une configuration spécifique aux signaux
        # si nécessaire
    
    def disconnect_signal(self, signal, receiver, sender=None):
        """Déconnecter un signal"""
        signal.disconnect(receiver, sender=sender)
    
    def reconnect_signal(self, signal, receiver, sender=None):
        """Reconnecter un signal"""
        signal.connect(receiver, sender=sender)

# Configuration globale pour tous les tests
def configure_test_environment():
    """Configurer l'environnement de test global"""
    import os
    
    # Définir des variables d'environnement pour les tests
    os.environ.setdefault('DJANGO_ENV', 'testing')
    os.environ.setdefault('CELERY_ALWAYS_EAGER', 'True')
    os.environ.setdefault('CELERY_EAGER_PROPAGATES_EXCEPTIONS', 'True')

# Appeler la configuration au chargement du module
configure_test_environment()

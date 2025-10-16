"""
Tests de configuration pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import os

from .test_settings import JobsTestCaseWithCelery

class ConfigurationTest(JobsTestCaseWithCelery):
    """Tests de configuration pour l'application jobs"""
    
    def setUp(self):
        super().setUp()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def tearDown(self):
        super().tearDown()
        cache.clear()

class DjangoSettingsConfigurationTest(ConfigurationTest):
    """Tests de configuration des paramètres Django"""
    
    def test_installed_apps_configuration(self):
        """Test de la configuration des applications installées"""
        # Vérifier que l'application jobs est installée
        self.assertIn('jobs', settings.INSTALLED_APPS)
        
        # Vérifier que django_celery_results est installé
        self.assertIn('django_celery_results', settings.INSTALLED_APPS)
        
        # Vérifier que les applications de base sont présentes
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'content_management'
        ]
        
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
    
    def test_database_configuration(self):
        """Test de la configuration de la base de données"""
        # Vérifier que la base de données est configurée
        self.assertTrue(hasattr(settings, 'DATABASES'))
        self.assertIn('default', settings.DATABASES)
        
        # Vérifier la configuration de la base de données par défaut
        default_db = settings.DATABASES['default']
        
        # Vérifier les paramètres requis
        required_params = ['ENGINE', 'NAME']
        for param in required_params:
            self.assertIn(param, default_db)
            self.assertIsNotNone(default_db[param])
        
        # Vérifier le moteur de base de données
        engine = default_db['ENGINE']
        self.assertIn('django.db.backends', engine)
    
    def test_cache_configuration(self):
        """Test de la configuration du cache"""
        # Vérifier que le cache est configuré
        self.assertTrue(hasattr(settings, 'CACHES'))
        self.assertIn('default', settings.CACHES)
        
        # Vérifier la configuration du cache par défaut
        default_cache = settings.CACHES['default']
        
        # Vérifier le backend du cache
        self.assertIn('BACKEND', default_cache)
        backend = default_cache['BACKEND']
        
        # Vérifier que le backend est valide
        valid_backends = [
            'django.core.cache.backends.locmem.LocMemCache',
            'django.core.cache.backends.redis.RedisCache',
            'django.core.cache.backends.db.DatabaseCache'
        ]
        
        self.assertIn(backend, valid_backends)
    
    def test_middleware_configuration(self):
        """Test de la configuration des middlewares"""
        # Vérifier que les middlewares sont configurés
        self.assertTrue(hasattr(settings, 'MIDDLEWARE'))
        
        # Vérifier que les middlewares de base sont présents
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware'
        ]
        
        for middleware in required_middleware:
            self.assertIn(middleware, settings.MIDDLEWARE)
    
    def test_templates_configuration(self):
        """Test de la configuration des templates"""
        # Vérifier que les templates sont configurés
        self.assertTrue(hasattr(settings, 'TEMPLATES'))
        self.assertGreater(len(settings.TEMPLATES), 0)
        
        # Vérifier la configuration du premier template
        template_config = settings.TEMPLATES[0]
        
        # Vérifier les paramètres requis
        required_params = ['BACKEND', 'DIRS', 'APP_DIRS', 'OPTIONS']
        for param in required_params:
            self.assertIn(param, template_config)
        
        # Vérifier le backend des templates
        backend = template_config['BACKEND']
        self.assertIn('django.template.backends.django.DjangoTemplates', backend)
        
        # Vérifier que APP_DIRS est activé
        self.assertTrue(template_config['APP_DIRS'])

class CeleryConfigurationTest(ConfigurationTest):
    """Tests de configuration de Celery"""
    
    def test_celery_broker_configuration(self):
        """Test de la configuration du broker Celery"""
        # Vérifier que le broker Celery est configuré
        self.assertTrue(hasattr(settings, 'CELERY_BROKER_URL'))
        
        # Vérifier que l'URL du broker est une chaîne valide
        broker_url = settings.CELERY_BROKER_URL
        self.assertIsInstance(broker_url, str)
        self.assertGreater(len(broker_url), 0)
        
        # Vérifier que l'URL contient le protocole Redis
        self.assertIn('redis://', broker_url)
    
    def test_celery_result_backend_configuration(self):
        """Test de la configuration du backend de résultats Celery"""
        # Vérifier que le backend de résultats est configuré
        self.assertTrue(hasattr(settings, 'CELERY_RESULT_BACKEND'))
        
        # Vérifier que l'URL du backend est une chaîne valide
        result_backend = settings.CELERY_RESULT_BACKEND
        self.assertIsInstance(result_backend, str)
        self.assertGreater(len(result_backend), 0)
        
        # Vérifier que l'URL contient le protocole Redis
        self.assertIn('redis://', result_backend)
    
    def test_celery_serialization_configuration(self):
        """Test de la configuration de sérialisation Celery"""
        # Vérifier la configuration de sérialisation
        self.assertTrue(hasattr(settings, 'CELERY_ACCEPT_CONTENT'))
        self.assertTrue(hasattr(settings, 'CELERY_TASK_SERIALIZER'))
        self.assertTrue(hasattr(settings, 'CELERY_RESULT_SERIALIZER'))
        
        # Vérifier les types de contenu acceptés
        accept_content = settings.CELERY_ACCEPT_CONTENT
        self.assertIsInstance(accept_content, list)
        self.assertIn('json', accept_content)
        
        # Vérifier le sérialiseur des tâches
        task_serializer = settings.CELERY_TASK_SERIALIZER
        self.assertEqual(task_serializer, 'json')
        
        # Vérifier le sérialiseur des résultats
        result_serializer = settings.CELERY_RESULT_SERIALIZER
        self.assertEqual(result_serializer, 'json')
    
    def test_celery_timezone_configuration(self):
        """Test de la configuration du fuseau horaire Celery"""
        # Vérifier que le fuseau horaire est configuré
        self.assertTrue(hasattr(settings, 'CELERY_TIMEZONE'))
        
        # Vérifier que le fuseau horaire est une chaîne valide
        timezone = settings.CELERY_TIMEZONE
        self.assertIsInstance(timezone, str)
        self.assertGreater(len(timezone), 0)
        
        # Vérifier que le fuseau horaire correspond à celui de Django
        self.assertEqual(timezone, settings.TIME_ZONE)
    
    def test_celery_task_routing_configuration(self):
        """Test de la configuration du routage des tâches Celery"""
        # Vérifier que le routage des tâches est configuré
        self.assertTrue(hasattr(settings, 'CELERY_TASK_ROUTES'))
        
        # Vérifier que le routage est un dictionnaire
        task_routes = settings.CELERY_TASK_ROUTES
        self.assertIsInstance(task_routes, dict)
        
        # Vérifier que les routes de base sont configurées
        expected_routes = [
            'jobs.tasks.*',
            'jobs.email_tasks.*',
            'jobs.maintenance_tasks.*'
        ]
        
        for route in expected_routes:
            self.assertIn(route, task_routes)
    
    def test_celery_worker_configuration(self):
        """Test de la configuration des workers Celery"""
        # Vérifier la configuration des workers
        self.assertTrue(hasattr(settings, 'CELERY_WORKER_CONCURRENCY'))
        self.assertTrue(hasattr(settings, 'CELERY_WORKER_MAX_TASKS_PER_CHILD'))
        
        # Vérifier la concurrence des workers
        worker_concurrency = settings.CELERY_WORKER_CONCURRENCY
        self.assertIsInstance(worker_concurrency, int)
        self.assertGreater(worker_concurrency, 0)
        
        # Vérifier le nombre maximum de tâches par worker
        max_tasks = settings.CELERY_WORKER_MAX_TASKS_PER_CHILD
        self.assertIsInstance(max_tasks, int)
        self.assertGreater(max_tasks, 0)
    
    def test_celery_task_timeout_configuration(self):
        """Test de la configuration des timeouts des tâches Celery"""
        # Vérifier la configuration des timeouts
        self.assertTrue(hasattr(settings, 'CELERY_TASK_TIME_LIMIT'))
        self.assertTrue(hasattr(settings, 'CELERY_TASK_SOFT_TIME_LIMIT'))
        
        # Vérifier la limite de temps des tâches
        time_limit = settings.CELERY_TASK_TIME_LIMIT
        self.assertIsInstance(time_limit, int)
        self.assertGreater(time_limit, 0)
        
        # Vérifier la limite de temps douce des tâches
        soft_time_limit = settings.CELERY_TASK_SOFT_TIME_LIMIT
        self.assertIsInstance(soft_time_limit, int)
        self.assertGreater(soft_time_limit, 0)
        
        # Vérifier que la limite douce est inférieure à la limite dure
        self.assertLess(soft_time_limit, time_limit)

class EmailConfigurationTest(ConfigurationTest):
    """Tests de configuration de l'email"""
    
    def test_email_backend_configuration(self):
        """Test de la configuration du backend email"""
        # Vérifier que le backend email est configuré
        self.assertTrue(hasattr(settings, 'EMAIL_BACKEND'))
        
        # Vérifier que le backend est valide
        email_backend = settings.EMAIL_BACKEND
        valid_backends = [
            'django.core.mail.backends.smtp.EmailBackend',
            'django.core.mail.backends.console.EmailBackend',
            'django.core.mail.backends.filebased.EmailBackend'
        ]
        
        self.assertIn(email_backend, valid_backends)
    
    def test_smtp_configuration(self):
        """Test de la configuration SMTP"""
        # Vérifier que la configuration SMTP est présente
        self.assertTrue(hasattr(settings, 'EMAIL_HOST'))
        self.assertTrue(hasattr(settings, 'EMAIL_PORT'))
        self.assertTrue(hasattr(settings, 'EMAIL_USE_TLS'))
        self.assertTrue(hasattr(settings, 'EMAIL_USE_SSL'))
        
        # Vérifier l'hôte SMTP
        email_host = settings.EMAIL_HOST
        self.assertIsInstance(email_host, str)
        self.assertGreater(len(email_host), 0)
        
        # Vérifier le port SMTP
        email_port = settings.EMAIL_PORT
        self.assertIsInstance(email_port, int)
        self.assertGreater(email_port, 0)
        self.assertLess(email_port, 65536)
        
        # Vérifier que TLS ou SSL est activé (mais pas les deux)
        use_tls = settings.EMAIL_USE_TLS
        use_ssl = settings.EMAIL_USE_SSL
        
        self.assertIsInstance(use_tls, bool)
        self.assertIsInstance(use_ssl, bool)
        
        # TLS et SSL ne peuvent pas être activés en même temps
        self.assertFalse(use_tls and use_ssl)
    
    def test_email_credentials_configuration(self):
        """Test de la configuration des identifiants email"""
        # Vérifier que les identifiants sont configurés
        self.assertTrue(hasattr(settings, 'EMAIL_HOST_USER'))
        self.assertTrue(hasattr(settings, 'EMAIL_HOST_PASSWORD'))
        
        # Vérifier l'utilisateur SMTP
        email_user = settings.EMAIL_HOST_USER
        self.assertIsInstance(email_user, str)
        self.assertGreater(len(email_user), 0)
        
        # Vérifier que l'utilisateur est un email valide
        self.assertIn('@', email_user)
        self.assertIn('.', email_user)
        
        # Vérifier le mot de passe SMTP
        email_password = settings.EMAIL_HOST_PASSWORD
        self.assertIsInstance(email_password, str)
        self.assertGreater(len(email_password), 0)
    
    def test_email_defaults_configuration(self):
        """Test de la configuration des valeurs par défaut de l'email"""
        # Vérifier que les valeurs par défaut sont configurées
        self.assertTrue(hasattr(settings, 'DEFAULT_FROM_EMAIL'))
        self.assertTrue(hasattr(settings, 'DEFAULT_TO_EMAIL'))
        
        # Vérifier l'expéditeur par défaut
        default_from = settings.DEFAULT_FROM_EMAIL
        self.assertIsInstance(default_from, str)
        self.assertGreater(len(default_from), 0)
        
        # Vérifier que c'est un email valide
        self.assertIn('@', default_from)
        self.assertIn('.', default_from)
        
        # Vérifier le destinataire par défaut
        default_to = settings.DEFAULT_TO_EMAIL
        self.assertIsInstance(default_to, str)
        self.assertGreater(len(default_to), 0)
        
        # Vérifier que c'est un email valide
        self.assertIn('@', default_to)
        self.assertIn('.', default_to)

class LoggingConfigurationTest(ConfigurationTest):
    """Tests de configuration de la journalisation"""
    
    def test_logging_configuration_structure(self):
        """Test de la structure de la configuration de journalisation"""
        # Vérifier que la journalisation est configurée
        self.assertTrue(hasattr(settings, 'LOGGING'))
        
        # Vérifier que la configuration est un dictionnaire
        logging_config = settings.LOGGING
        self.assertIsInstance(logging_config, dict)
        
        # Vérifier les sections requises
        required_sections = ['version', 'disable_existing_loggers', 'formatters', 'handlers', 'loggers']
        for section in required_sections:
            self.assertIn(section, logging_config)
    
    def test_logging_version_configuration(self):
        """Test de la version de la configuration de journalisation"""
        # Vérifier la version
        logging_config = settings.LOGGING
        version = logging_config.get('version')
        
        # La version doit être 1
        self.assertEqual(version, 1)
    
    def test_logging_formatters_configuration(self):
        """Test de la configuration des formateurs de journalisation"""
        # Vérifier les formateurs
        logging_config = settings.LOGGING
        formatters = logging_config.get('formatters', {})
        
        # Vérifier que les formateurs sont configurés
        self.assertIsInstance(formatters, dict)
        self.assertGreater(len(formatters), 0)
        
        # Vérifier le formateur standard
        if 'standard' in formatters:
            standard_formatter = formatters['standard']
            self.assertIn('format', standard_formatter)
            self.assertIn('datefmt', standard_formatter)
    
    def test_logging_handlers_configuration(self):
        """Test de la configuration des gestionnaires de journalisation"""
        # Vérifier les gestionnaires
        logging_config = settings.LOGGING
        handlers = logging_config.get('handlers', {})
        
        # Vérifier que les gestionnaires sont configurés
        self.assertIsInstance(handlers, dict)
        self.assertGreater(len(handlers), 0)
        
        # Vérifier les gestionnaires de base
        expected_handlers = ['console', 'file']
        for handler_name in expected_handlers:
            if handler_name in handlers:
                handler = handlers[handler_name]
                self.assertIn('class', handler)
                self.assertIn('level', handler)
    
    def test_logging_loggers_configuration(self):
        """Test de la configuration des loggers"""
        # Vérifier les loggers
        logging_config = settings.LOGGING
        loggers = logging_config.get('loggers', {})
        
        # Vérifier que les loggers sont configurés
        self.assertIsInstance(loggers, dict)
        self.assertGreater(len(loggers), 0)
        
        # Vérifier le logger Django
        if 'django' in loggers:
            django_logger = loggers['django']
            self.assertIn('handlers', django_logger)
            self.assertIn('level', django_logger)
            self.assertIn('propagate', django_logger)
        
        # Vérifier le logger jobs
        if 'jobs' in loggers:
            jobs_logger = loggers['jobs']
            self.assertIn('handlers', jobs_logger)
            self.assertIn('level', jobs_logger)
            self.assertIn('propagate', jobs_logger)

class SecurityConfigurationTest(ConfigurationTest):
    """Tests de configuration de la sécurité"""
    
    def test_secret_key_configuration(self):
        """Test de la configuration de la clé secrète"""
        # Vérifier que la clé secrète est configurée
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        
        # Vérifier que la clé secrète est une chaîne
        secret_key = settings.SECRET_KEY
        self.assertIsInstance(secret_key, str)
        self.assertGreater(len(secret_key), 0)
        
        # Vérifier que la clé secrète n'est pas la valeur par défaut
        default_secret_key = 'django-insecure-'
        self.assertNotEqual(secret_key, default_secret_key)
    
    def test_debug_configuration(self):
        """Test de la configuration du mode debug"""
        # Vérifier que le mode debug est configuré
        self.assertTrue(hasattr(settings, 'DEBUG'))
        
        # Vérifier que DEBUG est un booléen
        debug = settings.DEBUG
        self.assertIsInstance(debug, bool)
        
        # En production, DEBUG doit être False
        if not debug:
            # Vérifier les paramètres de sécurité de production
            self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
            self.assertTrue(hasattr(settings, 'CSRF_COOKIE_SECURE'))
            self.assertTrue(hasattr(settings, 'SESSION_COOKIE_SECURE'))
    
    def test_allowed_hosts_configuration(self):
        """Test de la configuration des hôtes autorisés"""
        # Vérifier que les hôtes autorisés sont configurés
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        
        # Vérifier que ALLOWED_HOSTS est une liste
        allowed_hosts = settings.ALLOWED_HOSTS
        self.assertIsInstance(allowed_hosts, list)
        self.assertGreater(len(allowed_hosts), 0)
        
        # Vérifier que les hôtes sont des chaînes valides
        for host in allowed_hosts:
            self.assertIsInstance(host, str)
            self.assertGreater(len(host), 0)
    
    def test_csrf_configuration(self):
        """Test de la configuration CSRF"""
        # Vérifier que la configuration CSRF est présente
        self.assertTrue(hasattr(settings, 'CSRF_COOKIE_SECURE'))
        self.assertTrue(hasattr(settings, 'CSRF_COOKIE_HTTPONLY'))
        self.assertTrue(hasattr(settings, 'CSRF_TRUSTED_ORIGINS'))
        
        # Vérifier CSRF_COOKIE_SECURE
        csrf_secure = settings.CSRF_COOKIE_SECURE
        self.assertIsInstance(csrf_secure, bool)
        
        # Vérifier CSRF_COOKIE_HTTPONLY
        csrf_httponly = settings.CSRF_COOKIE_HTTPONLY
        self.assertIsInstance(csrf_httponly, bool)
        
        # Vérifier CSRF_TRUSTED_ORIGINS
        csrf_origins = settings.CSRF_TRUSTED_ORIGINS
        self.assertIsInstance(csrf_origins, list)
    
    def test_session_configuration(self):
        """Test de la configuration des sessions"""
        # Vérifier que la configuration des sessions est présente
        self.assertTrue(hasattr(settings, 'SESSION_COOKIE_SECURE'))
        self.assertTrue(hasattr(settings, 'SESSION_COOKIE_HTTPONLY'))
        self.assertTrue(hasattr(settings, 'SESSION_COOKIE_AGE'))
        
        # Vérifier SESSION_COOKIE_SECURE
        session_secure = settings.SESSION_COOKIE_SECURE
        self.assertIsInstance(session_secure, bool)
        
        # Vérifier SESSION_COOKIE_HTTPONLY
        session_httponly = settings.SESSION_COOKIE_HTTPONLY
        self.assertIsInstance(session_httponly, bool)
        
        # Vérifier SESSION_COOKIE_AGE
        session_age = settings.SESSION_COOKIE_AGE
        self.assertIsInstance(session_age, int)
        self.assertGreater(session_age, 0)

class EnvironmentConfigurationTest(ConfigurationTest):
    """Tests de configuration de l'environnement"""
    
    def test_environment_variables_configuration(self):
        """Test de la configuration des variables d'environnement"""
        # Vérifier que les variables d'environnement importantes sont définies
        important_vars = [
            'DJANGO_SETTINGS_MODULE',
            'PYTHONPATH'
        ]
        
        for var in important_vars:
            if var in os.environ:
                value = os.environ[var]
                self.assertIsInstance(value, str)
                self.assertGreater(len(value), 0)
    
    def test_site_url_configuration(self):
        """Test de la configuration de l'URL du site"""
        # Vérifier que l'URL du site est configurée
        self.assertTrue(hasattr(settings, 'SITE_URL'))
        
        # Vérifier que l'URL est une chaîne valide
        site_url = settings.SITE_URL
        self.assertIsInstance(site_url, str)
        self.assertGreater(len(site_url), 0)
        
        # Vérifier que l'URL commence par http:// ou https://
        self.assertTrue(site_url.startswith(('http://', 'https://')))
    
    def test_static_files_configuration(self):
        """Test de la configuration des fichiers statiques"""
        # Vérifier que la configuration des fichiers statiques est présente
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))
        
        # Vérifier STATIC_URL
        static_url = settings.STATIC_URL
        self.assertIsInstance(static_url, str)
        self.assertGreater(len(static_url), 0)
        self.assertTrue(static_url.startswith('/'))
        
        # Vérifier STATIC_ROOT
        static_root = settings.STATIC_ROOT
        self.assertIsInstance(static_root, str)
        self.assertGreater(len(static_root), 0)
        
        # Vérifier STATICFILES_DIRS
        static_dirs = settings.STATICFILES_DIRS
        self.assertIsInstance(static_dirs, list)
    
    def test_media_files_configuration(self):
        """Test de la configuration des fichiers média"""
        # Vérifier que la configuration des fichiers média est présente
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        
        # Vérifier MEDIA_URL
        media_url = settings.MEDIA_URL
        self.assertIsInstance(media_url, str)
        self.assertGreater(len(media_url), 0)
        self.assertTrue(media_url.startswith('/'))
        
        # Vérifier MEDIA_ROOT
        media_root = settings.MEDIA_ROOT
        self.assertIsInstance(media_root, str)
        self.assertGreater(len(media_root), 0)

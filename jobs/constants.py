"""
Constantes pour l'application jobs
"""

# Statuts des emails en file d'attente
EMAIL_STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('processing', 'En cours de traitement'),
    ('sent', 'Envoyé'),
    ('failed', 'Échoué'),
    ('cancelled', 'Annulé'),
]

# Priorités des emails
EMAIL_PRIORITY_CHOICES = [
    (1, 'Basse'),
    (2, 'Normale'),
    (3, 'Haute'),
    (4, 'Urgente'),
]

# Statuts des logs de newsletter
NEWSLETTER_LOG_STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('sending', 'En cours d\'envoi'),
    ('sent', 'Envoyé'),
    ('failed', 'Échoué'),
    ('bounced', 'Retourné'),
    ('opened', 'Ouvert'),
    ('clicked', 'Cliqué'),
]

# Statuts des campagnes de newsletter
NEWSLETTER_CAMPAIGN_STATUS_CHOICES = [
    ('draft', 'Brouillon'),
    ('scheduled', 'Programmée'),
    ('sending', 'En cours d\'envoi'),
    ('completed', 'Terminée'),
    ('failed', 'Échouée'),
    ('cancelled', 'Annulée'),
]

# Types de cibles pour les newsletters
NEWSLETTER_TARGET_CHOICES = [
    ('all', 'Tous les abonnés'),
    ('active', 'Abonnés actifs uniquement'),
    ('inactive', 'Abonnés inactifs uniquement'),
    ('language', 'Par langue'),
    ('custom', 'Liste personnalisée'),
]

# Langues supportées
LANGUAGE_CHOICES = [
    ('fr', 'Français'),
    ('en', 'Anglais'),
    ('es', 'Espagnol'),
    ('de', 'Allemand'),
    ('it', 'Italien'),
    ('pt', 'Portugais'),
    ('ar', 'Arabe'),
    ('zh', 'Chinois'),
    ('ja', 'Japonais'),
    ('ko', 'Coréen'),
]

# Types de tâches
TASK_TYPE_CHOICES = [
    ('email', 'Envoi d\'email'),
    ('newsletter', 'Newsletter'),
    ('maintenance', 'Maintenance'),
    ('backup', 'Sauvegarde'),
    ('cleanup', 'Nettoyage'),
    ('health_check', 'Vérification de santé'),
    ('report', 'Rapport'),
    ('custom', 'Tâche personnalisée'),
]

# Statuts des tâches
TASK_STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('running', 'En cours'),
    ('completed', 'Terminée'),
    ('failed', 'Échouée'),
    ('cancelled', 'Annulée'),
    ('retrying', 'En retry'),
]

# Types de maintenance
MAINTENANCE_TYPE_CHOICES = [
    ('daily', 'Quotidienne'),
    ('weekly', 'Hebdomadaire'),
    ('monthly', 'Mensuelle'),
    ('quarterly', 'Trimestrielle'),
    ('yearly', 'Annuelle'),
    ('on_demand', 'À la demande'),
]

# Types de vérification de santé
HEALTH_CHECK_TYPE_CHOICES = [
    ('basic', 'Basique'),
    ('detailed', 'Détaillée'),
    ('performance', 'Performance'),
    ('security', 'Sécurité'),
    ('full', 'Complète'),
]

# Composants système à surveiller
SYSTEM_COMPONENTS = [
    'database',
    'cache',
    'storage',
    'memory',
    'cpu',
    'network',
    'celery',
    'email',
    'external_services',
]

# Seuils d'alerte pour la santé du système
HEALTH_THRESHOLDS = {
    'disk_usage_warning': 80.0,      # 80% d'utilisation disque
    'disk_usage_critical': 95.0,     # 95% d'utilisation disque
    'memory_usage_warning': 80.0,    # 80% d'utilisation mémoire
    'memory_usage_critical': 95.0,   # 95% d'utilisation mémoire
    'cpu_usage_warning': 80.0,       # 80% d'utilisation CPU
    'cpu_usage_critical': 95.0,      # 95% d'utilisation CPU
    'database_connections_warning': 80,  # 80% des connexions max
    'database_connections_critical': 95, # 95% des connexions max
}

# Configuration des retry
RETRY_CONFIG = {
    'max_retries': 3,
    'base_delay': 60,        # 1 minute
    'max_delay': 3600,       # 1 heure
    'backoff_factor': 2,     # Multiplicateur exponentiel
}

# Configuration des timeouts
TIMEOUT_CONFIG = {
    'email_sending': 300,    # 5 minutes
    'task_execution': 1800,  # 30 minutes
    'database_operation': 60, # 1 minute
    'external_api_call': 120, # 2 minutes
}

# Configuration des limites de taux
RATE_LIMIT_CONFIG = {
    'emails_per_minute': 60,
    'emails_per_hour': 1000,
    'emails_per_day': 10000,
    'tasks_per_minute': 100,
    'tasks_per_hour': 1000,
    'tasks_per_day': 10000,
}

# Configuration des queues
QUEUE_CONFIG = {
    'default': {
        'priority': 1,
        'concurrency': 4,
        'max_tasks_per_child': 1000,
    },
    'email': {
        'priority': 2,
        'concurrency': 2,
        'max_tasks_per_child': 500,
    },
    'newsletter': {
        'priority': 3,
        'concurrency': 1,
        'max_tasks_per_child': 100,
    },
    'maintenance': {
        'priority': 1,
        'concurrency': 1,
        'max_tasks_per_child': 100,
    },
    'monitoring': {
        'priority': 2,
        'concurrency': 1,
        'max_tasks_per_child': 100,
    },
    'emergency': {
        'priority': 5,
        'concurrency': 2,
        'max_tasks_per_child': 50,
    },
}

# Configuration des tâches programmées
SCHEDULED_TASKS = {
    'daily_maintenance': {
        'hour': 2,
        'minute': 0,
        'enabled': True,
    },
    'daily_health_check': {
        'hour': 8,
        'minute': 0,
        'enabled': True,
    },
    'weekly_backup': {
        'day_of_week': 0,  # Dimanche
        'hour': 1,
        'minute': 0,
        'enabled': True,
    },
    'email_queue_processing': {
        'minute': '*/5',  # Toutes les 5 minutes
        'enabled': True,
    },
    'newsletter_scheduled_sending': {
        'minute': '*/15',  # Toutes les 15 minutes
        'enabled': True,
    },
}

# Configuration des notifications
NOTIFICATION_CONFIG = {
    'email_notifications': True,
    'webhook_notifications': False,
    'slack_notifications': False,
    'admin_email': 'admin@example.com',
    'notification_levels': ['error', 'warning', 'info'],
}

# Configuration des logs
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5,
    'retention_days': 30,
}

# Configuration des métriques
METRICS_CONFIG = {
    'enabled': True,
    'collection_interval': 300,  # 5 minutes
    'retention_days': 90,
    'aggregation_rules': {
        'hourly': '1h',
        'daily': '1d',
        'weekly': '1w',
        'monthly': '1M',
    },
}

# Configuration des sauvegardes
BACKUP_CONFIG = {
    'enabled': True,
    'retention_days': 30,
    'compression': True,
    'encryption': False,
    'storage_backend': 'local',  # local, s3, gcs
    'backup_schedule': 'weekly',
}

# Configuration des nettoyages
CLEANUP_CONFIG = {
    'old_logs_days': 30,
    'old_emails_days': 7,
    'old_tasks_days': 90,
    'old_backups_days': 365,
    'temp_files_hours': 24,
    'cache_cleanup_hours': 6,
}

# Configuration des tests
TEST_CONFIG = {
    'email_test_enabled': True,
    'database_test_enabled': True,
    'celery_test_enabled': True,
    'external_services_test_enabled': False,
    'test_interval_hours': 24,
}

# Configuration des webhooks
WEBHOOK_CONFIG = {
    'enabled': False,
    'endpoints': {
        'task_completed': '/webhooks/task-completed/',
        'task_failed': '/webhooks/task-failed/',
        'system_alert': '/webhooks/system-alert/',
        'email_delivered': '/webhooks/email-delivered/',
    },
    'timeout': 30,
    'retry_count': 3,
    'retry_delay': 60,
}

# Configuration des API
API_CONFIG = {
    'enabled': True,
    'version': 'v1',
    'rate_limit': '100/hour',
    'authentication': 'token',
    'pagination': {
        'default_page_size': 50,
        'max_page_size': 1000,
    },
}

# Configuration des rapports
REPORT_CONFIG = {
    'enabled': True,
    'formats': ['html', 'pdf', 'csv', 'json'],
    'scheduling': {
        'daily': True,
        'weekly': True,
        'monthly': True,
        'quarterly': False,
        'yearly': False,
    },
    'delivery': {
        'email': True,
        'webhook': False,
        'file_export': False,
    },
}

# Configuration des alertes
ALERT_CONFIG = {
    'enabled': True,
    'channels': ['email', 'webhook'],
    'severity_levels': ['info', 'warning', 'error', 'critical'],
    'escalation_rules': {
        'warning': {'delay_minutes': 30, 'escalate_to': 'admin'},
        'error': {'delay_minutes': 15, 'escalate_to': 'admin'},
        'critical': {'delay_minutes': 5, 'escalate_to': 'emergency'},
    },
}

# Configuration des performances
PERFORMANCE_CONFIG = {
    'monitoring_enabled': True,
    'profiling_enabled': False,
    'slow_query_threshold': 1000,  # ms
    'memory_usage_threshold': 80,  # %
    'cpu_usage_threshold': 80,     # %
    'response_time_threshold': 5000,  # ms
}

# Configuration de la sécurité
SECURITY_CONFIG = {
    'audit_logging': True,
    'access_control': True,
    'rate_limiting': True,
    'input_validation': True,
    'sql_injection_protection': True,
    'xss_protection': True,
    'csrf_protection': True,
}

# Configuration des environnements
ENVIRONMENT_CONFIG = {
    'development': {
        'debug': True,
        'log_level': 'DEBUG',
        'celery_worker_concurrency': 1,
        'email_backend': 'console',
        'cache_backend': 'dummy',
    },
    'staging': {
        'debug': False,
        'log_level': 'INFO',
        'celery_worker_concurrency': 2,
        'email_backend': 'smtp',
        'cache_backend': 'redis',
    },
    'production': {
        'debug': False,
        'log_level': 'WARNING',
        'celery_worker_concurrency': 4,
        'email_backend': 'smtp',
        'cache_backend': 'redis',
    },
}

# Messages d'erreur par défaut
DEFAULT_ERROR_MESSAGES = {
    'template_not_found': 'Template non trouvé',
    'email_send_failed': 'Échec de l\'envoi de l\'email',
    'task_execution_failed': 'Échec de l\'exécution de la tâche',
    'worker_not_found': 'Worker non trouvé',
    'queue_not_found': 'Queue non trouvée',
    'system_health_degraded': 'Santé du système dégradée',
    'configuration_error': 'Erreur de configuration',
    'validation_error': 'Erreur de validation',
    'database_error': 'Erreur de base de données',
    'permission_denied': 'Permission refusée',
    'resource_not_found': 'Ressource non trouvée',
    'timeout_error': 'Délai d\'attente dépassé',
    'rate_limit_exceeded': 'Limite de taux dépassée',
}

# Codes d'erreur
ERROR_CODES = {
    'SUCCESS': 'SUCCESS',
    'GENERAL_ERROR': 'GENERAL_ERROR',
    'VALIDATION_ERROR': 'VALIDATION_ERROR',
    'NOT_FOUND': 'NOT_FOUND',
    'PERMISSION_DENIED': 'PERMISSION_DENIED',
    'TIMEOUT': 'TIMEOUT',
    'RATE_LIMIT_EXCEEDED': 'RATE_LIMIT_EXCEEDED',
    'CONFIGURATION_ERROR': 'CONFIGURATION_ERROR',
    'DATABASE_ERROR': 'DATABASE_ERROR',
    'EMAIL_ERROR': 'EMAIL_ERROR',
    'NEWSLETTER_ERROR': 'NEWSLETTER_ERROR',
    'TASK_ERROR': 'TASK_ERROR',
    'WORKER_ERROR': 'WORKER_ERROR',
    'QUEUE_ERROR': 'QUEUE_ERROR',
    'SYSTEM_ERROR': 'SYSTEM_ERROR',
}

# Statuts de réponse HTTP
HTTP_STATUS_CODES = {
    'OK': 200,
    'CREATED': 201,
    'NO_CONTENT': 204,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': 405,
    'CONFLICT': 409,
    'UNPROCESSABLE_ENTITY': 422,
    'TOO_MANY_REQUESTS': 429,
    'INTERNAL_SERVER_ERROR': 500,
    'SERVICE_UNAVAILABLE': 503,
}

# Formats de date et heure
DATETIME_FORMATS = {
    'display': '%d/%m/%Y %H:%M',
    'date_only': '%d/%m/%Y',
    'time_only': '%H:%M',
    'iso': '%Y-%m-%dT%H:%M:%S%z',
    'filename': '%Y%m%d_%H%M%S',
    'log': '%Y-%m-%d %H:%M:%S',
}

# Tailles de fichiers
FILE_SIZES = {
    'max_email_attachment': 10 * 1024 * 1024,  # 10 MB
    'max_template_size': 1024 * 1024,          # 1 MB
    'max_log_file_size': 100 * 1024 * 1024,   # 100 MB
    'max_backup_file_size': 1024 * 1024 * 1024,  # 1 GB
}

# Types MIME
MIME_TYPES = {
    'html': 'text/html',
    'text': 'text/plain',
    'json': 'application/json',
    'xml': 'application/xml',
    'csv': 'text/csv',
    'pdf': 'application/pdf',
    'zip': 'application/zip',
    'gzip': 'application/gzip',
}

# Encodages
ENCODINGS = {
    'default': 'utf-8',
    'fallback': 'latin-1',
    'email': 'utf-8',
    'database': 'utf-8',
    'file': 'utf-8',
}

# Configuration des sessions
SESSION_CONFIG = {
    'timeout': 3600,  # 1 heure
    'max_age': 86400,  # 24 heures
    'secure': True,
    'http_only': True,
    'same_site': 'Lax',
}

# Configuration des cookies
COOKIE_CONFIG = {
    'max_age': 86400,  # 24 heures
    'secure': True,
    'http_only': True,
    'same_site': 'Lax',
    'domain': None,
    'path': '/',
}

# Configuration des en-têtes HTTP
HTTP_HEADERS = {
    'security': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
    },
    'cache': {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
    },
}

# Configuration des middlewares
MIDDLEWARE_CONFIG = {
    'security': [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ],
    'performance': [
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
    ],
    'logging': [
        'django.middleware.logging.LoggingMiddleware',
    ],
}

# Configuration des caches
CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
        'KEY_PREFIX': 'jobs',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'sessions',
    },
}

# Configuration des bases de données
DATABASE_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'csig_db',
        'USER': 'csig_user',
        'PASSWORD': 'csig_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    },
}

# Configuration des emails
EMAIL_CONFIG = {
    'backend': 'django.core.mail.backends.smtp.EmailBackend',
    'host': 'smtp.gmail.com',
    'port': 587,
    'use_tls': True,
    'use_ssl': False,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'default_from_email': 'noreply@example.com',
    'default_to_email': 'admin@example.com',
    'timeout': 30,
    'ssl_keyfile': None,
    'ssl_certfile': None,
}

# Configuration de Celery
CELERY_CONFIG = {
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'django-db',
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,
    'worker_concurrency': 4,
    'worker_max_tasks_per_child': 1000,
    'worker_prefetch_multiplier': 1,
    'task_always_eager': False,
    'task_eager_propagates': True,
    'task_ignore_result': False,
    'task_store_eager_result': True,
    'task_annotations': {
        'tasks.add': {'rate_limit': '10/s'},
    },
    'beat_schedule': {},
    'beat_scheduler': 'django_celery_beat.schedulers:DatabaseScheduler',
}

# Configuration de Redis
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True,
    'max_connections': 20,
    'health_check_interval': 30,
}

# Configuration des logs
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/jobs.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'jobs': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

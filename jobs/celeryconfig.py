# Configuration spécifique pour Celery
from celery import Celery
import os

# Configuration des tâches
CELERY_TASK_ROUTES = {
    'jobs.tasks.send_newsletter_email': {'queue': 'newsletter'},
    'jobs.tasks.send_bulk_newsletter': {'queue': 'newsletter'},
    'jobs.tasks.send_scheduled_newsletter': {'queue': 'newsletter'},
    'jobs.tasks.cleanup_old_newsletter_logs': {'queue': 'maintenance'},
    'jobs.tasks.test_email_connection': {'queue': 'maintenance'},
}

# Configuration des queues
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

# Configuration des résultats
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_STORE_EAGER_RESULT = True

# Configuration des retry
CELERY_TASK_ANNOTATIONS = {
    'jobs.tasks.send_newsletter_email': {
        'retry_backoff': True,
        'retry_backoff_max': 600,
        'max_retries': 3,
    },
    'jobs.tasks.send_bulk_newsletter': {
        'retry_backoff': True,
        'retry_backoff_max': 600,
        'max_retries': 3,
    },
}

# Configuration des workers
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Configuration des tâches programmées (Beat)
CELERY_BEAT_SCHEDULE = {
    'test-email-connection-daily': {
        'task': 'jobs.tasks.test_email_connection',
        'schedule': 86400.0,  # 24 heures
    },
    'cleanup-old-logs-weekly': {
        'task': 'jobs.tasks.cleanup_old_newsletter_logs',
        'schedule': 604800.0,  # 7 jours
    },
}

# Configuration des logs
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

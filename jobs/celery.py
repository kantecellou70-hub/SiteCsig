import os
from celery import Celery
from django.conf import settings

# Définir le module de paramètres Django par défaut pour le programme 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csigwebsite.settings')

app = Celery('csigwebsite')

# Utiliser une chaîne ici signifie que l'utilisateur n'a pas à sérialiser
# l'objet de configuration vers les processus enfants.
# - namespace='CELERY' signifie que toutes les clés de configuration liées à Celery
#   doivent avoir un préfixe `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger automatiquement les tâches depuis tous les fichiers `tasks.py` enregistrés
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configuration des tâches périodiques (beat)
app.conf.beat_schedule = {
    'test-email-connection-daily': {
        'task': 'jobs.tasks.test_email_connection',
        'schedule': 86400.0,  # 24 heures
    },
    'cleanup-old-newsletter-logs-weekly': {
        'task': 'jobs.tasks.cleanup_old_newsletter_logs',
        'schedule': 604800.0,  # 7 jours
        'args': (30,),  # Nettoyer les logs de plus de 30 jours
    },
}

# Configuration des tâches
app.conf.update(
    # Nombre maximum de tâches simultanées
    worker_concurrency=4,
    
    # Limite de mémoire par worker (en MB)
    worker_max_memory_per_child=200000,
    
    # Timeout pour les tâches (en secondes)
    task_time_limit=3600,  # 1 heure
    
    # Timeout pour les tâches douces (en secondes)
    task_soft_time_limit=3000,  # 50 minutes
    
    # Configuration des retry
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configuration des résultats
    result_expires=3600,  # Résultats expirés après 1 heure
    
    # Configuration des queues
    task_default_queue='default',
    task_routes={
        'jobs.tasks.send_newsletter_email': {'queue': 'newsletter'},
        'jobs.tasks.send_bulk_newsletter': {'queue': 'newsletter'},
        'jobs.tasks.send_scheduled_newsletter': {'queue': 'newsletter'},
    },
    
    # Configuration des workers
    worker_disable_rate_limits=False,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

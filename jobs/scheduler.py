"""
Configuration des tâches programmées pour Celery Beat
"""
from celery.schedules import crontab
from .tasks import (
    test_email_connection, cleanup_old_newsletter_logs,
    cleanup_old_files, cleanup_database, check_system_health,
    backup_database, optimize_database, send_health_report
)
from .email_tasks import (
    process_email_queue, cleanup_failed_emails, retry_failed_emails
)

# Configuration des tâches programmées
CELERY_BEAT_SCHEDULE = {
    # Tâches de maintenance quotidiennes
    'daily-maintenance': {
        'task': 'jobs.tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # 2h00 du matin
        'options': {'queue': 'maintenance'}
    },
    
    'daily-database-cleanup': {
        'task': 'jobs.tasks.cleanup_database',
        'schedule': crontab(hour=3, minute=0),  # 3h00 du matin
        'options': {'queue': 'maintenance'}
    },
    
    'daily-email-queue-cleanup': {
        'task': 'jobs.email_tasks.cleanup_failed_emails',
        'schedule': crontab(hour=4, minute=0),  # 4h00 du matin
        'options': {'queue': 'maintenance'}
    },
    
    'daily-email-queue-retry': {
        'task': 'jobs.email_tasks.retry_failed_emails',
        'schedule': crontab(hour=5, minute=0),  # 5h00 du matin
        'options': {'queue': 'maintenance'}
    },
    
    # Tâches de maintenance hebdomadaires
    'weekly-database-backup': {
        'task': 'jobs.tasks.backup_database',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),  # Dimanche 1h00
        'options': {'queue': 'maintenance'}
    },
    
    'weekly-database-optimization': {
        'task': 'jobs.tasks.optimize_database',
        'schedule': crontab(day_of_week=0, hour=6, minute=0),  # Dimanche 6h00
        'options': {'queue': 'maintenance'}
    },
    
    'weekly-newsletter-logs-cleanup': {
        'task': 'jobs.tasks.cleanup_old_newsletter_logs',
        'schedule': crontab(day_of_week=0, hour=7, minute=0),  # Dimanche 7h00
        'options': {'queue': 'maintenance'}
    },
    
    # Tâches de surveillance continues
    'hourly-system-health-check': {
        'task': 'jobs.tasks.check_system_health',
        'schedule': crontab(minute=0),  # Toutes les heures
        'options': {'queue': 'monitoring'}
    },
    
    'every-5-minutes-email-queue-process': {
        'task': 'jobs.email_tasks.process_email_queue',
        'schedule': crontab(minute='*/5'),  # Toutes les 5 minutes
        'options': {'queue': 'email'}
    },
    
    # Tâches de test et surveillance
    'daily-email-connection-test': {
        'task': 'jobs.tasks.test_email_connection',
        'schedule': crontab(hour=8, minute=0),  # 8h00 du matin
        'options': {'queue': 'monitoring'}
    },
    
    'daily-health-report': {
        'task': 'jobs.tasks.send_health_report',
        'schedule': crontab(hour=9, minute=0),  # 9h00 du matin
        'options': {'queue': 'email'}
    },
    
    # Tâches de newsletter programmées
    'check-scheduled-newsletters': {
        'task': 'jobs.tasks.send_scheduled_newsletter',
        'schedule': crontab(minute='*/15'),  # Toutes les 15 minutes
        'options': {'queue': 'newsletter'}
    },
}

# Configuration des tâches de surveillance
CELERY_BEAT_SCHEDULE_FLEXIBLE = {
    # Tâches qui peuvent être exécutées de manière flexible
    'flexible-maintenance': {
        'task': 'jobs.tasks.cleanup_old_files',
        'schedule': 3600.0,  # Toutes les heures
        'options': {'queue': 'maintenance'}
    },
    
    'flexible-email-processing': {
        'task': 'jobs.email_tasks.process_email_queue',
        'schedule': 300.0,  # Toutes les 5 minutes
        'options': {'queue': 'email'}
    },
}

# Configuration des tâches de surveillance en temps réel
CELERY_BEAT_SCHEDULE_REALTIME = {
    # Tâches critiques qui doivent être exécutées rapidement
    'realtime-email-queue': {
        'task': 'jobs.email_tasks.process_email_queue',
        'schedule': 60.0,  # Toutes les minutes
        'options': {'queue': 'email', 'priority': 4}
    },
    
    'realtime-system-health': {
        'task': 'jobs.tasks.check_system_health',
        'schedule': 300.0,  # Toutes les 5 minutes
        'options': {'queue': 'monitoring', 'priority': 3}
    },
}

# Configuration des tâches de maintenance d'urgence
CELERY_BEAT_SCHEDULE_EMERGENCY = {
    # Tâches qui peuvent être déclenchées en cas d'urgence
    'emergency-cleanup': {
        'task': 'jobs.tasks.cleanup_old_files',
        'schedule': 1800.0,  # Toutes les 30 minutes
        'options': {'queue': 'emergency', 'priority': 5}
    },
    
    'emergency-database-cleanup': {
        'task': 'jobs.tasks.cleanup_database',
        'schedule': 3600.0,  # Toutes les heures
        'options': {'queue': 'emergency', 'priority': 5}
    },
}

# Configuration des tâches de développement
CELERY_BEAT_SCHEDULE_DEV = {
    # Tâches spécifiques au développement
    'dev-email-test': {
        'task': 'jobs.tasks.test_email_connection',
        'schedule': 1800.0,  # Toutes les 30 minutes
        'options': {'queue': 'dev', 'priority': 1}
    },
    
    'dev-system-health': {
        'task': 'jobs.tasks.check_system_health',
        'schedule': 600.0,  # Toutes les 10 minutes
        'options': {'queue': 'dev', 'priority': 1}
    },
}

# Sélection du planning selon l'environnement
def get_beat_schedule():
    """
    Retourne le planning approprié selon l'environnement
    """
    import os
    
    environment = os.environ.get('DJANGO_ENV', 'production')
    
    if environment == 'development':
        return {**CELERY_BEAT_SCHEDULE, **CELERY_BEAT_SCHEDULE_DEV}
    elif environment == 'staging':
        return {**CELERY_BEAT_SCHEDULE, **CELERY_BEAT_SCHEDULE_FLEXIBLE}
    elif environment == 'production':
        return CELERY_BEAT_SCHEDULE
    else:
        return CELERY_BEAT_SCHEDULE

# Configuration des tâches de surveillance des performances
CELERY_BEAT_SCHEDULE_PERFORMANCE = {
    'performance-monitoring': {
        'task': 'jobs.tasks.check_system_health',
        'schedule': 300.0,  # Toutes les 5 minutes
        'options': {'queue': 'performance', 'priority': 2}
    },
    
    'performance-optimization': {
        'task': 'jobs.tasks.optimize_database',
        'schedule': 86400.0,  # Tous les jours
        'options': {'queue': 'performance', 'priority': 2}
    },
}

# Configuration des tâches de sécurité
CELERY_BEAT_SCHEDULE_SECURITY = {
    'security-audit': {
        'task': 'jobs.tasks.check_system_health',
        'schedule': 3600.0,  # Toutes les heures
        'options': {'queue': 'security', 'priority': 4}
    },
    
    'security-cleanup': {
        'task': 'jobs.tasks.cleanup_database',
        'schedule': 43200.0,  # Toutes les 12 heures
        'options': {'queue': 'security', 'priority': 4}
    },
}

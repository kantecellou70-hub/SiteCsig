"""
Tâches Celery pour la maintenance du système
"""
import logging
import os
import shutil
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import psutil

logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_files():
    """
    Nettoie les anciens fichiers temporaires et uploads
    """
    try:
        cleaned_count = 0
        
        # Nettoyer les fichiers temporaires
        temp_dirs = [
            os.path.join(settings.MEDIA_ROOT, 'temp'),
            os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp'),
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        # Supprimer les fichiers de plus de 24h
                        if os.path.isfile(file_path):
                            file_age = timezone.now() - datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
                            if file_age > timedelta(hours=24):
                                os.remove(file_path)
                                cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer {file_path}: {str(e)}")
        
        # Nettoyer le cache
        cache.clear()
        
        logger.info(f"Nettoyage des fichiers terminé: {cleaned_count} fichiers supprimés")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des fichiers: {str(e)}")
        raise

@shared_task
def cleanup_database():
    """
    Nettoie la base de données (tables de session, logs, etc.)
    """
    try:
        cleaned_count = 0
        
        with connection.cursor() as cursor:
            # Nettoyer les anciennes sessions Django
            cursor.execute("""
                DELETE FROM django_session 
                WHERE expire_date < %s
            """, [timezone.now()])
            cleaned_count += cursor.rowcount
            
            # Nettoyer les anciens logs de Celery
            cursor.execute("""
                DELETE FROM django_celery_results_taskresult 
                WHERE date_done < %s
            """, [timezone.now() - timedelta(days=30)])
            cleaned_count += cursor.rowcount
        
        logger.info(f"Nettoyage de la base de données terminé: {cleaned_count} enregistrements supprimés")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de la base de données: {str(e)}")
        raise

@shared_task
def check_system_health():
    """
    Vérifie la santé du système (espace disque, mémoire, etc.)
    """
    try:
        health_status = {
            'timestamp': timezone.now().isoformat(),
            'disk_usage': {},
            'memory_usage': {},
            'database_connections': 0,
            'celery_workers': 0,
            'overall_status': 'healthy'
        }
        
        # Vérifier l'espace disque
        for path in [settings.MEDIA_ROOT, settings.BASE_DIR]:
            if os.path.exists(path):
                total, used, free = shutil.disk_usage(path)
                usage_percent = (used / total) * 100
                
                health_status['disk_usage'][path] = {
                    'total_gb': round(total / (1024**3), 2),
                    'used_gb': round(used / (1024**3), 2),
                    'free_gb': round(free / (1024**3), 2),
                    'usage_percent': round(usage_percent, 2)
                }
                
                if usage_percent > 90:
                    health_status['overall_status'] = 'warning'
                elif usage_percent > 95:
                    health_status['overall_status'] = 'critical'
        
        # Vérifier la mémoire
        memory = psutil.virtual_memory()
        health_status['memory_usage'] = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'usage_percent': round(memory.percent, 2)
        }
        
        if memory.percent > 90:
            health_status['overall_status'] = 'warning'
        elif memory.percent > 95:
            health_status['overall_status'] = 'critical'
        
        # Vérifier les connexions de base de données
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity")
                health_status['database_connections'] = cursor.fetchone()[0]
        except:
            health_status['database_connections'] = 0
        
        # Vérifier les workers Celery
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            if active_workers:
                health_status['celery_workers'] = len(active_workers)
            else:
                health_status['celery_workers'] = 0
                health_status['overall_status'] = 'warning'
        except:
            health_status['celery_workers'] = 0
            health_status['overall_status'] = 'warning'
        
        # Stocker le statut dans le cache
        cache.set('system_health_status', health_status, timeout=300)  # 5 minutes
        
        logger.info(f"Vérification de la santé du système terminée: {health_status['overall_status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la santé du système: {str(e)}")
        raise

@shared_task
def backup_database():
    """
    Crée une sauvegarde de la base de données
    """
    try:
        from django.conf import settings
        
        # Créer le répertoire de sauvegarde
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nom du fichier de sauvegarde
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Commande de sauvegarde PostgreSQL
        db_settings = settings.DATABASES['default']
        backup_command = f"pg_dump -h {db_settings['HOST']} -U {db_settings['USER']} -d {db_settings['NAME']} > {backup_path}"
        
        # Exécuter la sauvegarde
        result = os.system(backup_command)
        
        if result == 0:
            # Compresser la sauvegarde
            import gzip
            with open(backup_path, 'rb') as f_in:
                with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Supprimer le fichier non compressé
            os.remove(backup_path)
            
            # Supprimer les anciennes sauvegardes (garder les 10 plus récentes)
            backup_files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.gz')])
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    os.remove(os.path.join(backup_dir, old_backup))
            
            logger.info(f"Sauvegarde de la base de données créée: {backup_filename}.gz")
            return f"{backup_filename}.gz"
        else:
            raise Exception(f"Échec de la sauvegarde avec le code de sortie: {result}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la base de données: {str(e)}")
        raise

@shared_task
def optimize_database():
    """
    Optimise la base de données (VACUUM, ANALYZE, etc.)
    """
    try:
        with connection.cursor() as cursor:
            # VACUUM pour libérer l'espace
            cursor.execute("VACUUM ANALYZE")
            
            # Mettre à jour les statistiques
            cursor.execute("ANALYZE")
            
            # Vérifier l'intégrité
            cursor.execute("SELECT pg_check_visible('public')")
            
        logger.info("Optimisation de la base de données terminée")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation de la base de données: {str(e)}")
        raise

@shared_task
def send_health_report():
    """
    Envoie un rapport de santé par email aux administrateurs
    """
    try:
        from django.contrib.auth.models import User
        from .email_tasks import send_template_email
        
        # Récupérer le statut de santé
        health_status = cache.get('system_health_status')
        if not health_status:
            health_status = check_scheduler.delay()
            health_status = health_status.get()
        
        # Préparer le contexte pour l'email
        context = {
            'health_status': health_status,
            'timestamp': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'site_name': getattr(settings, 'SITE_NAME', 'CSIG Website'),
        }
        
        # Envoyer le rapport aux administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin_user in admin_users:
            if admin_user.email:
                send_template_email.delay(
                    template_name='health_report',
                    context=context,
                    to_email=admin_user.email,
                    priority=3
                )
        
        logger.info(f"Rapport de santé envoyé à {admin_users.count()} administrateurs")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du rapport de santé: {str(e)}")
        raise

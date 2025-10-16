"""
Signaux pour l'application jobs
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import EmailTemplate, EmailQueue, NewsletterLog
from .tasks import process_email_queue
from .utils import CacheManager

logger = logging.getLogger(__name__)

# Signaux pour EmailTemplate
@receiver(post_save, sender=EmailTemplate)
def email_template_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un template d'email
    """
    try:
        if created:
            logger.info(f"Nouveau template d'email créé: {instance.name}")
        else:
            logger.info(f"Template d'email modifié: {instance.name}")
        
        # Effacer le cache des templates
        cache.delete(f'email_template_{instance.name}')
        cache.delete('email_templates_list')
        
        # Mettre à jour les statistiques
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal email_template_saved: {str(e)}")

@receiver(post_delete, sender=EmailTemplate)
def email_template_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un template d'email
    """
    try:
        logger.info(f"Template d'email supprimé: {instance.name}")
        
        # Effacer le cache des templates
        cache.delete(f'email_template_{instance.name}')
        cache.delete('email_templates_list')
        
        # Mettre à jour les statistiques
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal email_template_deleted: {str(e)}")

@receiver(pre_save, sender=EmailTemplate)
def email_template_pre_save(sender, instance, **kwargs):
    """
    Signal déclenché avant la sauvegarde d'un template d'email
    """
    try:
        # Validation personnalisée si nécessaire
        if instance.pk:  # Modification d'un template existant
            old_instance = EmailTemplate.objects.get(pk=instance.pk)
            if old_instance.name != instance.name:
                logger.info(f"Renommage du template: {old_instance.name} -> {instance.name}")
        
    except EmailTemplate.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Erreur dans le signal email_template_pre_save: {str(e)}")

# Signaux pour EmailQueue
@receiver(post_save, sender=EmailQueue)
def email_queue_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un email en file d'attente
    """
    try:
        if created:
            logger.info(f"Nouvel email ajouté à la file d'attente: {instance.id} pour {instance.to_email}")
            
            # Si l'email est en attente et n'est pas programmé, le traiter immédiatement
            if instance.status == 'pending' and not instance.scheduled_at:
                process_email_queue.delay()
        
        # Mettre à jour les statistiques
        cache.delete('email_queue_stats')
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal email_queue_saved: {str(e)}")

@receiver(post_delete, sender=EmailQueue)
def email_queue_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un email en file d'attente
    """
    try:
        logger.info(f"Email supprimé de la file d'attente: {instance.id}")
        
        # Mettre à jour les statistiques
        cache.delete('email_queue_stats')
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal email_queue_deleted: {str(e)}")

@receiver(pre_save, sender=EmailQueue)
def email_queue_pre_save(sender, instance, **kwargs):
    """
    Signal déclenché avant la sauvegarde d'un email en file d'attente
    """
    try:
        if instance.pk:  # Modification d'un email existant
            old_instance = EmailQueue.objects.get(pk=instance.pk)
            
            # Si le statut change de 'pending' à 'sent', enregistrer la date d'envoi
            if old_instance.status == 'pending' and instance.status == 'sent' and not instance.sent_at:
                instance.sent_at = timezone.now()
                logger.info(f"Email {instance.id} marqué comme envoyé à {instance.sent_at}")
            
            # Si le statut change à 'failed', enregistrer le nombre de tentatives
            if old_instance.status != 'failed' and instance.status == 'failed':
                logger.warning(f"Email {instance.id} marqué comme échoué (tentative {instance.retry_count + 1})")
        
    except EmailQueue.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Erreur dans le signal email_queue_pre_save: {str(e)}")

# Signaux pour NewsletterLog
@receiver(post_save, sender=NewsletterLog)
def newsletter_log_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un log de newsletter
    """
    try:
        if created:
            logger.info(f"Nouveau log de newsletter créé: {instance.id} pour {instance.subscriber.email}")
        else:
            logger.info(f"Log de newsletter mis à jour: {instance.id} - Statut: {instance.status}")
        
        # Mettre à jour les statistiques
        cache.delete('newsletter_logs_stats')
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_log_saved: {str(e)}")

@receiver(post_delete, sender=NewsletterLog)
def newsletter_log_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un log de newsletter
    """
    try:
        logger.info(f"Log de newsletter supprimé: {instance.id}")
        
        # Mettre à jour les statistiques
        cache.delete('newsletter_logs_stats')
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_log_deleted: {str(e)}")

@receiver(pre_save, sender=NewsletterLog)
def newsletter_log_pre_save(sender, instance, **kwargs):
    """
    Signal déclenché avant la sauvegarde d'un log de newsletter
    """
    try:
        if instance.pk:  # Modification d'un log existant
            old_instance = NewsletterLog.objects.get(pk=instance.pk)
            
            # Si le statut change à 'sent', enregistrer la date d'envoi
            if old_instance.status != 'sent' and instance.status == 'sent' and not instance.sent_at:
                instance.sent_at = timezone.now()
                logger.info(f"Log de newsletter {instance.id} marqué comme envoyé à {instance.sent_at}")
            
            # Si le statut change à 'opened', enregistrer la date d'ouverture
            if old_instance.status != 'opened' and instance.status == 'opened' and not instance.opened_at:
                instance.opened_at = timezone.now()
                logger.info(f"Log de newsletter {instance.id} marqué comme ouvert à {instance.opened_at}")
            
            # Si le statut change à 'clicked', enregistrer la date de clic
            if old_instance.status != 'clicked' and instance.status == 'clicked' and not instance.clicked_at:
                instance.clicked_at = timezone.now()
                logger.info(f"Log de newsletter {instance.id} marqué comme cliqué à {instance.clicked_at}")
            
            # Si le statut change à 'failed', enregistrer le nombre de tentatives
            if old_instance.status != 'failed' and instance.status == 'failed':
                logger.warning(f"Log de newsletter {instance.id} marqué comme échoué (tentative {instance.retry_count + 1})")
        
    except NewsletterLog.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_log_pre_save: {str(e)}")

# Signaux pour les modèles de content_management
@receiver(post_save, sender='content_management.NewsletterCampaign')
def newsletter_campaign_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'une campagne de newsletter
    """
    try:
        if created:
            logger.info(f"Nouvelle campagne de newsletter créée: {instance.title}")
        else:
            logger.info(f"Campagne de newsletter modifiée: {instance.title}")
        
        # Effacer le cache des campagnes
        cache.delete('newsletter_campaigns_list')
        cache.delete(f'newsletter_campaign_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_campaign_saved: {str(e)}")

@receiver(post_delete, sender='content_management.NewsletterCampaign')
def newsletter_campaign_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'une campagne de newsletter
    """
    try:
        logger.info(f"Campagne de newsletter supprimée: {instance.title}")
        
        # Effacer le cache des campagnes
        cache.delete('newsletter_campaigns_list')
        cache.delete(f'newsletter_campaign_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_campaign_deleted: {str(e)}")

@receiver(post_save, sender='content_management.Newsletter')
def newsletter_subscriber_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un abonné à la newsletter
    """
    try:
        if created:
            logger.info(f"Nouvel abonné à la newsletter: {instance.email}")
        else:
            logger.info(f"Abonné à la newsletter modifié: {instance.email}")
        
        # Effacer le cache des abonnés
        cache.delete('newsletter_subscribers_list')
        cache.delete(f'newsletter_subscriber_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_subscriber_saved: {str(e)}")

@receiver(post_delete, sender='content_management.Newsletter')
def newsletter_subscriber_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un abonné à la newsletter
    """
    try:
        logger.info(f"Abonné à la newsletter supprimé: {instance.email}")
        
        # Effacer le cache des abonnés
        cache.delete('newsletter_subscribers_list')
        cache.delete(f'newsletter_subscriber_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal newsletter_subscriber_deleted: {str(e)}")

# Signaux pour les tâches Celery
@receiver(post_save, sender='django_celery_results.TaskResult')
def task_result_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un résultat de tâche Celery
    """
    try:
        if created:
            logger.info(f"Nouveau résultat de tâche: {instance.task_id} - {instance.task_name}")
        else:
            logger.info(f"Résultat de tâche mis à jour: {instance.task_id} - Statut: {instance.status}")
        
        # Effacer le cache des tâches
        cache.delete('celery_tasks_list')
        cache.delete(f'celery_task_{instance.task_id}')
        
        # Mettre à jour les statistiques
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal task_result_saved: {str(e)}")

@receiver(post_delete, sender='django_celery_results.TaskResult')
def task_result_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un résultat de tâche Celery
    """
    try:
        logger.info(f"Résultat de tâche supprimé: {instance.task_id}")
        
        # Effacer le cache des tâches
        cache.delete('celery_tasks_list')
        cache.delete(f'celery_task_{instance.task_id}')
        
        # Mettre à jour les statistiques
        CacheManager.set_cached_performance_metrics(
            CacheManager.get_cached_performance_metrics() or {}
        )
        
    except Exception as e:
        logger.error(f"Erreur dans le signal task_result_deleted: {str(e)}")

# Signaux pour les utilisateurs Django
@receiver(post_save, sender='auth.User')
def user_saved(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un utilisateur Django
    """
    try:
        if created:
            logger.info(f"Nouvel utilisateur créé: {instance.username}")
        else:
            logger.info(f"Utilisateur modifié: {instance.username}")
        
        # Effacer le cache des utilisateurs si nécessaire
        cache.delete('users_list')
        cache.delete(f'user_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal user_saved: {str(e)}")

@receiver(post_delete, sender='auth.User')
def user_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'un utilisateur Django
    """
    try:
        logger.info(f"Utilisateur supprimé: {instance.username}")
        
        # Effacer le cache des utilisateurs
        cache.delete('users_list')
        cache.delete(f'user_{instance.id}')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal user_deleted: {str(e)}")

# Signaux pour les sessions Django
@receiver(post_delete, sender='django.contrib.sessions.models.Session')
def session_deleted(sender, instance, **kwargs):
    """
    Signal déclenché après la suppression d'une session Django
    """
    try:
        logger.debug(f"Session supprimée: {instance.session_key}")
        
        # Effacer le cache des sessions si nécessaire
        cache.delete('sessions_count')
        
    except Exception as e:
        logger.error(f"Erreur dans le signal session_deleted: {str(e)}")

# Signaux personnalisés pour les événements métier
from django.dispatch import Signal

# Signal déclenché quand un email est envoyé avec succès
email_sent_successfully = Signal()

# Signal déclenché quand un email échoue
email_sent_failed = Signal()

# Signal déclenché quand une newsletter est envoyée avec succès
newsletter_sent_successfully = Signal()

# Signal déclenché quand une newsletter échoue
newsletter_sent_failed = Signal()

# Signal déclenché quand une tâche est terminée avec succès
task_completed_successfully = Signal()

# Signal déclenché quand une tâche échoue
task_completed_failed = Signal()

# Signal déclenché quand la santé du système change
system_health_changed = Signal()

# Gestionnaires pour les signaux personnalisés
@receiver(email_sent_successfully)
def handle_email_sent_successfully(sender, email_id, recipient, **kwargs):
    """
    Gestionnaire pour le signal email_sent_successfully
    """
    try:
        logger.info(f"Email {email_id} envoyé avec succès à {recipient}")
        
        # Mettre à jour les statistiques
        cache.delete('email_sent_count')
        
        # Déclencher d'autres actions si nécessaire
        # Par exemple, envoyer une notification, mettre à jour un dashboard, etc.
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire email_sent_successfully: {str(e)}")

@receiver(email_sent_failed)
def handle_email_sent_failed(sender, email_id, recipient, error_message, **kwargs):
    """
    Gestionnaire pour le signal email_sent_failed
    """
    try:
        logger.error(f"Échec de l'envoi de l'email {email_id} à {recipient}: {error_message}")
        
        # Mettre à jour les statistiques
        cache.delete('email_failed_count')
        
        # Déclencher d'autres actions si nécessaire
        # Par exemple, envoyer une alerte, notifier l'administrateur, etc.
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire email_sent_failed: {str(e)}")

@receiver(newsletter_sent_successfully)
def handle_newsletter_sent_successfully(sender, campaign_id, subscriber_email, **kwargs):
    """
    Gestionnaire pour le signal newsletter_sent_successfully
    """
    try:
        logger.info(f"Newsletter de la campagne {campaign_id} envoyée avec succès à {subscriber_email}")
        
        # Mettre à jour les statistiques
        cache.delete('newsletter_sent_count')
        
        # Déclencher d'autres actions si nécessaire
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire newsletter_sent_successfully: {str(e)}")

@receiver(newsletter_sent_failed)
def handle_newsletter_sent_failed(sender, campaign_id, subscriber_email, error_message, **kwargs):
    """
    Gestionnaire pour le signal newsletter_sent_failed
    """
    try:
        logger.error(f"Échec de l'envoi de la newsletter de la campagne {campaign_id} à {subscriber_email}: {error_message}")
        
        # Mettre à jour les statistiques
        cache.delete('newsletter_failed_count')
        
        # Déclencher d'autres actions si nécessaire
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire newsletter_sent_failed: {str(e)}")

@receiver(task_completed_successfully)
def handle_task_completed_successfully(sender, task_id, task_name, **kwargs):
    """
    Gestionnaire pour le signal task_completed_successfully
    """
    try:
        logger.info(f"Tâche {task_id} ({task_name}) terminée avec succès")
        
        # Mettre à jour les statistiques
        cache.delete('tasks_completed_count')
        
        # Déclencher d'autres actions si nécessaire
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire task_completed_successfully: {str(e)}")

@receiver(task_completed_failed)
def handle_task_completed_failed(sender, task_id, task_name, error_message, **kwargs):
    """
    Gestionnaire pour le signal task_completed_failed
    """
    try:
        logger.error(f"Échec de la tâche {task_id} ({task_name}): {error_message}")
        
        # Mettre à jour les statistiques
        cache.delete('tasks_failed_count')
        
        # Déclencher d'autres actions si nécessaire
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire task_completed_failed: {str(e)}")

@receiver(system_health_changed)
def handle_system_health_changed(sender, old_status, new_status, details, **kwargs):
    """
    Gestionnaire pour le signal system_health_changed
    """
    try:
        logger.info(f"Changement de santé du système: {old_status} -> {new_status}")
        
        # Mettre à jour le cache de santé
        cache.set('system_health_status', details, timeout=300)
        
        # Si la santé se dégrade, déclencher des alertes
        if new_status in ['warning', 'critical']:
            logger.warning(f"Alerte de santé du système: {new_status}")
            # Déclencher des actions d'alerte si nécessaire
        
    except Exception as e:
        logger.error(f"Erreur dans le gestionnaire system_health_changed: {str(e)}")

# Fonction pour déclencher les signaux personnalisés
def trigger_email_sent_successfully(email_id, recipient):
    """Déclenche le signal email_sent_successfully"""
    email_sent_successfully.send(
        sender=EmailQueue,
        email_id=email_id,
        recipient=recipient
    )

def trigger_email_sent_failed(email_id, recipient, error_message):
    """Déclenche le signal email_sent_failed"""
    email_sent_failed.send(
        sender=EmailQueue,
        email_id=email_id,
        recipient=recipient,
        error_message=error_message
    )

def trigger_newsletter_sent_successfully(campaign_id, subscriber_email):
    """Déclenche le signal newsletter_sent_successfully"""
    newsletter_sent_successfully.send(
        sender=NewsletterLog,
        campaign_id=campaign_id,
        subscriber_email=subscriber_email
    )

def trigger_newsletter_sent_failed(campaign_id, subscriber_email, error_message):
    """Déclenche le signal newsletter_sent_failed"""
    newsletter_sent_failed.send(
        sender=NewsletterLog,
        campaign_id=campaign_id,
        subscriber_email=subscriber_email,
        error_message=error_message
    )

def trigger_task_completed_successfully(task_id, task_name):
    """Déclenche le signal task_completed_successfully"""
    task_completed_successfully.send(
        sender='django_celery_results.TaskResult',
        task_id=task_id,
        task_name=task_name
    )

def trigger_task_completed_failed(task_id, task_name, error_message):
    """Déclenche le signal task_completed_failed"""
    task_completed_failed.send(
        sender='django_celery_results.TaskResult',
        task_id=task_id,
        task_name=task_name,
        error_message=error_message
    )

def trigger_system_health_changed(old_status, new_status, details):
    """Déclenche le signal system_health_changed"""
    system_health_changed.send(
        sender='jobs.SystemMonitor',
        old_status=old_status,
        new_status=new_status,
        details=details
    )

"""
Tâches Celery spécifiques pour la gestion des newsletters
"""
import logging
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from content_management.models import Newsletter, NewsletterCampaign
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_newsletter_email(self, campaign_id, subscriber_email, subscriber_name=None):
    """
    Envoie un email de newsletter à un abonné spécifique
    """
    try:
        campaign = NewsletterCampaign.objects.get(id=campaign_id)
        subscriber = Newsletter.objects.get(email=subscriber_email)
        
        # Préparer le contexte pour le template
        context = {
            'campaign': campaign,
            'subscriber': subscriber,
            'subscriber_name': subscriber_name or subscriber.name or 'Abonné',
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.id}/",
            'current_date': timezone.now().strftime('%d/%m/%Y'),
        }
        
        # Rendre le template HTML
        html_content = render_to_string(
            campaign.template_name or 'emails/newsletter_default.html',
            context
        )
        
        # Rendre le template texte
        text_content = render_to_string(
            campaign.template_name.replace('.html', '.txt') if campaign.template_name else 'emails/newsletter_default.txt',
            context
        )
        
        # Créer l'email
        email = EmailMessage(
            subject=campaign.subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        
        email.content_subtype = "html"
        email.attach_alternative(text_content, "text/plain")
        
        # Envoyer l'email
        email.send()
        
        # Mettre à jour les statistiques
        campaign.sent_count += 1
        campaign.save()
        
        logger.info(f"Email envoyé avec succès à {subscriber_email} pour la campagne {campaign.title}")
        return True
        
    except NewsletterCampaign.DoesNotExist:
        logger.error(f"Campagne {campaign_id} non trouvée")
        raise
    except Newsletter.DoesNotExist:
        logger.error(f"Abonné {subscriber_email} non trouvé")
        raise
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi à {subscriber_email}: {str(exc)}")
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_bulk_newsletter(self, campaign_id):
    """
    Envoie une newsletter en masse à tous les abonnés actifs
    """
    try:
        campaign = NewsletterCampaign.objects.get(id=campaign_id)
        
        if not campaign.can_be_sent:
            logger.warning(f"Campagne {campaign.title} ne peut pas être envoyée")
            return False
        
        # Marquer la campagne comme en cours d'envoi
        campaign.status = 'sending'
        campaign.started_at = timezone.now()
        campaign.save()
        
        # Récupérer tous les abonnés actifs
        subscribers = Newsletter.objects.filter(is_active=True)
        
        if campaign.target_language:
            subscribers = subscribers.filter(language=campaign.target_language)
        
        if campaign.target_active_only:
            subscribers = subscribers.filter(is_active=True)
        
        total_subscribers = subscribers.count()
        sent_count = 0
        failed_count = 0
        
        logger.info(f"Début de l'envoi de la campagne {campaign.title} à {total_subscribers} abonnés")
        
        # Envoyer les emails par petits lots pour éviter la surcharge
        batch_size = 50
        for i in range(0, total_subscribers, batch_size):
            batch = subscribers[i:i + batch_size]
            
            for subscriber in batch:
                try:
                    # Créer une tâche individuelle pour chaque email
                    send_newsletter_email.delay(campaign_id, subscriber.email, subscriber.name)
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi à {subscriber.email}: {str(e)}")
                    failed_count += 1
            
            # Pause entre les lots pour éviter la surcharge
            if i + batch_size < total_subscribers:
                import time
                time.sleep(1)
        
        # Mettre à jour les statistiques finales
        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.status = 'completed'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        logger.info(f"Campagne {campaign.title} terminée: {sent_count} envoyés, {failed_count} échecs")
        return True
        
    except NewsletterCampaign.DoesNotExist:
        logger.error(f"Campagne {campaign_id} non trouvée")
        raise
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi en masse de la campagne {campaign_id}: {str(exc)}")
        # Marquer la campagne comme échouée
        try:
            campaign.status = 'failed'
            campaign.save()
        except:
            pass
        raise self.retry(exc=exc, countdown=300 * (2 ** self.request.retries))

@shared_task
def send_scheduled_newsletter():
    """
    Tâche programmée pour envoyer les newsletters planifiées
    """
    try:
        now = timezone.now()
        scheduled_campaigns = NewsletterCampaign.objects.filter(
            status='scheduled',
            scheduled_at__lte=now
        )
        
        for campaign in scheduled_campaigns:
            logger.info(f"Envoi de la campagne planifiée: {campaign.title}")
            send_bulk_newsletter.delay(campaign.id)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des newsletters planifiées: {str(e)}")

@shared_task
def cleanup_old_newsletter_logs():
    """
    Nettoie les anciens logs de newsletter (placeholder)
    """
    try:
        # Supprimer les campagnes terminées depuis plus de 30 jours
        cutoff_date = timezone.now() - timedelta(days=30)
        old_campaigns = NewsletterCampaign.objects.filter(
            status__in=['completed', 'failed'],
            completed_at__lt=cutoff_date
        )
        
        deleted_count = old_campaigns.count()
        old_campaigns.delete()
        
        logger.info(f"Nettoyage terminé: {deleted_count} anciennes campagnes supprimées")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des logs: {str(e)}")

@shared_task
def test_email_connection():
    """
    Teste la connexion email pour vérifier la configuration
    """
    try:
        from django.core.mail import get_connection
        
        connection = get_connection()
        connection.open()
        connection.close()
        
        logger.info("Test de connexion email réussi")
        return True
        
    except Exception as e:
        logger.error(f"Échec du test de connexion email: {str(e)}")
        return False

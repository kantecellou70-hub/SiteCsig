"""
Tâches Celery pour la gestion des emails généraux
"""
import logging
from celery import shared_task
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import EmailQueue, EmailTemplate
from datetime import datetime, timedelta
from django.db import models

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_from_queue(self, email_id):
    """
    Envoie un email depuis la file d'attente
    """
    try:
        email_queue = EmailQueue.objects.get(id=email_id)
        
        if not email_queue.can_be_sent():
            logger.warning(f"Email {email_id} ne peut pas être envoyé")
            return False
        
        # Marquer comme en cours de traitement
        email_queue.mark_as_processing()
        
        # Créer l'email
        email = EmailMessage(
            subject=email_queue.subject,
            body=email_queue.html_content,
            from_email=email_queue.from_email,
            to=[email_queue.to_email],
            reply_to=[email_queue.from_email],
        )
        
        email.content_subtype = "html"
        if email_queue.text_content:
            email.attach_alternative(email_queue.text_content, "text/plain")
        
        # Envoyer l'email
        email.send()
        
        # Marquer comme envoyé
        email_queue.mark_as_sent()
        
        logger.info(f"Email {email_id} envoyé avec succès à {email_queue.to_email}")
        return True
        
    except EmailQueue.DoesNotExist:
        logger.error(f"Email {email_id} non trouvé dans la file d'attente")
        raise
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi de l'email {email_id}: {str(exc)}")
        
        try:
            email_queue.mark_as_failed(str(exc))
        except:
            pass
        
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def process_email_queue():
    """
    Traite la file d'attente des emails
    """
    try:
        # Récupérer les emails prêts à être envoyés
        pending_emails = EmailQueue.objects.filter(
            status='pending'
        ).filter(
            models.Q(scheduled_at__isnull=True) | 
            models.Q(scheduled_at__lte=timezone.now())
        ).order_by('-priority', 'created_at')[:50]  # Traiter par lots de 50
        
        for email_queue in pending_emails:
            try:
                send_email_from_queue.delay(email_queue.id)
            except Exception as e:
                logger.error(f"Erreur lors du lancement de l'envoi de l'email {email_queue.id}: {str(e)}")
        
        logger.info(f"File d'attente traitée: {len(pending_emails)} emails mis en file d'attente")
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la file d'attente: {str(e)}")

@shared_task
def cleanup_failed_emails():
    """
    Nettoie les emails échoués après un certain délai
    """
    try:
        # Supprimer les emails échoués depuis plus de 7 jours
        cutoff_date = timezone.now() - timedelta(days=7)
        failed_emails = EmailQueue.objects.filter(
            status='failed',
            updated_at__lt=cutoff_date
        )
        
        deleted_count = failed_emails.count()
        failed_emails.delete()
        
        logger.info(f"Nettoyage terminé: {deleted_count} emails échoués supprimés")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des emails échoués: {str(e)}")

@shared_task
def retry_failed_emails():
    """
    Remet en file d'attente les emails échoués qui peuvent être retentés
    """
    try:
        # Récupérer les emails échoués qui peuvent être retentés
        failed_emails = EmailQueue.objects.filter(
            status='failed',
            retry_count__lt=models.F('max_retries')
        )
        
        retry_count = 0
        for email_queue in failed_emails:
            if email_queue.retry():
                retry_count += 1
        
        logger.info(f"Retry terminé: {retry_count} emails remis en file d'attente")
        
    except Exception as e:
        logger.error(f"Erreur lors du retry des emails échoués: {str(e)}")

@shared_task
def send_template_email(template_name, context, to_email, from_email=None, priority=2):
    """
    Envoie un email en utilisant un template
    """
    try:
        template = EmailTemplate.objects.get(name=template_name, is_active=True)
        
        # Rendre le contenu du template
        subject = template.get_subject(context)
        html_content = template.get_html_content(context)
        text_content = template.get_text_content(context)
        
        # Créer l'email dans la file d'attente
        email_queue = EmailQueue.objects.create(
            to_email=to_email,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            priority=priority
        )
        
        # Lancer l'envoi
        send_email_from_queue.delay(email_queue.id)
        
        logger.info(f"Email template '{template_name}' mis en file d'attente pour {to_email}")
        return email_queue.id
        
    except EmailTemplate.DoesNotExist:
        logger.error(f"Template '{template_name}' non trouvé ou inactif")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'email template: {str(e)}")
        raise

@shared_task
def send_bulk_template_emails(template_name, context_list, from_email=None, priority=2):
    """
    Envoie des emails en masse en utilisant un template
    """
    try:
        template = EmailTemplate.objects.get(name=template_name, is_active=True)
        
        created_count = 0
        for context, to_email in context_list:
            try:
                # Rendre le contenu du template
                subject = template.get_subject(context)
                html_content = template.get_html_content(context)
                text_content = template.get_text_content(context)
                
                # Créer l'email dans la file d'attente
                EmailQueue.objects.create(
                    to_email=to_email,
                    from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    priority=priority
                )
                
                created_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'email pour {to_email}: {str(e)}")
        
        logger.info(f"Bulk emails terminé: {created_count} emails créés dans la file d'attente")
        return created_count
        
    except EmailTemplate.DoesNotExist:
        logger.error(f"Template '{template_name}' non trouvé ou inactif")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création des emails en masse: {str(e)}")
        raise

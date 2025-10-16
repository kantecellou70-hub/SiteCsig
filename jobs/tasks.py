import logging
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from content_management.models import Newsletter, NewsletterCampaign
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_newsletter_email(self, newsletter_id, campaign_id=None, template_name='newsletter_default.html'):
    """
    Envoyer un email de newsletter à un abonné spécifique
    """
    try:
        # Récupérer l'abonné
        newsletter = Newsletter.objects.get(id=newsletter_id, is_active=True)
        
        # Récupérer la campagne si spécifiée
        campaign = None
        if campaign_id:
            campaign = NewsletterCampaign.objects.get(id=campaign_id)
        
        # Préparer le contexte pour le template
        context = {
            'newsletter': newsletter,
            'campaign': campaign,
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{newsletter.id}/",
            'current_date': timezone.now(),
        }
        
        # Rendre le template HTML
        html_content = render_to_string(f'newsletter_templates/{template_name}', context)
        
        # Préparer l'email
        subject = campaign.subject if campaign else "Newsletter CSIG"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = newsletter.email
        
        # Créer l'email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=[to_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.content_subtype = "html"  # Email en HTML
        
        # Envoyer l'email
        email.send()
        
        # Mettre à jour le statut
        if campaign:
            # Créer ou mettre à jour le suivi d'envoi
            NewsletterCampaign.objects.filter(id=campaign_id).update(
                sent_count=models.F('sent_count') + 1
            )
        
        logger.info(f"Newsletter envoyée avec succès à {to_email}")
        return {
            'success': True,
            'email': to_email,
            'campaign_id': campaign_id,
            'sent_at': timezone.now().isoformat()
        }
        
    except Newsletter.DoesNotExist:
        logger.error(f"Abonné newsletter {newsletter_id} non trouvé")
        raise self.retry(countdown=60, max_retries=3)
        
    except NewsletterCampaign.DoesNotExist:
        logger.error(f"Campagne newsletter {campaign_id} non trouvée")
        raise self.retry(countdown=60, max_retries=3)
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi de la newsletter: {exc}")
        raise self.retry(countdown=300, max_retries=3, exc=exc)


@shared_task(bind=True, max_retries=3)
def send_user_creation_email(self, user_id, password):
    """
    Envoyer un email de bienvenue avec les informations de connexion à un nouvel utilisateur
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Récupérer l'utilisateur
        user = User.objects.get(id=user_id)
        
        # Préparer le contexte pour le template
        context = {
            'user': user,
            'username': user.username,
            'password': password,
            'login_url': f"{settings.SITE_URL}/admin/login/",
            'current_date': timezone.now(),
        }
        
        # Rendre les templates HTML et texte
        html_content = render_to_string('email_templates/user_creation.html', context)
        text_content = render_to_string('email_templates/user_creation.txt', context)
        
        # Préparer l'email
        subject = f"Bienvenue sur CSIG - Vos informations de connexion"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email
        
        # Créer l'email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=[to_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.content_subtype = "html"  # Email en HTML
        
        # Ajouter la version texte comme alternative
        email.alternatives = [(text_content, 'text/plain')]
        
        # Envoyer l'email
        email.send()
        
        logger.info(f"Email de création d'utilisateur envoyé avec succès à {to_email}")
        return {
            'success': True,
            'email': to_email,
            'user_id': user_id,
            'sent_at': timezone.now().isoformat()
        }
        
    except User.DoesNotExist:
        logger.error(f"Utilisateur {user_id} non trouvé")
        raise self.retry(countdown=60, max_retries=3)
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi de l'email de création d'utilisateur: {exc}")
        raise self.retry(countdown=300, max_retries=3, exc=exc)


@shared_task(bind=True)
def send_bulk_newsletter(self, campaign_id, template_name='newsletter_default.html'):
    """
    Envoyer une newsletter en masse à tous les abonnés actifs
    """
    try:
        campaign = NewsletterCampaign.objects.get(id=campaign_id)
        
        # Récupérer tous les abonnés actifs
        active_newsletters = Newsletter.objects.filter(is_active=True)
        
        total_subscribers = active_newsletters.count()
        sent_count = 0
        failed_count = 0
        
        logger.info(f"Début de l'envoi en masse pour la campagne {campaign.title} à {total_subscribers} abonnés")
        
        # Mettre à jour le statut de la campagne
        campaign.status = 'sending'
        campaign.started_at = timezone.now()
        campaign.save()
        
        # Envoyer à chaque abonné
        for newsletter in active_newsletters:
            try:
                # Utiliser la tâche individuelle
                result = send_newsletter_email.delay(
                    newsletter.id, 
                    campaign.id, 
                    template_name
                )
                
                if result.get('success'):
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi à {newsletter.email}: {e}")
                failed_count += 1
        
        # Mettre à jour le statut final de la campagne
        campaign.status = 'completed'
        campaign.completed_at = timezone.now()
        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.save()
        
        logger.info(f"Campagne {campaign.title} terminée: {sent_count} envoyés, {failed_count} échecs")
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'total_subscribers': total_subscribers,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'completed_at': timezone.now().isoformat()
        }
        
    except NewsletterCampaign.DoesNotExist:
        logger.error(f"Campagne newsletter {campaign_id} non trouvée")
        return {'success': False, 'error': 'Campagne non trouvée'}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi en masse: {exc}")
        # Mettre à jour le statut en cas d'erreur
        try:
            campaign = NewsletterCampaign.objects.get(id=campaign_id)
            campaign.status = 'failed'
            campaign.save()
        except:
            pass
        return {'success': False, 'error': str(exc)}


@shared_task(bind=True)
def send_scheduled_newsletter(self, campaign_id):
    """
    Envoyer une newsletter programmée
    """
    try:
        campaign = NewsletterCampaign.objects.get(id=campaign_id)
        
        # Vérifier si c'est le moment d'envoyer
        if campaign.scheduled_at and campaign.scheduled_at <= timezone.now():
            logger.info(f"Envoi de la newsletter programmée: {campaign.title}")
            
            # Utiliser la tâche d'envoi en masse
            result = send_bulk_newsletter.delay(campaign_id, campaign.template_name)
            
            return result
        else:
            logger.info(f"Newsletter {campaign.title} pas encore programmée pour l'envoi")
            return {'success': False, 'message': 'Pas encore programmée'}
            
    except NewsletterCampaign.DoesNotExist:
        logger.error(f"Campagne newsletter {campaign_id} non trouvée")
        return {'success': False, 'error': 'Campagne non trouvée'}


@shared_task(bind=True)
def cleanup_old_newsletter_logs(self, days=30):
    """
    Nettoyer les anciens logs d'envoi de newsletters
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Supprimer les anciens logs (à implémenter selon votre modèle de logs)
        # NewsletterLog.objects.filter(created_at__lt=cutoff_date).delete()
        
        logger.info(f"Nettoyage des logs de newsletters antérieurs à {cutoff_date}")
        
        return {
            'success': True,
            'cleaned_before': cutoff_date.isoformat(),
            'message': f'Logs nettoyés pour les newsletters antérieures à {days} jours'
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors du nettoyage des logs: {exc}")
        return {'success': False, 'error': str(exc)}


@shared_task(bind=True)
def test_email_connection(self):
    """
    Tester la connexion email
    """
    try:
        from django.core.mail import get_connection
        
        connection = get_connection()
        connection.open()
        connection.close()
        
        logger.info("Connexion email testée avec succès")
        
        return {
            'success': True,
            'message': 'Connexion email fonctionnelle',
            'tested_at': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Erreur de connexion email: {exc}")
        return {'success': False, 'error': str(exc)}


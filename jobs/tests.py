"""
Tests pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from .models import NewsletterLog, EmailTemplate, EmailQueue
from .tasks import (
    send_newsletter_email, send_bulk_newsletter,
    cleanup_old_newsletter_logs, test_email_connection
)
from .email_tasks import (
    send_email_from_queue, process_email_queue,
    cleanup_failed_emails, retry_failed_emails
)

class NewsletterLogModelTest(TestCase):
    """Tests pour le modèle NewsletterLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des modèles de test (simulés)
        self.campaign = MagicMock()
        self.campaign.id = 1
        self.campaign.title = "Test Campaign"
        
        self.subscriber = MagicMock()
        self.subscriber.id = 1
        self.subscriber.email = "subscriber@example.com"
    
    def test_newsletter_log_creation(self):
        """Test de création d'un log de newsletter"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        self.assertEqual(log.status, 'pending')
        self.assertEqual(log.retry_count, 0)
        self.assertIsNotNone(log.created_at)
    
    def test_mark_as_sent(self):
        """Test du marquage comme envoyé"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        log.mark_as_sent()
        
        self.assertEqual(log.status, 'sent')
        self.assertIsNotNone(log.sent_at)
    
    def test_mark_as_failed(self):
        """Test du marquage comme échoué"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        error_message = "Test error"
        log.mark_as_failed(error_message)
        
        self.assertEqual(log.status, 'failed')
        self.assertEqual(log.error_message, error_message)
        self.assertEqual(log.retry_count, 1)

class EmailTemplateModelTest(TestCase):
    """Tests pour le modèle EmailTemplate"""
    
    def setUp(self):
        self.template = EmailTemplate.objects.create(
            name='test_template',
            subject_template='Hello {{ name }}!',
            html_template='<h1>Hello {{ name }}!</h1>',
            text_template='Hello {{ name }}!'
        )
    
    def test_template_creation(self):
        """Test de création d'un template"""
        self.assertEqual(self.template.name, 'test_template')
        self.assertTrue(self.template.is_active)
    
    def test_get_subject(self):
        """Test du rendu du sujet"""
        context = {'name': 'John'}
        subject = self.template.get_subject(context)
        self.assertEqual(subject, 'Hello John!')
    
    def test_get_html_content(self):
        """Test du rendu du contenu HTML"""
        context = {'name': 'John'}
        html_content = self.template.get_html_content(context)
        self.assertEqual(html_content, '<h1>Hello John!</h1>')
    
    def test_get_text_content(self):
        """Test du rendu du contenu texte"""
        context = {'name': 'John'}
        text_content = self.template.get_text_content(context)
        self.assertEqual(text_content, 'Hello John!')

class EmailQueueModelTest(TestCase):
    """Tests pour le modèle EmailQueue"""
    
    def setUp(self):
        self.email_queue = EmailQueue.objects.create(
            to_email='test@example.com',
            from_email='noreply@example.com',
            subject='Test Subject',
            html_content='<p>Test content</p>',
            priority=2
        )
    
    def test_email_queue_creation(self):
        """Test de création d'un email en file d'attente"""
        self.assertEqual(self.email_queue.status, 'pending')
        self.assertEqual(self.email_queue.priority, 2)
        self.assertEqual(self.email_queue.retry_count, 0)
    
    def test_can_be_sent(self):
        """Test de la vérification si l'email peut être envoyé"""
        self.assertTrue(self.email_queue.can_be_sent())
        
        # Marquer comme en cours de traitement
        self.email_queue.mark_as_processing()
        self.assertFalse(self.email_queue.can_be_sent())
    
    def test_mark_as_sent(self):
        """Test du marquage comme envoyé"""
        self.email_queue.mark_as_sent()
        
        self.assertEqual(self.email_queue.status, 'sent')
        self.assertIsNotNone(self.email_queue.sent_at)
    
    def test_mark_as_failed(self):
        """Test du marquage comme échoué"""
        error_message = "Test error"
        self.email_queue.mark_as_failed(error_message)
        
        self.assertEqual(self.email_queue.status, 'failed')
        self.assertEqual(self.email_queue.error_message, error_message)
        self.assertEqual(self.email_queue.retry_count, 1)
    
    def test_retry(self):
        """Test de la remise en file d'attente"""
        self.email_queue.mark_as_failed("Test error")
        
        # Premier retry
        self.assertTrue(self.email_queue.retry())
        self.assertEqual(self.email_queue.status, 'pending')
        self.assertEqual(self.email_queue.retry_count, 1)
        
        # Deuxième retry
        self.email_queue.mark_as_failed("Test error")
        self.assertTrue(self.email_queue.retry())
        self.assertEqual(self.email_queue.retry_count, 2)
        
        # Troisième retry
        self.email_queue.mark_as_failed("Test error")
        self.assertTrue(self.email_queue.retry())
        self.assertEqual(self.email_queue.retry_count, 3)
        
        # Quatrième retry (dépassement de la limite)
        self.email_queue.mark_as_failed("Test error")
        self.assertFalse(self.email_queue.retry())

class TasksTest(TestCase):
    """Tests pour les tâches Celery"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('jobs.tasks.EmailMessage')
    @patch('jobs.tasks.render_to_string')
    def test_send_newsletter_email_success(self, mock_render, mock_email_class):
        """Test de l'envoi réussi d'un email de newsletter"""
        # Mock du rendu des templates
        mock_render.side_effect = ['<html>Test</html>', 'Test text']
        
        # Mock de l'email
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        # Mock des modèles
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_campaign_get:
            with patch('jobs.tasks.Newsletter.objects.get') as mock_subscriber_get:
                mock_campaign = MagicMock()
                mock_campaign.id = 1
                mock_campaign.title = "Test Campaign"
                mock_campaign.template_name = None
                mock_campaign_get.return_value = mock_campaign
                
                mock_subscriber = MagicMock()
                mock_subscriber.email = "test@example.com"
                mock_subscriber.name = "Test User"
                mock_subscriber_get.return_value = mock_subscriber
                
                # Exécuter la tâche
                result = send_newsletter_email(1, "test@example.com", "Test User")
                
                # Vérifications
                self.assertTrue(result)
                mock_email.send.assert_called_once()
                self.assertEqual(mock_campaign.sent_count, 1)
    
    @patch('jobs.tasks.NewsletterCampaign.objects.get')
    def test_send_newsletter_email_campaign_not_found(self, mock_get):
        """Test de l'échec quand la campagne n'est pas trouvée"""
        mock_get.side_effect = Exception("Campaign not found")
        
        with self.assertRaises(Exception):
            send_newsletter_email(999, "test@example.com")
    
    @patch('jobs.tasks.Newsletter.objects.get')
    def test_send_newsletter_email_subscriber_not_found(self, mock_get):
        """Test de l'échec quand l'abonné n'est pas trouvé"""
        mock_get.side_effect = Exception("Subscriber not found")
        
        with self.assertRaises(Exception):
            send_newsletter_email(1, "nonexistent@example.com")
    
    @patch('jobs.tasks.send_newsletter_email.delay')
    def test_send_bulk_newsletter(self, mock_send_delay):
        """Test de l'envoi en masse de newsletters"""
        # Mock des modèles
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_campaign_get:
            with patch('jobs.tasks.Newsletter.objects.filter') as mock_subscribers_filter:
                mock_campaign = MagicMock()
                mock_campaign.id = 1
                mock_campaign.title = "Test Campaign"
                mock_campaign.can_be_sent.return_value = True
                mock_campaign_get.return_value = mock_campaign
                
                mock_subscribers = MagicMock()
                mock_subscribers.count.return_value = 2
                mock_subscribers.__iter__.return_value = [
                    MagicMock(email="user1@example.com", name="User 1"),
                    MagicMock(email="user2@example.com", name="User 2")
                ]
                mock_subscribers_filter.return_value = mock_subscribers
                
                # Exécuter la tâche
                result = send_bulk_newsletter(1)
                
                # Vérifications
                self.assertTrue(result)
                self.assertEqual(mock_send_delay.call_count, 2)
                self.assertEqual(mock_campaign.status, 'completed')
    
    def test_cleanup_old_newsletter_logs(self):
        """Test du nettoyage des anciens logs"""
        # Cette tâche est un placeholder, donc on teste juste qu'elle s'exécute
        result = cleanup_old_newsletter_logs()
        self.assertIsNone(result)
    
    @patch('jobs.tasks.get_connection')
    def test_test_email_connection_success(self, mock_get_connection):
        """Test de la vérification de connexion email réussie"""
        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        
        result = test_email_connection()
        
        self.assertTrue(result)
        mock_connection.open.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('jobs.tasks.get_connection')
    def test_test_email_connection_failure(self, mock_get_connection):
        """Test de l'échec de la vérification de connexion email"""
        mock_get_connection.side_effect = Exception("Connection failed")
        
        result = test_email_connection()
        
        self.assertFalse(result)

class EmailTasksTest(TestCase):
    """Tests pour les tâches d'email"""
    
    def setUp(self):
        self.email_queue = EmailQueue.objects.create(
            to_email='test@example.com',
            from_email='noreply@example.com',
            subject='Test Subject',
            html_content='<p>Test content</p>',
            priority=2
        )
    
    @patch('jobs.email_tasks.EmailMessage')
    def test_send_email_from_queue_success(self, mock_email_class):
        """Test de l'envoi réussi d'un email depuis la file d'attente"""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        result = send_email_from_queue(self.email_queue.id)
        
        self.assertTrue(result)
        mock_email.send.assert_called_once()
        
        # Vérifier que l'email a été marqué comme envoyé
        self.email_queue.refresh_from_db()
        self.assertEqual(self.email_queue.status, 'sent')
    
    def test_send_email_from_queue_not_found(self):
        """Test de l'échec quand l'email n'est pas trouvé"""
        with self.assertRaises(Exception):
            send_email_from_queue(999)
    
    def test_process_email_queue(self):
        """Test du traitement de la file d'attente"""
        # Cette tâche lance des sous-tâches, on teste juste qu'elle s'exécute
        result = process_email_queue()
        self.assertIsNone(result)
    
    def test_cleanup_failed_emails(self):
        """Test du nettoyage des emails échoués"""
        # Marquer un email comme échoué
        self.email_queue.mark_as_failed("Test error")
        
        # Exécuter le nettoyage
        result = cleanup_failed_emails()
        self.assertIsNone(result)
    
    def test_retry_failed_emails(self):
        """Test de la remise en file d'attente des emails échoués"""
        # Marquer un email comme échoué
        self.email_queue.mark_as_failed("Test error")
        
        # Exécuter le retry
        result = retry_failed_emails()
        self.assertIsNone(result)
        
        # Vérifier que l'email a été remis en file d'attente
        self.email_queue.refresh_from_db()
        self.assertEqual(self.email_queue.status, 'pending')

class IntegrationTest(TestCase):
    """Tests d'intégration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_full_email_workflow(self):
        """Test du workflow complet d'envoi d'email"""
        # Créer un template
        template = EmailTemplate.objects.create(
            name='test_workflow',
            subject_template='Test for {{ name }}',
            html_template='<p>Hello {{ name }}!</p>',
            text_template='Hello {{ name }}!'
        )
        
        # Créer un email en file d'attente
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Subject',
            html_content='<p>Test content</p>',
            priority=2
        )
        
        # Vérifier l'état initial
        self.assertEqual(email_queue.status, 'pending')
        self.assertEqual(email_queue.retry_count, 0)
        
        # Simuler l'envoi
        email_queue.mark_as_processing()
        self.assertEqual(email_queue.status, 'processing')
        
        # Simuler l'envoi réussi
        email_queue.mark_as_sent()
        self.assertEqual(email_queue.status, 'sent')
        self.assertIsNotNone(email_queue.sent_at)
    
    def test_newsletter_log_workflow(self):
        """Test du workflow complet des logs de newsletter"""
        # Créer un log
        log = NewsletterLog.objects.create(
            campaign=MagicMock(id=1, title="Test Campaign"),
            subscriber=MagicMock(id=1, email="test@example.com"),
            status='pending'
        )
        
        # Vérifier l'état initial
        self.assertEqual(log.status, 'pending')
        self.assertIsNone(log.sent_at)
        
        # Simuler l'envoi
        log.mark_as_sent()
        self.assertEqual(log.status, 'sent')
        self.assertIsNotNone(log.sent_at)
        
        # Simuler l'ouverture
        log.mark_as_opened()
        self.assertEqual(log.status, 'opened')
        self.assertIsNotNone(log.opened_at)
        
        # Simuler le clic
        log.mark_as_clicked()
        self.assertEqual(log.status, 'clicked')
        self.assertIsNotNone(log.clicked_at)

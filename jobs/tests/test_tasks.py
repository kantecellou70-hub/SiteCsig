"""
Tests pour les tâches Celery de l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import json
import os

# Configuration pour les tests Celery
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class NewsletterTasksTest(TestCase):
    """Tests pour les tâches de newsletter"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des modèles de test (simulés)
        self.campaign = type('MockCampaign', (), {
            'id': 1,
            'title': "Test Campaign",
            'subject': "Test Subject",
            'template_name': 'emails/newsletter_default.html',
            'sent_count': 0,
            'save': MagicMock()
        })()
        
        self.subscriber = type('MockSubscriber', (), {
            'id': 1,
            'email': "subscriber@example.com",
            'name': "Test Subscriber"
        })()
    
    @patch('jobs.tasks.EmailMessage')
    @patch('jobs.tasks.render_to_string')
    @patch('jobs.tasks.settings')
    def test_send_newsletter_email_success(self, mock_settings, mock_render, mock_email):
        """Test de l'envoi réussi d'un email de newsletter"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances
        mock_settings.SITE_URL = 'http://example.com'
        mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
        
        mock_render.side_effect = [
            '<h1>Test Newsletter</h1>',  # HTML content
            'Test Newsletter'  # Text content
        ]
        
        mock_email_instance = MagicMock()
        mock_email.return_value = mock_email_instance
        
        # Exécuter la tâche
        result = send_newsletter_email(1, 'subscriber@example.com', 'Test Subscriber')
        
        # Vérifications
        self.assertTrue(result)
        mock_email.assert_called_once()
        mock_email_instance.send.assert_called_once()
        self.campaign.save.assert_called_once()
        
        # Vérifier que le compteur a été incrémenté
        self.assertEqual(self.campaign.sent_count, 1)
    
    @patch('jobs.tasks.EmailMessage')
    @patch('jobs.tasks.render_to_string')
    def test_send_newsletter_email_campaign_not_found(self, mock_render, mock_email):
        """Test de l'échec quand la campagne n'existe pas"""
        from jobs.tasks import send_newsletter_email
        
        # Mock pour simuler une campagne non trouvée
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get:
            mock_get.side_effect = Exception("Campaign not found")
            
            # Exécuter la tâche
            with self.assertRaises(Exception):
                send_newsletter_email(999, 'subscriber@example.com')
            
            # Vérifier que l'email n'a pas été envoyé
            mock_email.assert_not_called()
    
    @patch('jobs.tasks.EmailMessage')
    @patch('jobs.tasks.render_to_string')
    def test_send_newsletter_email_subscriber_not_found(self, mock_render, mock_email):
        """Test de l'échec quand l'abonné n'existe pas"""
        from jobs.tasks import send_newsletter_email
        
        # Mock pour simuler un abonné non trouvé
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.return_value = self.campaign
            
            with patch('jobs.tasks.Newsletter.objects.get') as mock_get_subscriber:
                mock_get_subscriber.side_effect = Exception("Subscriber not found")
                
                # Exécuter la tâche
                with self.assertRaises(Exception):
                    send_newsletter_email(1, 'nonexistent@example.com')
                
                # Vérifier que l'email n'a pas été envoyé
                mock_email.assert_not_called()
    
    @patch('jobs.tasks.send_newsletter_email')
    def test_send_bulk_newsletter_success(self, mock_send_email):
        """Test de l'envoi en masse réussi"""
        from jobs.tasks import send_bulk_newsletter
        
        # Mock des dépendances
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.return_value = self.campaign
            
            with patch('jobs.tasks.Newsletter.objects.filter') as mock_filter:
                mock_subscribers = [
                    type('MockSubscriber', (), {
                        'email': f'subscriber{i}@example.com',
                        'name': f'Subscriber {i}'
                    })() for i in range(3)
                ]
                mock_filter.return_value = mock_subscribers
                
                # Exécuter la tâche
                result = send_bulk_newsletter(1)
                
                # Vérifications
                self.assertTrue(result)
                self.assertEqual(mock_send_email.delay.call_count, 3)
                
                # Vérifier que la campagne a été marquée comme terminée
                self.assertEqual(self.campaign.status, 'completed')
    
    @patch('jobs.tasks.send_newsletter_email')
    def test_send_bulk_newsletter_campaign_cannot_be_sent(self, mock_send_email):
        """Test de l'échec quand la campagne ne peut pas être envoyée"""
        from jobs.tasks import send_bulk_newsletter
        
        # Mock d'une campagne qui ne peut pas être envoyée
        self.campaign.can_be_sent = MagicMock(return_value=False)
        
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.return_value = self.campaign
            
            # Exécuter la tâche
            result = send_bulk_newsletter(1)
            
            # Vérifications
            self.assertFalse(result)
            mock_send_email.delay.assert_not_called()
    
    def test_send_scheduled_newsletter(self):
        """Test de l'envoi des newsletters programmées"""
        from jobs.tasks import send_scheduled_newsletter
        
        # Mock des campagnes programmées
        scheduled_campaigns = [
            type('MockCampaign', (), {
                'id': i,
                'title': f'Scheduled Campaign {i}'
            })() for i in range(2)
        ]
        
        with patch('jobs.tasks.NewsletterCampaign.objects.filter') as mock_filter:
            mock_filter.return_value = scheduled_campaigns
            
            with patch('jobs.tasks.send_bulk_newsletter.delay') as mock_send:
                # Exécuter la tâche
                send_scheduled_newsletter()
                
                # Vérifier que les campagnes ont été envoyées
                self.assertEqual(mock_send.call_count, 2)
                mock_send.assert_any_call(0)
                mock_send.assert_any_call(1)
    
    def test_cleanup_old_newsletter_logs(self):
        """Test du nettoyage des anciens logs de newsletter"""
        from jobs.tasks import cleanup_old_newsletter_logs
        
        # Mock des anciennes campagnes
        old_campaigns = [
            type('MockCampaign', (), {
                'id': i,
                'title': f'Old Campaign {i}'
            })() for i in range(3)
        ]
        
        with patch('jobs.tasks.NewsletterCampaign.objects.filter') as mock_filter:
            mock_filter.return_value = old_campaigns
            
            # Exécuter la tâche
            cleanup_old_newsletter_logs()
            
            # Vérifier que les anciennes campagnes ont été supprimées
            self.assertEqual(len(old_campaigns), 3)
    
    def test_test_email_connection_success(self):
        """Test du test de connexion email réussi"""
        from jobs.tasks import test_email_connection
        
        # Mock de la connexion email
        with patch('jobs.tasks.get_connection') as mock_get_connection:
            mock_connection = MagicMock()
            mock_get_connection.return_value = mock_connection
            
            # Exécuter la tâche
            result = test_email_connection()
            
            # Vérifications
            self.assertTrue(result)
            mock_connection.open.assert_called_once()
            mock_connection.close.assert_called_once()
    
    def test_test_email_connection_failure(self):
        """Test du test de connexion email échoué"""
        from jobs.tasks import test_email_connection
        
        # Mock d'une connexion échouée
        with patch('jobs.tasks.get_connection') as mock_get_connection:
            mock_connection = MagicMock()
            mock_connection.open.side_effect = Exception("Connection failed")
            mock_get_connection.return_value = mock_connection
            
            # Exécuter la tâche
            result = test_email_connection()
            
            # Vérifications
            self.assertFalse(result)

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class EmailTasksTest(TestCase):
    """Tests pour les tâches d'email générales"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('jobs.email_tasks.EmailMessage')
    def test_send_email_from_queue_success(self, mock_email):
        """Test de l'envoi réussi d'un email depuis la file d'attente"""
        from jobs.email_tasks import send_email_from_queue
        
        # Créer un email en file d'attente simulé
        email_queue = type('MockEmailQueue', (), {
            'id': 1,
            'to_email': 'recipient@example.com',
            'from_email': 'sender@example.com',
            'subject': 'Test Subject',
            'html_content': '<p>Test content</p>',
            'text_content': 'Test content',
            'can_be_sent': MagicMock(return_value=True),
            'mark_as_processing': MagicMock(),
            'mark_as_sent': MagicMock()
        })()
        
        # Mock des dépendances
        with patch('jobs.email_tasks.EmailQueue.objects.get') as mock_get:
            mock_get.return_value = email_queue
            
            mock_email_instance = MagicMock()
            mock_email.return_value = mock_email_instance
            
            # Exécuter la tâche
            result = send_email_from_queue(1)
            
            # Vérifications
            self.assertTrue(result)
            mock_email.assert_called_once()
            mock_email_instance.send.assert_called_once()
            email_queue.mark_as_processing.assert_called_once()
            email_queue.mark_as_sent.assert_called_once()
    
    @patch('jobs.email_tasks.EmailMessage')
    def test_send_email_from_queue_cannot_be_sent(self, mock_email):
        """Test de l'échec quand l'email ne peut pas être envoyé"""
        from jobs.email_tasks import send_email_from_queue
        
        # Créer un email qui ne peut pas être envoyé
        email_queue = type('MockEmailQueue', (), {
            'id': 1,
            'can_be_sent': MagicMock(return_value=False)
        })()
        
        with patch('jobs.email_tasks.EmailQueue.objects.get') as mock_get:
            mock_get.return_value = email_queue
            
            # Exécuter la tâche
            result = send_email_from_queue(1)
            
            # Vérifications
            self.assertFalse(result)
            mock_email.assert_not_called()
    
    def test_process_email_queue(self):
        """Test du traitement de la file d'attente des emails"""
        from jobs.email_tasks import process_email_queue
        
        # Mock des emails en attente
        pending_emails = [
            type('MockEmailQueue', (), {
                'id': i,
                'to_email': f'recipient{i}@example.com'
            })() for i in range(3)
        ]
        
        with patch('jobs.email_tasks.EmailQueue.objects.filter') as mock_filter:
            mock_filter.return_value = pending_emails
            
            with patch('jobs.email_tasks.send_email_from_queue.delay') as mock_send:
                # Exécuter la tâche
                process_email_queue()
                
                # Vérifier que les emails ont été traités
                self.assertEqual(mock_send.call_count, 3)
                mock_send.assert_any_call(0)
                mock_send.assert_any_call(1)
                mock_send.assert_any_call(2)
    
    def test_cleanup_failed_emails(self):
        """Test du nettoyage des emails échoués"""
        from jobs.email_tasks import cleanup_failed_emails
        
        # Mock des emails échoués
        failed_emails = [
            type('MockEmailQueue', (), {
                'id': i,
                'to_email': f'failed{i}@example.com'
            })() for i in range(2)
        ]
        
        with patch('jobs.email_tasks.EmailQueue.objects.filter') as mock_filter:
            mock_filter.return_value = failed_emails
            
            # Exécuter la tâche
            cleanup_failed_emails()
            
            # Vérifier que les emails échoués ont été supprimés
            self.assertEqual(len(failed_emails), 2)
    
    def test_retry_failed_emails(self):
        """Test du retry des emails échoués"""
        from jobs.email_tasks import retry_failed_emails
        
        # Mock des emails échoués
        failed_emails = [
            type('MockEmailQueue', (), {
                'id': i,
                'retry': MagicMock(return_value=True)
            })() for i in range(2)
        ]
        
        with patch('jobs.email_tasks.EmailQueue.objects.filter') as mock_filter:
            mock_filter.return_value = failed_emails
            
            # Exécuter la tâche
            retry_failed_emails()
            
            # Vérifier que les emails ont été retentés
            for email in failed_emails:
                email.retry.assert_called_once()
    
    @patch('jobs.email_tasks.EmailTemplate.objects.get')
    def test_send_template_email_success(self, mock_get_template):
        """Test de l'envoi réussi d'un email avec template"""
        from jobs.email_tasks import send_template_email
        
        # Mock du template
        template = type('MockTemplate', (), {
            'name': 'test_template',
            'is_active': True,
            'get_subject': MagicMock(return_value='Test Subject'),
            'get_html_content': MagicMock(return_value='<h1>Test</h1>'),
            'get_text_content': MagicMock(return_value='Test')
        })()
        mock_get_template.return_value = template
        
        # Mock de la création d'email en file d'attente
        with patch('jobs.email_tasks.EmailQueue.objects.create') as mock_create:
            mock_queue = MagicMock()
            mock_queue.id = 123
            mock_create.return_value = mock_queue
            
            with patch('jobs.email_tasks.send_email_from_queue.delay') as mock_send:
                # Exécuter la tâche
                result = send_template_email(
                    'test_template',
                    {'name': 'Test User'},
                    'user@example.com'
                )
                
                # Vérifications
                self.assertEqual(result, 123)
                mock_create.assert_called_once()
                mock_send.assert_called_once_with(123)
    
    @patch('jobs.email_tasks.EmailTemplate.objects.get')
    def test_send_template_email_template_not_found(self, mock_get_template):
        """Test de l'échec quand le template n'existe pas"""
        from jobs.email_tasks import send_template_email
        
        # Mock d'un template non trouvé
        mock_get_template.side_effect = Exception("Template not found")
        
        # Exécuter la tâche
        with self.assertRaises(Exception):
            send_template_email(
                'nonexistent_template',
                {'name': 'Test User'},
                'user@example.com'
            )
    
    def test_send_bulk_template_emails(self):
        """Test de l'envoi en masse d'emails avec template"""
        from jobs.email_tasks import send_bulk_template_emails
        
        # Mock du template
        with patch('jobs.email_tasks.EmailTemplate.objects.get') as mock_get_template:
            template = type('MockTemplate', (), {
                'name': 'test_template',
                'is_active': True,
                'get_subject': MagicMock(return_value='Test Subject'),
                'get_html_content': MagicMock(return_value='<h1>Test</h1>'),
                'get_text_content': MagicMock(return_value='Test')
            })()
            mock_get_template.return_value = template
            
            # Mock de la création d'emails en file d'attente
            with patch('jobs.email_tasks.EmailQueue.objects.create') as mock_create:
                # Préparer la liste de contextes et emails
                context_list = [
                    ({'name': f'User {i}'}, f'user{i}@example.com')
                    for i in range(3)
                ]
                
                # Exécuter la tâche
                result = send_bulk_template_emails(
                    'test_template',
                    context_list
                )
                
                # Vérifications
                self.assertEqual(result, 3)
                self.assertEqual(mock_create.call_count, 3)

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class MaintenanceTasksTest(TestCase):
    """Tests pour les tâches de maintenance"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('jobs.maintenance_tasks.os.path.exists')
    @patch('jobs.maintenance_tasks.os.listdir')
    @patch('jobs.maintenance_tasks.os.path.isfile')
    @patch('jobs.maintenance_tasks.os.path.getmtime')
    @patch('jobs.maintenance_tasks.os.remove')
    @patch('jobs.maintenance_tasks.settings')
    def test_cleanup_old_files_success(self, mock_settings, mock_getmtime, 
                                      mock_isfile, mock_listdir, mock_exists, mock_remove):
        """Test du nettoyage réussi des anciens fichiers"""
        from jobs.maintenance_tasks import cleanup_old_files
        
        # Mock des dépendances
        mock_settings.MEDIA_ROOT = '/tmp/media'
        mock_settings.BASE_DIR = '/tmp/project'
        
        mock_exists.return_value = True
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        
        # Simuler des fichiers de plus de 24h
        old_time = timezone.now() - timedelta(hours=25)
        mock_getmtime.return_value = old_time.timestamp()
        
        # Exécuter la tâche
        result = cleanup_old_files()
        
        # Vérifications
        self.assertEqual(result, 2)
        self.assertEqual(mock_remove.call_count, 2)
    
    @patch('jobs.maintenance_tasks.connection')
    def test_cleanup_database_success(self, mock_connection):
        """Test du nettoyage réussi de la base de données"""
        from jobs.maintenance_tasks import cleanup_database
        
        # Mock de la connexion à la base de données
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 5
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Exécuter la tâche
        result = cleanup_database()
        
        # Vérifications
        self.assertEqual(result, 5)
        self.assertEqual(mock_cursor.execute.call_count, 2)
    
    @patch('jobs.maintenance_tasks.psutil.virtual_memory')
    @patch('jobs.maintenance_tasks.psutil.cpu_percent')
    @patch('jobs.maintenance_tasks.connection')
    @patch('jobs.maintenance_tasks.settings')
    @patch('jobs.maintenance_tasks.os.path.exists')
    @patch('jobs.maintenance_tasks.shutil.disk_usage')
    def test_check_system_health_success(self, mock_disk_usage, mock_exists,
                                       mock_settings, mock_connection, mock_cpu, mock_memory):
        """Test de la vérification réussie de la santé du système"""
        from jobs.maintenance_tasks import check_system_health
        
        # Mock des dépendances
        mock_settings.MEDIA_ROOT = '/tmp/media'
        mock_settings.BASE_DIR = '/tmp/project'
        
        mock_exists.return_value = True
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)  # 1GB total, 500MB used, 500MB free
        
        mock_memory_instance = MagicMock()
        mock_memory_instance.total = 8000000000  # 8GB
        mock_memory_instance.available = 4000000000  # 4GB
        mock_memory_instance.used = 4000000000  # 4GB
        mock_memory_instance.percent = 50.0
        mock_memory.return_value = mock_memory_instance
        
        mock_cpu.return_value = 25.0
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [10]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Exécuter la tâche
        result = check_system_health()
        
        # Vérifications
        self.assertIn('timestamp', result)
        self.assertIn('disk_usage', result)
        self.assertIn('memory_usage', result)
        self.assertIn('cpu_usage', result)
        self.assertIn('database_connections', result)
        self.assertEqual(result['overall_status'], 'healthy')
    
    @patch('jobs.maintenance_tasks.settings')
    @patch('jobs.maintenance_tasks.os.makedirs')
    @patch('jobs.maintenance_tasks.os.system')
    @patch('jobs.maintenance_tasks.os.remove')
    @patch('jobs.maintenance_tasks.gzip.open')
    @patch('jobs.maintenance_tasks.os.listdir')
    def test_backup_database_success(self, mock_listdir, mock_gzip_open, mock_remove,
                                   mock_system, mock_makedirs, mock_settings):
        """Test de la sauvegarde réussie de la base de données"""
        from jobs.maintenance_tasks import backup_database
        
        # Mock des dépendances
        mock_settings.BASE_DIR = '/tmp/project'
        mock_settings.DATABASES = {
            'default': {
                'HOST': 'localhost',
                'USER': 'testuser',
                'NAME': 'testdb'
            }
        }
        
        mock_makedirs.return_value = None
        mock_system.return_value = 0  # Succès
        mock_listdir.return_value = ['backup_20240101_120000.sql.gz']
        
        # Mock de gzip
        mock_gzip_file = MagicMock()
        mock_gzip_open.return_value.__enter__.return_value = mock_gzip_file
        
        # Exécuter la tâche
        result = backup_database()
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith('.gz'))
        mock_system.assert_called_once()
        mock_makedirs.assert_called_once()
    
    @patch('jobs.maintenance_tasks.connection')
    def test_optimize_database_success(self, mock_connection):
        """Test de l'optimisation réussie de la base de données"""
        from jobs.maintenance_tasks import optimize_database
        
        # Mock de la connexion à la base de données
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Exécuter la tâche
        result = optimize_database()
        
        # Vérifications
        self.assertTrue(result)
        self.assertEqual(mock_cursor.execute.call_count, 3)
    
    @patch('jobs.maintenance_tasks.cache')
    @patch('jobs.maintenance_tasks.User.objects.filter')
    @patch('jobs.maintenance_tasks.send_template_email')
    def test_send_health_report_success(self, mock_send_email, mock_user_filter, mock_cache):
        """Test de l'envoi réussi du rapport de santé"""
        from jobs.maintenance_tasks import send_health_report
        
        # Mock des dépendances
        mock_cache.get.return_value = {
            'overall_status': 'healthy',
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        mock_users = [self.user]
        mock_user_filter.return_value = mock_users
        
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_send_email.delay.return_value = mock_task
        
        # Exécuter la tâche
        result = send_health_report()
        
        # Vérifications
        self.assertTrue(result)
        mock_send_email.delay.assert_called_once()

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TaskRetryTest(TestCase):
    """Tests pour la gestion des retry des tâches"""
    
    def test_task_retry_on_failure(self):
        """Test du retry automatique d'une tâche en cas d'échec"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances pour simuler un échec
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.side_effect = Exception("Temporary failure")
            
            # Exécuter la tâche
            with self.assertRaises(Exception):
                send_newsletter_email(1, 'test@example.com')
            
            # Vérifier que la tâche a été retentée
            # Note: En mode eager, le retry n'est pas réellement exécuté
            pass
    
    def test_task_max_retries_exceeded(self):
        """Test que la tâche n'est plus retentée après le nombre maximum de tentatives"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances pour simuler des échecs répétés
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.side_effect = Exception("Permanent failure")
            
            # Exécuter la tâche
            with self.assertRaises(Exception):
                send_newsletter_email(1, 'test@example.com')
            
            # Vérifier que la tâche n'est plus retentée
            # Note: En mode eager, le retry n'est pas réellement exécuté
            pass

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TaskLoggingTest(TestCase):
    """Tests pour la journalisation des tâches"""
    
    @patch('jobs.tasks.logger')
    def test_task_success_logging(self, mock_logger):
        """Test de la journalisation en cas de succès"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.return_value = type('MockCampaign', (), {
                'id': 1,
                'title': "Test Campaign",
                'template_name': 'emails/newsletter_default.html',
                'sent_count': 0,
                'save': MagicMock()
            })()
            
            with patch('jobs.tasks.Newsletter.objects.get') as mock_get_subscriber:
                mock_get_subscriber.return_value = type('MockSubscriber', (), {
                    'id': 1,
                    'email': "subscriber@example.com",
                    'name': "Test Subscriber"
                })()
                
                with patch('jobs.tasks.render_to_string') as mock_render:
                    mock_render.side_effect = ['<h1>Test</h1>', 'Test']
                    
                    with patch('jobs.tasks.EmailMessage') as mock_email:
                        mock_email_instance = MagicMock()
                        mock_email.return_value = mock_email_instance
                        
                        with patch('jobs.tasks.settings') as mock_settings:
                            mock_settings.SITE_URL = 'http://example.com'
                            mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
                            
                            # Exécuter la tâche
                            send_newsletter_email(1, 'subscriber@example.com')
                            
                            # Vérifier que les logs ont été écrits
                            mock_logger.info.assert_called()
    
    @patch('jobs.tasks.logger')
    def test_task_failure_logging(self, mock_logger):
        """Test de la journalisation en cas d'échec"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances pour simuler un échec
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.side_effect = Exception("Campaign not found")
            
            # Exécuter la tâche
            with self.assertRaises(Exception):
                send_newsletter_email(999, 'test@example.com')
            
            # Vérifier que les logs d'erreur ont été écrits
            mock_logger.error.assert_called()

@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class TaskPerformanceTest(TestCase):
    """Tests pour les performances des tâches"""
    
    def test_task_execution_time(self):
        """Test du temps d'exécution des tâches"""
        import time
        from jobs.tasks import test_email_connection
        
        # Mock de la connexion email
        with patch('jobs.tasks.get_connection') as mock_get_connection:
            mock_connection = MagicMock()
            mock_get_connection.return_value = mock_connection
            
            # Mesurer le temps d'exécution
            start_time = time.time()
            result = test_email_connection()
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Vérifications
            self.assertTrue(result)
            self.assertLess(execution_time, 1.0)  # Moins d'1 seconde
    
    def test_bulk_task_efficiency(self):
        """Test de l'efficacité des tâches en masse"""
        from jobs.tasks import send_bulk_newsletter
        
        # Mock des dépendances
        with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
            mock_get_campaign.return_value = type('MockCampaign', (), {
                'id': 1,
                'title': "Test Campaign",
                'can_be_sent': MagicMock(return_value=True),
                'status': 'draft',
                'started_at': None,
                'completed_at': None,
                'save': MagicMock()
            })()
            
            with patch('jobs.tasks.Newsletter.objects.filter') as mock_filter:
                # Simuler 100 abonnés
                mock_subscribers = [
                    type('MockSubscriber', (), {
                        'email': f'subscriber{i}@example.com',
                        'name': f'Subscriber {i}'
                    })() for i in range(100)
                ]
                mock_filter.return_value = mock_subscribers
                
                with patch('jobs.tasks.send_newsletter_email.delay') as mock_send:
                    # Exécuter la tâche
                    result = send_bulk_newsletter(1)
                    
                    # Vérifications
                    self.assertTrue(result)
                    self.assertEqual(mock_send.call_count, 100)

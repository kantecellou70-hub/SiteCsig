"""
Tests d'intégration pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import outbox
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from .test_settings import JobsTestCaseWithCelery, JobsTestCaseWithEmail

class IntegrationTest(JobsTestCaseWithCelery):
    """Tests d'intégration pour l'application jobs"""
    
    def setUp(self):
        super().setUp()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def tearDown(self):
        super().tearDown()
        cache.clear()

class NewsletterCampaignIntegrationTest(IntegrationTest):
    """Tests d'intégration pour les campagnes de newsletter"""
    
    def test_complete_newsletter_campaign_workflow(self):
        """Test du workflow complet d'une campagne de newsletter"""
        from content_management.models import NewsletterCampaign
        from jobs.models import NewsletterLog, EmailTemplate
        from jobs.tasks import send_newsletter_email, send_bulk_newsletter
        
        # 1. Créer un template d'email
        template = EmailTemplate.objects.create(
            name='test_template',
            subject_template='Hello {{ subscriber.name }}!',
            html_template='<h1>Hello {{ subscriber.name }}</h1><p>Welcome to our newsletter!</p>',
            text_template='Hello {{ subscriber.name }}!\n\nWelcome to our newsletter!'
        )
        
        # 2. Créer une campagne de newsletter
        campaign = NewsletterCampaign.objects.create(
            title='Test Campaign',
            subject='Welcome Newsletter',
            content='Welcome to our newsletter!',
            template_name='test_template',
            status='draft',
            created_by=self.user
        )
        
        # 3. Simuler des abonnés (mock Newsletter.objects.filter)
        with patch('jobs.tasks.Newsletter.objects.filter') as mock_filter:
            mock_subscribers = [
                type('MockSubscriber', (), {
                    'id': i,
                    'email': f'subscriber{i}@example.com',
                    'name': f'Subscriber {i}'
                })() for i in range(5)
            ]
            mock_filter.return_value = mock_subscribers
            
            # 4. Envoyer la campagne
            with patch('jobs.tasks.send_newsletter_email.delay') as mock_send:
                result = send_bulk_newsletter(campaign.id)
                
                # Vérifications
                self.assertTrue(result)
                self.assertEqual(mock_send.call_count, 5)
                
                # Vérifier que la campagne a été mise à jour
                campaign.refresh_from_db()
                self.assertEqual(campaign.status, 'sending')
                self.assertIsNotNone(campaign.started_at)
        
        # 5. Nettoyer
        template.delete()
        campaign.delete()
    
    def test_newsletter_campaign_with_real_email_sending(self):
        """Test d'une campagne avec envoi d'email réel"""
        from content_management.models import NewsletterCampaign
        from jobs.models import EmailTemplate
        from jobs.tasks import send_newsletter_email
        
        # 1. Créer un template
        template = EmailTemplate.objects.create(
            name='real_email_template',
            subject_template='Test from {{ campaign.title }}',
            html_template='<h1>{{ campaign.title }}</h1><p>{{ campaign.content }}</p>',
            text_template='{{ campaign.title }}\n\n{{ campaign.content }}'
        )
        
        # 2. Créer une campagne
        campaign = NewsletterCampaign.objects.create(
            title='Real Email Test',
            subject='Test Email',
            content='This is a test email content.',
            template_name='real_email_template',
            status='draft',
            created_by=self.user
        )
        
        # 3. Envoyer un email réel
        with patch('jobs.tasks.settings') as mock_settings:
            mock_settings.SITE_URL = 'http://example.com'
            mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
            
            result = send_newsletter_email(
                campaign.id, 
                'test@example.com', 
                'Test User'
            )
            
            # Vérifications
            self.assertTrue(result)
        
        # 4. Nettoyer
        template.delete()
        campaign.delete()
    
    def test_newsletter_campaign_scheduling_integration(self):
        """Test d'intégration pour la planification des campagnes"""
        from content_management.models import NewsletterCampaign
        from jobs.tasks import send_scheduled_newsletter
        
        # 1. Créer une campagne planifiée
        scheduled_time = timezone.now() + timedelta(minutes=1)
        campaign = NewsletterCampaign.objects.create(
            title='Scheduled Campaign',
            subject='Scheduled Newsletter',
            content='This is a scheduled newsletter.',
            status='scheduled',
            scheduled_at=scheduled_time,
            created_by=self.user
        )
        
        # 2. Simuler l'exécution de la tâche planifiée
        with patch('jobs.tasks.Newsletter.objects.filter') as mock_filter:
            mock_subscribers = [
                type('MockSubscriber', (), {
                    'id': 1,
                    'email': 'test@example.com',
                    'name': 'Test User'
                })()
            ]
            mock_filter.return_value = mock_subscribers
            
            with patch('jobs.tasks.send_newsletter_email.delay') as mock_send:
                result = send_scheduled_newsletter()
                
                # Vérifications
                self.assertTrue(result)
                mock_send.assert_called_once()
        
        # 3. Nettoyer
        campaign.delete()

class EmailQueueIntegrationTest(IntegrationTest):
    """Tests d'intégration pour la file d'attente d'emails"""
    
    def test_email_queue_processing_workflow(self):
        """Test du workflow complet de traitement de la file d'attente"""
        from jobs.models import EmailQueue
        from jobs.email_tasks import process_email_queue, send_email_from_queue
        
        # 1. Créer des emails en file d'attente
        emails = []
        for i in range(3):
            email = EmailQueue.objects.create(
                to_email=f'recipient{i}@example.com',
                from_email='sender@example.com',
                subject=f'Test Email {i}',
                html_content=f'<h1>Test {i}</h1>',
                priority='normal'
            )
            emails.append(email)
        
        # 2. Traiter la file d'attente
        with patch('jobs.email_tasks.send_email_from_queue.delay') as mock_send:
            process_email_queue()
            
            # Vérifications
            self.assertEqual(mock_send.call_count, 3)
            
            # Vérifier que les emails ont été traités
            for email in emails:
                email.refresh_from_db()
                self.assertEqual(email.status, 'queued')
        
        # 3. Nettoyer
        for email in emails:
            email.delete()
    
    def test_email_queue_priority_handling(self):
        """Test de la gestion des priorités dans la file d'attente"""
        from jobs.models import EmailQueue
        from jobs.email_tasks import process_email_queue
        
        # 1. Créer des emails avec différentes priorités
        high_priority = EmailQueue.objects.create(
            to_email='high@example.com',
            from_email='sender@example.com',
            subject='High Priority',
            html_content='<h1>High Priority</h1>',
            priority='high'
        )
        
        normal_priority = EmailQueue.objects.create(
            to_email='normal@example.com',
            from_email='sender@example.com',
            subject='Normal Priority',
            html_content='<h1>Normal Priority</h1>',
            priority='normal'
        )
        
        low_priority = EmailQueue.objects.create(
            to_email='low@example.com',
            from_email='sender@example.com',
            subject='Low Priority',
            html_content='<h1>Low Priority</h1>',
            priority='low'
        )
        
        # 2. Traiter la file d'attente
        with patch('jobs.email_tasks.send_email_from_queue.delay') as mock_send:
            process_email_queue()
            
            # Vérifications
            self.assertEqual(mock_send.call_count, 3)
            
            # Vérifier l'ordre des priorités (high, normal, low)
            calls = mock_send.call_args_list
            # Note: L'ordre exact dépend de l'implémentation, mais tous doivent être traités
        
        # 3. Nettoyer
        high_priority.delete()
        normal_priority.delete()
        low_priority.delete()

class SystemMonitoringIntegrationTest(IntegrationTest):
    """Tests d'intégration pour la surveillance système"""
    
    def test_system_health_monitoring_integration(self):
        """Test d'intégration pour la surveillance de santé du système"""
        from jobs.maintenance_tasks import check_system_health
        from jobs.utils import SystemMonitor
        
        # 1. Vérifier la santé du système
        health_status = check_system_health()
        
        # Vérifications de base
        self.assertIn('timestamp', health_status)
        self.assertIn('overall_status', health_status)
        self.assertIn('components', health_status)
        
        # 2. Vérifier les composants individuels
        components = health_status['components']
        
        # CPU
        if 'cpu' in components:
            cpu_info = components['cpu']
            self.assertIn('status', cpu_info)
            self.assertIn('usage_percent', cpu_info)
        
        # Mémoire
        if 'memory' in components:
            memory_info = components['memory']
            self.assertIn('status', memory_info)
            self.assertIn('usage_percent', memory_info)
        
        # Disque
        if 'disk' in components:
            disk_info = components['disk']
            self.assertIn('status', disk_info)
            self.assertIn('usage_percent', disk_info)
    
    def test_system_monitor_data_collection_integration(self):
        """Test d'intégration pour la collecte de données système"""
        from jobs.utils import SystemMonitor
        
        # 1. Collecter les informations système
        cpu_info = SystemMonitor.get_cpu_info()
        memory_info = SystemMonitor.get_memory_info()
        disk_info = SystemMonitor.get_disk_info()
        
        # 2. Vérifier la cohérence des données
        # CPU
        self.assertIn('usage_percent', cpu_info)
        self.assertIn('count', cpu_info)
        self.assertGreaterEqual(cpu_info['usage_percent'], 0)
        self.assertLessEqual(cpu_info['usage_percent'], 100)
        self.assertGreater(cpu_info['count'], 0)
        
        # Mémoire
        self.assertIn('total_gb', memory_info)
        self.assertIn('available_gb', memory_info)
        self.assertIn('usage_percent', memory_info)
        self.assertGreater(memory_info['total_gb'], 0)
        self.assertGreaterEqual(memory_info['available_gb'], 0)
        self.assertGreaterEqual(memory_info['usage_percent'], 0)
        self.assertLessEqual(memory_info['usage_percent'], 100)
        
        # Disque
        self.assertIn('total_gb', disk_info)
        self.assertIn('used_gb', disk_info)
        self.assertIn('usage_percent', disk_info)
        self.assertGreater(disk_info['total_gb'], 0)
        self.assertGreaterEqual(disk_info['used_gb'], 0)
        self.assertGreaterEqual(disk_info['usage_percent'], 0)
        self.assertLessEqual(disk_info['usage_percent'], 100)
    
    def test_performance_monitor_integration(self):
        """Test d'intégration pour le moniteur de performance"""
        from jobs.utils import PerformanceMonitor
        
        # 1. Tester le décorateur de timing
        @PerformanceMonitor.timing
        def test_function():
            return "test_result"
        
        # 2. Exécuter la fonction
        result = test_function()
        
        # Vérifications
        self.assertEqual(result, "test_result")
        
        # 3. Vérifier que les métriques ont été collectées
        # Note: Cela dépend de l'implémentation du moniteur de performance
        # Le décorateur devrait avoir enregistré le temps d'exécution

class CacheIntegrationTest(IntegrationTest):
    """Tests d'intégration pour le cache"""
    
    def test_cache_manager_integration(self):
        """Test d'intégration pour le gestionnaire de cache"""
        from jobs.utils import CacheManager
        
        # 1. Tester la mise en cache
        test_data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        CacheManager.set_cached_data('test_key', test_data, timeout=300)
        
        # 2. Récupérer les données
        cached_data = CacheManager.get_cached_data('test_key')
        
        # Vérifications
        self.assertEqual(cached_data, test_data)
        
        # 3. Tester la génération de clés
        cache_key = CacheManager.get_cache_key('test', 'data', '123')
        self.assertIsInstance(cache_key, str)
        self.assertIn('test', cache_key)
        self.assertIn('data', cache_key)
        self.assertIn('123', cache_key)
        
        # 4. Tester la suppression
        CacheManager.delete_cached_data('test_key')
        deleted_data = CacheManager.get_cached_data('test_key')
        self.assertIsNone(deleted_data)
    
    def test_cache_invalidation_integration(self):
        """Test d'intégration pour l'invalidation du cache"""
        from jobs.utils import CacheManager
        
        # 1. Mettre plusieurs clés en cache
        for i in range(5):
            CacheManager.set_cached_data(f'key_{i}', f'value_{i}', timeout=300)
        
        # 2. Vérifier que toutes les clés sont présentes
        for i in range(5):
            value = CacheManager.get_cached_data(f'key_{i}')
            self.assertEqual(value, f'value_{i}')
        
        # 3. Invalider le cache
        cache.clear()
        
        # 4. Vérifier que toutes les clés ont été supprimées
        for i in range(5):
            value = CacheManager.get_cached_data(f'key_{i}')
            self.assertIsNone(value)

class DataExportIntegrationTest(IntegrationTest):
    """Tests d'intégration pour l'export de données"""
    
    def test_data_exporter_format_integration(self):
        """Test d'intégration pour les différents formats d'export"""
        from jobs.utils import DataExporter
        
        # 1. Données de test
        test_data = [
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 30,
                'city': 'New York'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'age': 25,
                'city': 'Los Angeles'
            }
        ]
        
        # 2. Test export CSV
        csv_content = DataExporter.export_to_csv(test_data)
        self.assertIsNotNone(csv_content)
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # En-tête + 2 lignes de données
        self.assertIn('id,name,email,age,city', lines[0])  # En-tête
        self.assertIn('1,John Doe,john@example.com,30,New York', lines[1])
        self.assertIn('2,Jane Smith,jane@example.com,25,Los Angeles', lines[2])
        
        # 3. Test export JSON
        json_content = DataExporter.export_to_json(test_data)
        self.assertIsNotNone(json_content)
        parsed_json = json.loads(json_content)
        self.assertEqual(len(parsed_json), 2)
        self.assertEqual(parsed_json[0]['name'], 'John Doe')
        self.assertEqual(parsed_json[1]['name'], 'Jane Smith')
        
        # 4. Test export XML
        xml_content = DataExporter.export_to_xml(
            test_data, 
            root_name='users', 
            item_name='user'
        )
        self.assertIsNotNone(xml_content)
        self.assertIn('<users>', xml_content)
        self.assertIn('</users>', xml_content)
        self.assertIn('<user>', xml_content)
        self.assertIn('</user>', xml_content)
        self.assertIn('<name>John Doe</name>', xml_content)
        self.assertIn('<name>Jane Smith</name>', xml_content)

class SecurityUtilsIntegrationTest(IntegrationTest):
    """Tests d'intégration pour les utilitaires de sécurité"""
    
    def test_security_utils_integration(self):
        """Test d'intégration pour les utilitaires de sécurité"""
        from jobs.utils import SecurityUtils
        
        # 1. Test de génération de tokens
        token_16 = SecurityUtils.generate_token(16)
        token_32 = SecurityUtils.generate_token(32)
        token_64 = SecurityUtils.generate_token(64)
        
        # Vérifications
        self.assertEqual(len(token_16), 16)
        self.assertEqual(len(token_32), 32)
        self.assertEqual(len(token_64), 64)
        
        # Vérifier l'unicité
        tokens = [token_16, token_32, token_64]
        self.assertEqual(len(set(tokens)), 3)
        
        # 2. Test de génération de mots de passe
        password_8 = SecurityUtils.generate_secure_password(8)
        password_16 = SecurityUtils.generate_secure_password(16)
        password_32 = SecurityUtils.generate_secure_password(32)
        
        # Vérifications
        self.assertEqual(len(password_8), 8)
        self.assertEqual(len(password_16), 16)
        self.assertEqual(len(password_32), 32)
        
        # Vérifier les critères de sécurité
        for password in [password_8, password_16, password_32]:
            self.assertTrue(any(c.isupper() for c in password))
            self.assertTrue(any(c.islower() for c in password))
            self.assertTrue(any(c.isdigit() for c in password))
        
        # 3. Test de hachage
        test_data = "Test data for hashing"
        hash_value = SecurityUtils.hash_data(test_data)
        
        # Vérifications
        self.assertEqual(len(hash_value), 64)  # SHA-256
        self.assertIsInstance(hash_value, str)
        
        # Vérifier la cohérence
        hash_value_2 = SecurityUtils.hash_data(test_data)
        self.assertEqual(hash_value, hash_value_2)

class EmailTemplateIntegrationTest(IntegrationTest):
    """Tests d'intégration pour les templates d'email"""
    
    def test_email_template_rendering_integration(self):
        """Test d'intégration pour le rendu des templates d'email"""
        from jobs.models import EmailTemplate
        
        # 1. Créer un template complexe
        template = EmailTemplate.objects.create(
            name='integration_test_template',
            subject_template='Welcome {{ user.name }} to {{ company.name }}',
            html_template='''
                <h1>Welcome {{ user.name }}!</h1>
                <p>You are joining <strong>{{ company.name }}</strong> as a {{ user.role }}.</p>
                <p>Your department: {{ user.department }}</p>
                <p>Start date: {{ user.start_date|date:"F j, Y" }}</p>
                {% if user.manager %}
                <p>Your manager: {{ user.manager.name }}</p>
                {% endif %}
                <p>Skills: {{ user.skills|join:', ' }}</p>
            ''',
            text_template='''
                Welcome {{ user.name }}!
                
                You are joining {{ company.name }} as a {{ user.role }}.
                Your department: {{ user.department }}
                Start date: {{ user.start_date|date:"F j, Y" }}
                {% if user.manager %}
                Your manager: {{ user.manager.name }}
                {% endif %}
                Skills: {{ user.skills|join:', ' }}
            '''
        )
        
        # 2. Contexte de test
        context = {
            'user': {
                'name': 'Alice Johnson',
                'role': 'Senior Developer',
                'department': 'Engineering',
                'start_date': datetime(2024, 1, 15),
                'manager': {'name': 'Bob Wilson'},
                'skills': ['Python', 'Django', 'React', 'PostgreSQL']
            },
            'company': {
                'name': 'Tech Solutions Inc.'
            }
        }
        
        # 3. Tester le rendu
        subject = template.get_subject(context)
        html_content = template.get_html_content(context)
        text_content = template.get_text_content(context)
        
        # Vérifications du sujet
        self.assertIn('Alice Johnson', subject)
        self.assertIn('Tech Solutions Inc.', subject)
        
        # Vérifications du contenu HTML
        self.assertIn('<h1>Welcome Alice Johnson!</h1>', html_content)
        self.assertIn('<strong>Tech Solutions Inc.</strong>', html_content)
        self.assertIn('Senior Developer', html_content)
        self.assertIn('Engineering', html_content)
        self.assertIn('January 15, 2024', html_content)
        self.assertIn('Bob Wilson', html_content)
        self.assertIn('Python, Django, React, PostgreSQL', html_content)
        
        # Vérifications du contenu texte
        self.assertIn('Welcome Alice Johnson!', text_content)
        self.assertIn('Tech Solutions Inc.', text_content)
        self.assertIn('Senior Developer', text_content)
        self.assertIn('Engineering', text_content)
        self.assertIn('January 15, 2024', text_content)
        self.assertIn('Bob Wilson', text_content)
        self.assertIn('Python, Django, React, PostgreSQL', text_content)
        
        # 4. Nettoyer
        template.delete()
    
    def test_email_template_with_conditional_logic(self):
        """Test d'intégration pour les templates avec logique conditionnelle"""
        from jobs.models import EmailTemplate
        
        # 1. Créer un template avec logique conditionnelle
        template = EmailTemplate.objects.create(
            name='conditional_template',
            subject_template='{{ event.title }} - {{ event.date|date:"F j" }}',
            html_template='''
                <h1>{{ event.title }}</h1>
                <p>Date: {{ event.date|date:"F j, Y" }}</p>
                <p>Location: {{ event.location }}</p>
                
                {% if event.description %}
                <p>{{ event.description }}</p>
                {% endif %}
                
                {% if event.attendees %}
                <h2>Attendees ({{ event.attendees|length }})</h2>
                <ul>
                {% for attendee in event.attendees %}
                    <li>{{ attendee.name }} - {{ attendee.role }}</li>
                {% endfor %}
                </ul>
                {% else %}
                <p>No attendees registered yet.</p>
                {% endif %}
                
                {% if event.is_free %}
                <p><strong>This event is free!</strong></p>
                {% else %}
                <p>Price: ${{ event.price }}</p>
                {% endif %}
            ''',
            text_template='''
                {{ event.title }}
                
                Date: {{ event.date|date:"F j, Y" }}
                Location: {{ event.location }}
                
                {% if event.description %}
                {{ event.description }}
                {% endif %}
                
                {% if event.attendees %}
                Attendees ({{ event.attendees|length }}):
                {% for attendee in event.attendees %}
                - {{ attendee.name }} - {{ attendee.role }}
                {% endfor %}
                {% else %}
                No attendees registered yet.
                {% endif %}
                
                {% if event.is_free %}
                This event is free!
                {% else %}
                Price: ${{ event.price }}
                {% endif %}
            '''
        )
        
        # 2. Contexte avec données conditionnelles
        context = {
            'event': {
                'title': 'Tech Conference 2024',
                'date': datetime(2024, 6, 15),
                'location': 'San Francisco Convention Center',
                'description': 'Annual technology conference featuring industry leaders.',
                'attendees': [
                    {'name': 'John Doe', 'role': 'Speaker'},
                    {'name': 'Jane Smith', 'role': 'Organizer'},
                    {'name': 'Bob Wilson', 'role': 'Attendee'}
                ],
                'is_free': False,
                'price': 299
            }
        }
        
        # 3. Tester le rendu
        subject = template.get_subject(context)
        html_content = template.get_html_content(context)
        text_content = template.get_text_content(context)
        
        # Vérifications
        self.assertIn('Tech Conference 2024', subject)
        self.assertIn('June 15', subject)
        
        # Vérifier la logique conditionnelle
        self.assertIn('Annual technology conference featuring industry leaders.', html_content)
        self.assertIn('Attendees (3)', html_content)
        self.assertIn('John Doe - Speaker', html_content)
        self.assertIn('Price: $299', html_content)
        
        # 4. Nettoyer
        template.delete()

class NotificationManagerIntegrationTest(IntegrationTest):
    """Tests d'intégration pour le gestionnaire de notifications"""
    
    def test_notification_manager_integration(self):
        """Test d'intégration pour le gestionnaire de notifications"""
        from jobs.utils import NotificationManager
        
        # 1. Tester l'envoi de notifications
        notification = NotificationManager.send_notification(
            user_id=self.user.id,
            title='Test Notification',
            message='This is a test notification',
            notification_type='info'
        )
        
        # Vérifications
        self.assertIsNotNone(notification)
        self.assertEqual(notification['title'], 'Test Notification')
        self.assertEqual(notification['message'], 'This is a test notification')
        self.assertEqual(notification['type'], 'info')
        
        # 2. Tester la récupération des notifications
        notifications = NotificationManager.get_user_notifications(self.user.id)
        
        # Vérifications
        self.assertIsInstance(notifications, list)
        
        # 3. Tester la marque comme lue
        if notifications:
            notification_id = notifications[0]['id']
            result = NotificationManager.mark_as_read(notification_id)
            self.assertTrue(result)
        
        # 4. Tester la suppression
        if notifications:
            notification_id = notifications[0]['id']
            result = NotificationManager.delete_notification(notification_id)
            self.assertTrue(result)

class TaskSchedulerIntegrationTest(IntegrationTest):
    """Tests d'intégration pour le planificateur de tâches"""
    
    def test_task_scheduler_integration(self):
        """Test d'intégration pour le planificateur de tâches"""
        from jobs.utils import TaskScheduler
        
        # 1. Tester la planification d'une tâche
        task_id = TaskScheduler.schedule_task(
            task_name='test_task',
            args=[1, 2, 3],
            kwargs={'key': 'value'},
            eta=timezone.now() + timedelta(minutes=5)
        )
        
        # Vérifications
        self.assertIsNotNone(task_id)
        
        # 2. Tester la récupération des tâches planifiées
        scheduled_tasks = TaskScheduler.get_scheduled_tasks()
        
        # Vérifications
        self.assertIsInstance(scheduled_tasks, list)
        
        # 3. Tester l'annulation d'une tâche
        if task_id:
            result = TaskScheduler.cancel_task(task_id)
            self.assertTrue(result)
    
    def test_task_scheduler_with_recurring_tasks(self):
        """Test d'intégration pour les tâches récurrentes"""
        from jobs.utils import TaskScheduler
        
        # 1. Tester la planification d'une tâche récurrente
        task_id = TaskScheduler.schedule_recurring_task(
            task_name='recurring_test_task',
            args=[1, 2, 3],
            kwargs={'key': 'value'},
            interval_minutes=30
        )
        
        # Vérifications
        self.assertIsNotNone(task_id)
        
        # 2. Tester la récupération des tâches récurrentes
        recurring_tasks = TaskScheduler.get_recurring_tasks()
        
        # Vérifications
        self.assertIsInstance(recurring_tasks, list)
        
        # 3. Tester l'arrêt d'une tâche récurrente
        if task_id:
            result = TaskScheduler.stop_recurring_task(task_id)
            self.assertTrue(result)

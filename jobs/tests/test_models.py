"""
Tests pour les modèles de l'application jobs
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import NewsletterLog, EmailTemplate, EmailQueue

class NewsletterLogModelTest(TestCase):
    """Tests pour le modèle NewsletterLog"""
    
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
            'title': "Test Campaign"
        })()
        
        self.subscriber = type('MockSubscriber', (), {
            'id': 1,
            'email': "subscriber@example.com"
        })()
    
    def test_newsletter_log_creation(self):
        """Test de la création d'un log de newsletter"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        # Vérifications
        self.assertEqual(log.campaign, self.campaign)
        self.assertEqual(log.subscriber, self.subscriber)
        self.assertEqual(log.status, 'pending')
        self.assertIsNone(log.sent_at)
        self.assertIsNone(log.opened_at)
        self.assertIsNone(log.clicked_at)
        self.assertEqual(log.retry_count, 0)
        self.assertIsNotNone(log.created_at)
        self.assertIsNotNone(log.updated_at)
    
    def test_newsletter_log_str_representation(self):
        """Test de la représentation string du log"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        expected_str = f"{self.campaign.title} - {self.subscriber.email} (En attente)"
        self.assertEqual(str(log), expected_str)
    
    def test_newsletter_log_status_choices(self):
        """Test des choix de statut disponibles"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        # Vérifier que le statut est valide
        self.assertIn(log.status, dict(NewsletterLog.STATUS_CHOICES).keys())
        
        # Tester différents statuts
        valid_statuses = ['pending', 'sending', 'sent', 'failed', 'bounced', 'opened', 'clicked']
        for status in valid_statuses:
            log.status = status
            log.save()
            log.refresh_from_db()
            self.assertEqual(log.status, status)
    
    def test_newsletter_log_mark_as_sent(self):
        """Test de la méthode mark_as_sent"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        # Marquer comme envoyé
        log.mark_as_sent()
        
        # Vérifications
        self.assertEqual(log.status, 'sent')
        self.assertIsNotNone(log.sent_at)
        self.assertEqual(log.sent_at.date(), timezone.now().date())
    
    def test_newsletter_log_mark_as_failed(self):
        """Test de la méthode mark_as_failed"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='pending'
        )
        
        initial_retry_count = log.retry_count
        
        # Marquer comme échoué
        error_message = "SMTP connection failed"
        log.mark_as_failed(error_message)
        
        # Vérifications
        self.assertEqual(log.status, 'failed')
        self.assertEqual(log.error_message, error_message)
        self.assertEqual(log.retry_count, initial_retry_count + 1)
    
    def test_newsletter_log_mark_as_opened(self):
        """Test de la méthode mark_as_opened"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='sent'
        )
        
        # Marquer comme ouvert
        log.mark_as_opened()
        
        # Vérifications
        self.assertEqual(log.status, 'opened')
        self.assertIsNotNone(log.opened_at)
        self.assertEqual(log.opened_at.date(), timezone.now().date())
        
        # Marquer à nouveau comme ouvert (ne devrait pas changer la date)
        original_opened_at = log.opened_at
        log.mark_as_opened()
        self.assertEqual(log.opened_at, original_opened_at)
    
    def test_newsletter_log_mark_as_clicked(self):
        """Test de la méthode mark_as_clicked"""
        log = NewsletterLog.objects.create(
            campaign=self.campaign,
            subscriber=self.subscriber,
            status='opened'
        )
        
        # Marquer comme cliqué
        log.mark_as_clicked()
        
        # Vérifications
        self.assertEqual(log.status, 'clicked')
        self.assertIsNotNone(log.clicked_at)
        self.assertEqual(log.clicked_at.date(), timezone.now().date())
        
        # Marquer à nouveau comme cliqué (ne devrait pas changer la date)
        original_clicked_at = log.clicked_at
        log.mark_as_clicked()
        self.assertEqual(log.clicked_at, original_clicked_at)
    
    def test_newsletter_log_meta_options(self):
        """Test des options Meta du modèle"""
        # Vérifier le nom verbose
        self.assertEqual(NewsletterLog._meta.verbose_name, "Log de newsletter")
        self.assertEqual(NewsletterLog._meta.verbose_name_plural, "Logs de newsletters")
        
        # Vérifier l'unicité
        unique_together = NewsletterLog._meta.unique_together
        self.assertIn(('campaign', 'subscriber'), unique_together)
        
        # Vérifier les index
        indexes = NewsletterLog._meta.indexes
        index_fields = [index.fields for index in indexes]
        self.assertIn(['status', 'created_at'], index_fields)
        self.assertIn(['campaign', 'status'], index_fields)
        self.assertIn(['subscriber', 'status'], index_fields)

class EmailTemplateModelTest(TestCase):
    """Tests pour le modèle EmailTemplate"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_template_creation(self):
        """Test de la création d'un template d'email"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1><p>Thank you for joining us.</p>',
            text_template='Welcome {{ name }}!\n\nThank you for joining us.'
        )
        
        # Vérifications
        self.assertEqual(template.name, 'welcome_email')
        self.assertEqual(template.subject_template, 'Welcome {{ name }}!')
        self.assertIn('<h1>Welcome {{ name }}!</h1>', template.html_template)
        self.assertIn('Welcome {{ name }}!', template.text_template)
        self.assertTrue(template.is_active)
        self.assertIsNotNone(template.created_at)
        self.assertIsNotNone(template.updated_at)
    
    def test_email_template_str_representation(self):
        """Test de la représentation string du template"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1>'
        )
        
        self.assertEqual(str(template), 'welcome_email')
    
    def test_email_template_get_subject(self):
        """Test de la méthode get_subject"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }} to {{ site_name }}!',
            html_template='<h1>Welcome {{ name }}!</h1>'
        )
        
        context = {'name': 'John', 'site_name': 'MySite'}
        subject = template.get_subject(context)
        
        self.assertEqual(subject, 'Welcome John to MySite!')
    
    def test_email_template_get_html_content(self):
        """Test de la méthode get_html_content"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1><p>You joined on {{ join_date }}.</p>'
        )
        
        context = {'name': 'John', 'join_date': '2024-01-01'}
        html_content = template.get_html_content(context)
        
        self.assertIn('<h1>Welcome John!</h1>', html_content)
        self.assertIn('<p>You joined on 2024-01-01.</p>', html_content)
    
    def test_email_template_get_text_content(self):
        """Test de la méthode get_text_content"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1>',
            text_template='Welcome {{ name }}!\n\nYou joined on {{ join_date }}.'
        )
        
        context = {'name': 'John', 'join_date': '2024-01-01'}
        text_content = template.get_text_content(context)
        
        self.assertIn('Welcome John!', text_content)
        self.assertIn('You joined on 2024-01-01.', text_content)
    
    def test_email_template_get_text_content_empty(self):
        """Test de la méthode get_text_content avec template texte vide"""
        template = EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1>',
            text_template=''
        )
        
        context = {'name': 'John'}
        text_content = template.get_text_content(context)
        
        self.assertEqual(text_content, '')
    
    def test_email_template_meta_options(self):
        """Test des options Meta du modèle"""
        # Vérifier le nom verbose
        self.assertEqual(EmailTemplate._meta.verbose_name, "Template d'email")
        self.assertEqual(EmailTemplate._meta.verbose_name_plural, "Templates d'emails")
        
        # Vérifier l'ordre
        self.assertEqual(EmailTemplate._meta.ordering, ['name'])
        
        # Vérifier l'unicité du nom
        self.assertTrue(EmailTemplate._meta.get_field('name').unique)
    
    def test_email_template_name_uniqueness(self):
        """Test de l'unicité du nom du template"""
        # Créer un premier template
        EmailTemplate.objects.create(
            name='welcome_email',
            subject_template='Welcome {{ name }}!',
            html_template='<h1>Welcome {{ name }}!</h1>'
        )
        
        # Essayer de créer un template avec le même nom
        with self.assertRaises(Exception):
            EmailTemplate.objects.create(
                name='welcome_email',
                subject_template='Another welcome email',
                html_template='<h1>Another welcome</h1>'
            )

class EmailQueueModelTest(TestCase):
    """Tests pour le modèle EmailQueue"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_queue_creation(self):
        """Test de la création d'un email en file d'attente"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1><p>This is a test email.</p>',
            text_content='Test\n\nThis is a test email.',
            priority=2
        )
        
        # Vérifications
        self.assertEqual(email_queue.to_email, 'recipient@example.com')
        self.assertEqual(email_queue.from_email, 'sender@example.com')
        self.assertEqual(email_queue.subject, 'Test Email')
        self.assertIn('<h1>Test</h1>', email_queue.html_content)
        self.assertIn('Test', email_queue.text_content)
        self.assertEqual(email_queue.priority, 2)
        self.assertEqual(email_queue.status, 'pending')
        self.assertEqual(email_queue.retry_count, 0)
        self.assertEqual(email_queue.max_retries, 3)
        self.assertIsNone(email_queue.scheduled_at)
        self.assertIsNone(email_queue.sent_at)
        self.assertIsNotNone(email_queue.created_at)
        self.assertIsNotNone(email_queue.updated_at)
    
    def test_email_queue_str_representation(self):
        """Test de la représentation string de l'email en file d'attente"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>'
        )
        
        expected_str = f"recipient@example.com - Test Email (En attente)"
        self.assertEqual(str(email_queue), expected_str)
    
    def test_email_queue_priority_choices(self):
        """Test des choix de priorité disponibles"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>'
        )
        
        # Vérifier que la priorité est valide
        self.assertIn(email_queue.priority, dict(EmailQueue.PRIORITY_CHOICES).keys())
        
        # Tester différentes priorités
        valid_priorities = [1, 2, 3, 4]
        for priority in valid_priorities:
            email_queue.priority = priority
            email_queue.save()
            email_queue.refresh_from_db()
            self.assertEqual(email_queue.priority, priority)
    
    def test_email_queue_status_choices(self):
        """Test des choix de statut disponibles"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>'
        )
        
        # Vérifier que le statut est valide
        self.assertIn(email_queue.status, dict(EmailQueue.STATUS_CHOICES).keys())
        
        # Tester différents statuts
        valid_statuses = ['pending', 'processing', 'sent', 'failed', 'cancelled']
        for status in valid_statuses:
            email_queue.status = status
            email_queue.save()
            email_queue.refresh_from_db()
            self.assertEqual(email_queue.status, status)
    
    def test_email_queue_can_be_sent_pending(self):
        """Test de la méthode can_be_sent pour un email en attente"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending'
        )
        
        self.assertTrue(email_queue.can_be_sent())
    
    def test_email_queue_can_be_sent_processing(self):
        """Test de la méthode can_be_sent pour un email en cours de traitement"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='processing'
        )
        
        self.assertFalse(email_queue.can_be_sent())
    
    def test_email_queue_can_be_sent_scheduled_future(self):
        """Test de la méthode can_be_sent pour un email programmé dans le futur"""
        future_time = timezone.now() + timedelta(hours=1)
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending',
            scheduled_at=future_time
        )
        
        self.assertFalse(email_queue.can_be_sent())
    
    def test_email_queue_can_be_sent_scheduled_past(self):
        """Test de la méthode can_be_sent pour un email programmé dans le passé"""
        past_time = timezone.now() - timedelta(hours=1)
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending',
            scheduled_at=past_time
        )
        
        self.assertTrue(email_queue.can_be_sent())
    
    def test_email_queue_can_be_sent_max_retries_exceeded(self):
        """Test de la méthode can_be_sent quand le nombre maximum de tentatives est dépassé"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending',
            retry_count=3,
            max_retries=3
        )
        
        self.assertFalse(email_queue.can_be_sent())
    
    def test_email_queue_mark_as_processing(self):
        """Test de la méthode mark_as_processing"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending'
        )
        
        # Marquer comme en cours de traitement
        email_queue.mark_as_processing()
        
        # Vérifications
        self.assertEqual(email_queue.status, 'processing')
    
    def test_email_queue_mark_as_sent(self):
        """Test de la méthode mark_as_sent"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='processing'
        )
        
        # Marquer comme envoyé
        email_queue.mark_as_sent()
        
        # Vérifications
        self.assertEqual(email_queue.status, 'sent')
        self.assertIsNotNone(email_queue.sent_at)
        self.assertEqual(email_queue.sent_at.date(), timezone.now().date())
    
    def test_email_queue_mark_as_failed(self):
        """Test de la méthode mark_as_failed"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='processing'
        )
        
        initial_retry_count = email_queue.retry_count
        
        # Marquer comme échoué
        error_message = "SMTP connection failed"
        email_queue.mark_as_failed(error_message)
        
        # Vérifications
        self.assertEqual(email_queue.status, 'failed')
        self.assertEqual(email_queue.error_message, error_message)
        self.assertEqual(email_queue.retry_count, initial_retry_count + 1)
    
    def test_email_queue_retry_success(self):
        """Test de la méthode retry avec succès"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='failed',
            retry_count=1,
            max_retries=3
        )
        
        # Remettre en file d'attente
        result = email_queue.retry()
        
        # Vérifications
        self.assertTrue(result)
        self.assertEqual(email_queue.status, 'pending')
        self.assertEqual(email_queue.error_message, '')
    
    def test_email_queue_retry_max_retries_exceeded(self):
        """Test de la méthode retry quand le nombre maximum de tentatives est dépassé"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='failed',
            retry_count=3,
            max_retries=3
        )
        
        # Essayer de remettre en file d'attente
        result = email_queue.retry()
        
        # Vérifications
        self.assertFalse(result)
        self.assertEqual(email_queue.status, 'failed')
    
    def test_email_queue_meta_options(self):
        """Test des options Meta du modèle"""
        # Vérifier le nom verbose
        self.assertEqual(EmailQueue._meta.verbose_name, "Email en file d'attente")
        self.assertEqual(EmailQueue._meta.verbose_name_plural, "Emails en file d'attente")
        
        # Vérifier l'ordre
        self.assertEqual(EmailQueue._meta.ordering, ['-priority', 'created_at'])
        
        # Vérifier les index
        indexes = EmailQueue._meta.indexes
        index_fields = [index.fields for index in indexes]
        self.assertIn(['status', 'priority', 'scheduled_at'], index_fields)
        self.assertIn(['to_email', 'status'], index_fields)
        self.assertIn(['created_at'], index_fields)

class ModelValidationTest(TestCase):
    """Tests pour la validation des modèles"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_template_name_required(self):
        """Test que le nom du template est requis"""
        with self.assertRaises(Exception):
            EmailTemplate.objects.create(
                subject_template='Test Subject',
                html_template='<h1>Test</h1>'
            )
    
    def test_email_template_html_template_required(self):
        """Test que le template HTML est requis"""
        with self.assertRaises(Exception):
            EmailTemplate.objects.create(
                name='test_template',
                subject_template='Test Subject'
            )
    
    def test_email_queue_to_email_required(self):
        """Test que l'email de destination est requis"""
        with self.assertRaises(Exception):
            EmailQueue.objects.create(
                from_email='sender@example.com',
                subject='Test Subject',
                html_content='<h1>Test</h1>'
            )
    
    def test_email_queue_from_email_required(self):
        """Test que l'email d'expédition est requis"""
        with self.assertRaises(Exception):
            EmailQueue.objects.create(
                to_email='recipient@example.com',
                subject='Test Subject',
                html_content='<h1>Test</h1>'
            )
    
    def test_email_queue_subject_required(self):
        """Test que le sujet est requis"""
        with self.assertRaises(Exception):
            EmailQueue.objects.create(
                to_email='recipient@example.com',
                from_email='sender@example.com',
                html_content='<h1>Test</h1>'
            )
    
    def test_email_queue_html_content_required(self):
        """Test que le contenu HTML est requis"""
        with self.assertRaises(Exception):
            EmailQueue.objects.create(
                to_email='recipient@example.com',
                from_email='sender@example.com',
                subject='Test Subject'
            )

class ModelRelationshipsTest(TestCase):
    """Tests pour les relations entre modèles"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_newsletter_log_campaign_relationship(self):
        """Test de la relation entre NewsletterLog et NewsletterCampaign"""
        # Créer une campagne simulée
        campaign = type('MockCampaign', (), {
            'id': 1,
            'title': "Test Campaign"
        })()
        
        # Créer un abonné simulé
        subscriber = type('MockSubscriber', (), {
            'id': 1,
            'email': "subscriber@example.com"
        })()
        
        # Créer un log
        log = NewsletterLog.objects.create(
            campaign=campaign,
            subscriber=subscriber,
            status='pending'
        )
        
        # Vérifier la relation
        self.assertEqual(log.campaign, campaign)
    
    def test_newsletter_log_subscriber_relationship(self):
        """Test de la relation entre NewsletterLog et Newsletter"""
        # Créer une campagne simulée
        campaign = type('MockCampaign', (), {
            'id': 1,
            'title': "Test Campaign"
        })()
        
        # Créer un abonné simulé
        subscriber = type('MockSubscriber', (), {
            'id': 1,
            'email': "subscriber@example.com"
        })()
        
        # Créer un log
        log = NewsletterLog.objects.create(
            campaign=campaign,
            subscriber=subscriber,
            status='pending'
        )
        
        # Vérifier la relation
        self.assertEqual(log.subscriber, subscriber)

class ModelMethodsTest(TestCase):
    """Tests pour les méthodes des modèles"""
    
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_template_context_rendering(self):
        """Test du rendu des templates avec contexte"""
        template = EmailTemplate.objects.create(
            name='test_template',
            subject_template='Hello {{ name }}!',
            html_template='<h1>Hello {{ name }}!</h1><p>Welcome to {{ site }}.</p>',
            text_template='Hello {{ name }}!\n\nWelcome to {{ site }}.'
        )
        
        context = {'name': 'John', 'site': 'MyWebsite'}
        
        # Tester le rendu du sujet
        subject = template.get_subject(context)
        self.assertEqual(subject, 'Hello John!')
        
        # Tester le rendu HTML
        html_content = template.get_html_content(context)
        self.assertIn('<h1>Hello John!</h1>', html_content)
        self.assertIn('<p>Welcome to MyWebsite.</p>', html_content)
        
        # Tester le rendu texte
        text_content = template.get_text_content(context)
        self.assertIn('Hello John!', text_content)
        self.assertIn('Welcome to MyWebsite.', text_content)
    
    def test_email_template_context_rendering_missing_variables(self):
        """Test du rendu des templates avec variables manquantes"""
        template = EmailTemplate.objects.create(
            name='test_template',
            subject_template='Hello {{ name }}!',
            html_template='<h1>Hello {{ name }}!</h1><p>Welcome to {{ site }}.</p>'
        )
        
        context = {'name': 'John'}  # 'site' manquant
        
        # Tester le rendu du sujet
        subject = template.get_subject(context)
        self.assertEqual(subject, 'Hello John!')
        
        # Tester le rendu HTML (les variables manquantes devraient être vides)
        html_content = template.get_html_content(context)
        self.assertIn('<h1>Hello John!</h1>', html_content)
        self.assertIn('<p>Welcome to .</p>', html_content)
    
    def test_email_queue_status_transitions(self):
        """Test des transitions de statut de l'email en file d'attente"""
        email_queue = EmailQueue.objects.create(
            to_email='recipient@example.com',
            from_email='sender@example.com',
            subject='Test Email',
            html_content='<h1>Test</h1>',
            status='pending'
        )
        
        # Transition: pending -> processing
        email_queue.mark_as_processing()
        self.assertEqual(email_queue.status, 'processing')
        
        # Transition: processing -> sent
        email_queue.mark_as_sent()
        self.assertEqual(email_queue.status, 'sent')
        self.assertIsNotNone(email_queue.sent_at)
    
    def test_newsletter_log_status_transitions(self):
        """Test des transitions de statut du log de newsletter"""
        # Créer des modèles simulés
        campaign = type('MockCampaign', (), {
            'id': 1,
            'title': "Test Campaign"
        })()
        
        subscriber = type('MockSubscriber', (), {
            'id': 1,
            'email': "subscriber@example.com"
        })()
        
        log = NewsletterLog.objects.create(
            campaign=campaign,
            subscriber=subscriber,
            status='pending'
        )
        
        # Transition: pending -> sent
        log.mark_as_sent()
        self.assertEqual(log.status, 'sent')
        self.assertIsNotNone(log.sent_at)
        
        # Transition: sent -> opened
        log.mark_as_opened()
        self.assertEqual(log.status, 'opened')
        self.assertIsNotNone(log.opened_at)
        
        # Transition: opened -> clicked
        log.mark_as_clicked()
        self.assertEqual(log.status, 'clicked')
        self.assertIsNotNone(log.clicked_at)

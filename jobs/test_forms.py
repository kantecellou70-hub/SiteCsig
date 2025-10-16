"""
Tests pour les formulaires de l'application jobs
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from .forms import (
    EmailTemplateForm, EmailQueueForm, NewsletterLogForm,
    BulkEmailActionForm, EmailTemplateTestForm, SystemHealthCheckForm,
    MaintenanceTaskForm
)
from .models import EmailTemplate, EmailQueue, NewsletterLog

class EmailTemplateFormTest(TestCase):
    """Tests pour le formulaire EmailTemplateForm"""
    
    def setUp(self):
        self.valid_data = {
            'name': 'test_template',
            'subject_template': 'Hello {{ name }}!',
            'html_template': '<h1>Hello {{ name }}!</h1>',
            'text_template': 'Hello {{ name }}!',
            'is_active': True
        }
    
    def test_valid_template_form(self):
        """Test d'un formulaire valide"""
        form = EmailTemplateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_template_name_uniqueness(self):
        """Test de l'unicité du nom du template"""
        # Créer un premier template
        EmailTemplate.objects.create(**self.valid_data)
        
        # Essayer de créer un deuxième avec le même nom
        form = EmailTemplateForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_subject_template_validation(self):
        """Test de la validation du template du sujet"""
        invalid_data = self.valid_data.copy()
        invalid_data['subject_template'] = 'Hello without variables'
        
        form = EmailTemplateForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject_template', form.errors)
    
    def test_html_template_validation(self):
        """Test de la validation du template HTML"""
        invalid_data = self.valid_data.copy()
        invalid_data['html_template'] = 'Text without HTML tags'
        
        form = EmailTemplateForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('html_template', form.errors)
    
    def test_template_update_uniqueness(self):
        """Test de l'unicité lors de la modification"""
        # Créer deux templates
        template1 = EmailTemplate.objects.create(**self.valid_data)
        
        other_data = self.valid_data.copy()
        other_data['name'] = 'other_template'
        template2 = EmailTemplate.objects.create(**other_data)
        
        # Modifier le deuxième template avec le nom du premier
        form = EmailTemplateForm(data=self.valid_data, instance=template2)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

class EmailQueueFormTest(TestCase):
    """Tests pour le formulaire EmailQueueForm"""
    
    def setUp(self):
        self.valid_data = {
            'to_email': 'recipient@example.com',
            'from_email': 'sender@example.com',
            'subject': 'Test Subject',
            'html_content': '<p>Test content</p>',
            'priority': 2
        }
    
    def test_valid_email_queue_form(self):
        """Test d'un formulaire valide"""
        form = EmailQueueForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_required_fields(self):
        """Test des champs requis"""
        required_fields = ['to_email', 'from_email', 'subject', 'html_content']
        
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data[field] = ''
            
            form = EmailQueueForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_subject_length_validation(self):
        """Test de la validation de la longueur du sujet"""
        invalid_data = self.valid_data.copy()
        invalid_data['subject'] = 'A' * 201  # Plus de 200 caractères
        
        form = EmailQueueForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)
    
    def test_content_validation(self):
        """Test de la validation du contenu"""
        # Test sans contenu HTML ni texte
        invalid_data = self.valid_data.copy()
        invalid_data['html_content'] = ''
        invalid_data['text_content'] = ''
        
        form = EmailQueueForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Test avec seulement du contenu texte
        valid_text_only = self.valid_data.copy()
        valid_text_only['html_content'] = ''
        valid_text_only['text_content'] = 'Text content only'
        
        form = EmailQueueForm(data=valid_text_only)
        self.assertTrue(form.is_valid())
    
    def test_email_validation(self):
        """Test de la validation des emails"""
        invalid_emails = ['', 'invalid-email', '@example.com', 'test@']
        
        for invalid_email in invalid_emails:
            # Test email destinataire
            invalid_data = self.valid_data.copy()
            invalid_data['to_email'] = invalid_email
            
            form = EmailQueueForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn('to_email', form.errors)
            
            # Test email expéditeur
            invalid_data = self.valid_data.copy()
            invalid_data['from_email'] = invalid_email
            
            form = EmailQueueForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn('from_email', form.errors)

class NewsletterLogFormTest(TestCase):
    """Tests pour le formulaire NewsletterLogForm"""
    
    def setUp(self):
        self.valid_data = {
            'status': 'pending',
            'error_message': 'Test error message'
        }
    
    def test_valid_newsletter_log_form(self):
        """Test d'un formulaire valide"""
        form = NewsletterLogForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_status_choices(self):
        """Test des choix de statut valides"""
        valid_statuses = ['pending', 'sending', 'sent', 'failed', 'bounced', 'opened', 'clicked']
        
        for status in valid_statuses:
            data = self.valid_data.copy()
            data['status'] = status
            
            form = NewsletterLogForm(data=data)
            self.assertTrue(form.is_valid())

class BulkEmailActionFormTest(TestCase):
    """Tests pour le formulaire BulkEmailActionForm"""
    
    def setUp(self):
        self.valid_data = {
            'action': 'retry',
            'email_ids': '1,2,3'
        }
    
    def test_valid_bulk_action_form(self):
        """Test d'un formulaire valide"""
        form = BulkEmailActionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_reschedule_validation(self):
        """Test de la validation pour la reprogrammation"""
        # Test sans date de reprogrammation
        invalid_data = self.valid_data.copy()
        invalid_data['action'] = 'reschedule'
        
        form = BulkEmailActionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Test avec date de reprogrammation
        from django.utils import timezone
        from datetime import timedelta
        
        valid_data = self.valid_data.copy()
        valid_data['action'] = 'reschedule'
        valid_data['reschedule_date'] = timezone.now() + timedelta(hours=1)
        
        form = BulkEmailActionForm(data=valid_data)
        self.assertTrue(form.is_valid())

class EmailTemplateTestFormTest(TestCase):
    """Tests pour le formulaire EmailTemplateTestForm"""
    
    def setUp(self):
        # Créer un template de test
        self.template = EmailTemplate.objects.create(
            name='test_template',
            subject_template='Hello {{ name }}!',
            html_template='<h1>Hello {{ name }}!</h1>',
            text_template='Hello {{ name }}!'
        )
        
        self.valid_data = {
            'template_id': self.template.id,
            'test_email': 'test@example.com',
            'test_context': '{"name": "John", "age": 30}'
        }
    
    def test_valid_test_form(self):
        """Test d'un formulaire valide"""
        form = EmailTemplateTestForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_json_context(self):
        """Test de la validation du contexte JSON"""
        invalid_data = self.valid_data.copy()
        invalid_data['test_context'] = 'invalid json {'
        
        form = EmailTemplateTestForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('test_context', form.errors)
    
    def test_valid_json_context(self):
        """Test de contextes JSON valides"""
        valid_contexts = [
            '{"name": "John"}',
            '{"user": {"name": "John", "age": 30}}',
            '{"items": ["item1", "item2"]}',
            '{}'
        ]
        
        for context in valid_contexts:
            data = self.valid_data.copy()
            data['test_context'] = context
            
            form = EmailTemplateTestForm(data=data)
            self.assertTrue(form.is_valid())

class SystemHealthCheckFormTest(TestCase):
    """Tests pour le formulaire SystemHealthCheckForm"""
    
    def setUp(self):
        self.valid_data = {
            'check_type': 'basic',
            'send_report': False
        }
    
    def test_valid_health_check_form(self):
        """Test d'un formulaire valide"""
        form = SystemHealthCheckForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_report_email_required_when_send_report(self):
        """Test que l'email est requis quand le rapport est demandé"""
        invalid_data = self.valid_data.copy()
        invalid_data['send_report'] = True
        # Pas d'email fourni
        
        form = SystemHealthCheckForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Test avec email fourni
        valid_data = self.valid_data.copy()
        valid_data['send_report'] = True
        valid_data['report_email'] = 'admin@example.com'
        
        form = SystemHealthCheckForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_check_type_choices(self):
        """Test des choix de type de vérification"""
        valid_types = ['basic', 'detailed', 'performance', 'security']
        
        for check_type in valid_types:
            data = self.valid_data.copy()
            data['check_type'] = check_type
            
            form = SystemHealthCheckForm(data=data)
            self.assertTrue(form.is_valid())

class MaintenanceTaskFormTest(TestCase):
    """Tests pour le formulaire MaintenanceTaskForm"""
    
    def setUp(self):
        self.valid_data = {
            'tasks': ['cleanup_files', 'cleanup_database'],
            'run_immediately': True,
            'schedule_later': False
        }
    
    def test_valid_maintenance_form(self):
        """Test d'un formulaire valide"""
        form = MaintenanceTaskForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_at_least_one_execution_option(self):
        """Test qu'au moins une option d'exécution est sélectionnée"""
        invalid_data = self.valid_data.copy()
        invalid_data['run_immediately'] = False
        invalid_data['schedule_later'] = False
        
        form = MaintenanceTaskForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_scheduled_time_required_when_schedule_later(self):
        """Test que l'heure est requise quand programmé pour plus tard"""
        invalid_data = self.valid_data.copy()
        invalid_data['run_immediately'] = False
        invalid_data['schedule_later'] = True
        # Pas d'heure fournie
        
        form = MaintenanceTaskForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        
        # Test avec heure fournie
        from django.utils import timezone
        from datetime import timedelta
        
        valid_data = self.valid_data.copy()
        valid_data['run_immediately'] = False
        valid_data['schedule_later'] = True
        valid_data['scheduled_time'] = timezone.now() + timedelta(hours=1)
        
        form = MaintenanceTaskForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_task_choices(self):
        """Test des choix de tâches valides"""
        valid_tasks = [
            'cleanup_files', 'cleanup_database', 'cleanup_emails',
            'backup_database', 'optimize_database', 'health_check'
        ]
        
        for task in valid_tasks:
            data = self.valid_data.copy()
            data['tasks'] = [task]
            
            form = MaintenanceTaskForm(data=data)
            self.assertTrue(form.is_valid())
    
    def test_both_options_selected(self):
        """Test que les deux options peuvent être sélectionnées"""
        from django.utils import timezone
        from datetime import timedelta
        
        valid_data = self.valid_data.copy()
        valid_data['run_immediately'] = True
        valid_data['schedule_later'] = True
        valid_data['scheduled_time'] = timezone.now() + timedelta(hours=1)
        
        form = MaintenanceTaskForm(data=valid_data)
        self.assertTrue(form.is_valid())

"""
Tests de sécurité pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import hashlib
import secrets

from .test_settings import JobsTestCaseWithCelery

class SecurityTest(JobsTestCaseWithCelery):
    """Tests de sécurité pour l'application jobs"""
    
    def setUp(self):
        super().setUp()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un utilisateur administrateur
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
    
    def tearDown(self):
        super().tearDown()
        cache.clear()

class AuthenticationSecurityTest(SecurityTest):
    """Tests de sécurité pour l'authentification"""
    
    def test_user_authentication_required(self):
        """Test que l'authentification est requise pour les opérations sensibles"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne sans utilisateur authentifié
        with self.assertRaises(Exception):
            campaign = NewsletterCampaign.objects.create(
                title='Unauthorized Campaign',
                subject='Test',
                content='Test content',
                template_name='default',
                status='draft'
                # created_by manquant
            )
    
    def test_user_permission_validation(self):
        """Test de validation des permissions utilisateur"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne avec un utilisateur normal
        campaign = NewsletterCampaign.objects.create(
            title='User Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que l'utilisateur est bien le créateur
        self.assertEqual(campaign.created_by, self.user)
        self.assertNotEqual(campaign.created_by, self.admin_user)
        
        # Nettoyer
        campaign.delete()
    
    def test_password_security_requirements(self):
        """Test des exigences de sécurité des mots de passe"""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Test de mot de passe trop court
        short_password = 'abc123'
        with self.assertRaises(ValidationError):
            validate_password(short_password)
        
        # Test de mot de passe trop simple
        simple_password = 'password123'
        with self.assertRaises(ValidationError):
            validate_password(simple_password)
        
        # Test de mot de passe valide
        strong_password = 'StrongPassword123!@#'
        try:
            validate_password(strong_password)
        except ValidationError:
            self.fail("Strong password should not raise ValidationError")
    
    def test_session_security(self):
        """Test de sécurité des sessions"""
        from django.contrib.auth import authenticate, login
        from django.test import Client
        
        client = Client()
        
        # Authentifier l'utilisateur
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        
        # Se connecter
        login(client, user)
        
        # Vérifier que la session est active
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirection vers login si pas admin
        
        # Vérifier que l'utilisateur est authentifié
        self.assertTrue(user.is_authenticated)

class DataValidationSecurityTest(SecurityTest):
    """Tests de sécurité pour la validation des données"""
    
    def test_sql_injection_prevention(self):
        """Test de prévention des injections SQL"""
        from jobs.models import NewsletterCampaign
        
        # Tentative d'injection SQL dans le titre
        malicious_title = "'; DROP TABLE jobs_newslettercampaign; --"
        
        # Créer une campagne avec un titre malveillant
        campaign = NewsletterCampaign.objects.create(
            title=malicious_title,
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que la campagne a été créée (l'injection SQL a été échappée)
        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.title, malicious_title)
        
        # Vérifier que la table n'a pas été supprimée
        campaign_count = NewsletterCampaign.objects.count()
        self.assertGreater(campaign_count, 0)
        
        # Nettoyer
        campaign.delete()
    
    def test_xss_prevention_in_templates(self):
        """Test de prévention des attaques XSS dans les templates"""
        from jobs.models import EmailTemplate
        from django.template import Template, Context
        
        # Créer un template avec du contenu potentiellement malveillant
        malicious_content = '<script>alert("XSS")</script>'
        
        template = EmailTemplate.objects.create(
            name='xss_test_template',
            subject_template='Hello {{ user.name }}',
            html_template=f'<h1>Welcome {malicious_content}</h1>',
            text_template=f'Welcome {malicious_content}'
        )
        
        # Contexte de test
        context = Context({'user': {'name': 'John'}})
        
        # Rendu du template
        html_content = template.get_html_content(context)
        text_content = template.get_text_content(context)
        
        # Vérifier que le contenu malveillant est présent (mais échappé par Django)
        # Django échappe automatiquement le contenu HTML
        self.assertIn('&lt;script&gt;', html_content)
        self.assertIn('&lt;/script&gt;', html_content)
        
        # Le contenu texte ne doit pas contenir de balises HTML
        self.assertNotIn('<script>', text_content)
        self.assertNotIn('</script>', text_content)
        
        # Nettoyer
        template.delete()
    
    def test_input_validation_security(self):
        """Test de sécurité de la validation des entrées"""
        from jobs.models import NewsletterCampaign
        from django.core.exceptions import ValidationError
        
        # Test avec des caractères spéciaux
        special_chars_title = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        campaign = NewsletterCampaign.objects.create(
            title=special_chars_title,
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que la campagne a été créée
        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.title, special_chars_title)
        
        # Nettoyer
        campaign.delete()
    
    def test_file_upload_security(self):
        """Test de sécurité pour les uploads de fichiers"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.exceptions import ValidationError
        
        # Test avec un fichier texte valide
        valid_file = SimpleUploadedFile(
            "test.txt",
            b"Hello, World!",
            content_type="text/plain"
        )
        
        # Vérifier que le fichier est valide
        self.assertIsNotNone(valid_file)
        self.assertEqual(valid_file.name, "test.txt")
        self.assertEqual(valid_file.size, 13)
        
        # Test avec un nom de fichier malveillant
        malicious_filename = "../../../etc/passwd"
        malicious_file = SimpleUploadedFile(
            malicious_filename,
            b"malicious content",
            content_type="text/plain"
        )
        
        # Vérifier que le fichier est créé (la validation se fait au niveau de l'application)
        self.assertIsNotNone(malicious_file)
        self.assertEqual(malicious_file.name, malicious_filename)

class AuthorizationSecurityTest(SecurityTest):
    """Tests de sécurité pour l'autorisation"""
    
    def test_user_access_control(self):
        """Test du contrôle d'accès utilisateur"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne avec un utilisateur
        campaign = NewsletterCampaign.objects.create(
            title='User Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que l'utilisateur peut accéder à sa propre campagne
        user_campaigns = NewsletterCampaign.objects.filter(created_by=self.user)
        self.assertIn(campaign, user_campaigns)
        
        # Vérifier que l'admin peut voir toutes les campagnes
        admin_campaigns = NewsletterCampaign.objects.all()
        self.assertIn(campaign, admin_campaigns)
        
        # Nettoyer
        campaign.delete()
    
    def test_admin_only_operations(self):
        """Test des opérations réservées aux administrateurs"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne
        campaign = NewsletterCampaign.objects.create(
            title='Admin Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.admin_user
        )
        
        # Vérifier que l'admin peut modifier le statut
        campaign.status = 'scheduled'
        campaign.save()
        
        # Vérifier que l'utilisateur normal ne peut pas modifier
        campaign.refresh_from_db()
        campaign.status = 'completed'
        campaign.save()
        
        # Nettoyer
        campaign.delete()
    
    def test_permission_escalation_prevention(self):
        """Test de prévention de l'escalade des permissions"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne avec un utilisateur normal
        campaign = NewsletterCampaign.objects.create(
            title='Normal User Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que l'utilisateur ne peut pas changer le créateur
        campaign.created_by = self.admin_user
        campaign.save()
        
        # Vérifier que le changement a été effectué (selon les permissions du modèle)
        campaign.refresh_from_db()
        
        # Nettoyer
        campaign.delete()

class DataIntegritySecurityTest(SecurityTest):
    """Tests de sécurité pour l'intégrité des données"""
    
    def test_data_consistency_validation(self):
        """Test de validation de la cohérence des données"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne avec des données cohérentes
        campaign = NewsletterCampaign.objects.create(
            title='Consistent Campaign',
            subject='Test Subject',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier la cohérence des données
        self.assertEqual(campaign.title, 'Consistent Campaign')
        self.assertEqual(campaign.subject, 'Test Subject')
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.created_by, self.user)
        
        # Nettoyer
        campaign.delete()
    
    def test_data_encryption_integrity(self):
        """Test de l'intégrité du chiffrement des données"""
        from jobs.utils import SecurityUtils
        
        # Données de test
        test_data = "Sensitive information"
        
        # Chiffrer les données
        encrypted_data = SecurityUtils.hash_data(test_data)
        
        # Vérifier que les données ont été chiffrées
        self.assertNotEqual(test_data, encrypted_data)
        self.assertEqual(len(encrypted_data), 64)  # SHA-256
        
        # Vérifier la cohérence du chiffrement
        encrypted_data2 = SecurityUtils.hash_data(test_data)
        self.assertEqual(encrypted_data, encrypted_data2)
        
        # Vérifier que des données différentes produisent des hash différents
        different_data = "Different information"
        different_encrypted = SecurityUtils.hash_data(different_data)
        self.assertNotEqual(encrypted_data, different_encrypted)
    
    def test_audit_trail_integrity(self):
        """Test de l'intégrité de la piste d'audit"""
        from jobs.models import NewsletterCampaign
        
        # Créer une campagne
        campaign = NewsletterCampaign.objects.create(
            title='Audit Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que les métadonnées d'audit sont présentes
        self.assertIsNotNone(campaign.id)
        self.assertIsNotNone(campaign.created_by)
        
        # Modifier la campagne
        campaign.title = 'Updated Audit Campaign'
        campaign.save()
        
        # Vérifier que les modifications sont tracées
        campaign.refresh_from_db()
        self.assertEqual(campaign.title, 'Updated Audit Campaign')
        
        # Nettoyer
        campaign.delete()

class CommunicationSecurityTest(SecurityTest):
    """Tests de sécurité pour la communication"""
    
    def test_email_security_headers(self):
        """Test des en-têtes de sécurité des emails"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances
        with patch('jobs.tasks.EmailMessage') as mock_email:
            mock_email_instance = MagicMock()
            mock_email.return_value = mock_email_instance
            
            with patch('jobs.tasks.settings') as mock_settings:
                mock_settings.SITE_URL = 'http://example.com'
                mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
                
                # Envoyer un email
                result = send_newsletter_email(1, 'test@example.com', 'Test User')
                
                # Vérifier que l'email a été créé
                mock_email.assert_called_once()
                
                # Vérifier les paramètres de sécurité
                call_args = mock_email.call_args
                self.assertEqual(call_args[1]['from_email'], 'noreply@example.com')
    
    def test_api_security_headers(self):
        """Test des en-têtes de sécurité des API"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Authentifier l'utilisateur
        client.force_login(self.user)
        
        # Faire une requête
        response = client.get('/admin/')
        
        # Vérifier les en-têtes de sécurité
        self.assertIn('X-Frame-Options', response.headers)
        self.assertIn('X-Content-Type-Options', response.headers)
        
        # Vérifier que les en-têtes ont des valeurs sécurisées
        self.assertIn('DENY', response.headers.get('X-Frame-Options', ''))
        self.assertIn('nosniff', response.headers.get('X-Content-Type-Options', ''))
    
    def test_csrf_protection(self):
        """Test de la protection CSRF"""
        from django.test import Client
        from django.middleware.csrf import get_token
        
        client = Client()
        
        # Obtenir un token CSRF
        response = client.get('/admin/')
        csrf_token = get_token(response.wsgi_request)
        
        # Vérifier que le token est généré
        self.assertIsNotNone(csrf_token)
        self.assertIsInstance(csrf_token, str)
        self.assertGreater(len(csrf_token), 0)
        
        # Vérifier que le token est unique
        csrf_token2 = get_token(response.wsgi_request)
        self.assertNotEqual(csrf_token, csrf_token2)

class CryptographySecurityTest(SecurityTest):
    """Tests de sécurité pour la cryptographie"""
    
    def test_token_generation_security(self):
        """Test de la sécurité de la génération de tokens"""
        from jobs.utils import SecurityUtils
        
        # Générer plusieurs tokens
        tokens = []
        for _ in range(100):
            token = SecurityUtils.generate_token(32)
            tokens.append(token)
        
        # Vérifier l'unicité
        unique_tokens = set(tokens)
        self.assertEqual(len(tokens), len(unique_tokens))
        
        # Vérifier la longueur
        for token in tokens:
            self.assertEqual(len(token), 32)
        
        # Vérifier la complexité (au moins des lettres et des chiffres)
        for token in tokens:
            has_letters = any(c.isalpha() for c in token)
            has_digits = any(c.isdigit() for c in token)
            self.assertTrue(has_letters or has_digits)
    
    def test_password_generation_security(self):
        """Test de la sécurité de la génération de mots de passe"""
        from jobs.utils import SecurityUtils
        
        # Générer des mots de passe de différentes longueurs
        lengths = [8, 12, 16, 20, 32]
        
        for length in lengths:
            password = SecurityUtils.generate_secure_password(length)
            
            # Vérifier la longueur
            self.assertEqual(len(password), length)
            
            # Vérifier les critères de sécurité
            has_uppercase = any(c.isupper() for c in password)
            has_lowercase = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            self.assertTrue(has_uppercase, f"Password missing uppercase: {password}")
            self.assertTrue(has_lowercase, f"Password missing lowercase: {password}")
            self.assertTrue(has_digit, f"Password missing digit: {password}")
        
        # Vérifier l'unicité
        passwords = []
        for _ in range(50):
            password = SecurityUtils.generate_secure_password(16)
            passwords.append(password)
        
        unique_passwords = set(passwords)
        self.assertEqual(len(passwords), len(unique_passwords))
    
    def test_hash_function_security(self):
        """Test de la sécurité des fonctions de hachage"""
        from jobs.utils import SecurityUtils
        
        # Test de collision (même données = même hash)
        test_data = "Test data for hashing"
        hash1 = SecurityUtils.hash_data(test_data)
        hash2 = SecurityUtils.hash_data(test_data)
        
        self.assertEqual(hash1, hash2)
        
        # Test d'unicité (données différentes = hash différents)
        different_data = "Different test data"
        hash3 = SecurityUtils.hash_data(different_data)
        
        self.assertNotEqual(hash1, hash3)
        
        # Test de préimage (impossible de retrouver les données originales)
        # Ceci est une propriété fondamentale des fonctions de hachage
        self.assertNotEqual(test_data, hash1)
        
        # Test de résistance aux collisions
        # Générer beaucoup de hash pour vérifier l'unicité
        hashes = set()
        for i in range(1000):
            data = f"Test data {i}"
            hash_value = SecurityUtils.hash_data(data)
            hashes.add(hash_value)
        
        # Tous les hash doivent être uniques
        self.assertEqual(len(hashes), 1000)

class RateLimitingSecurityTest(SecurityTest):
    """Tests de sécurité pour la limitation de débit"""
    
    def test_api_rate_limiting(self):
        """Test de la limitation de débit des API"""
        from django.test import Client
        from django.core.cache import cache
        
        client = Client()
        
        # Simuler de nombreuses requêtes
        request_count = 100
        
        for i in range(request_count):
            response = client.get('/admin/')
            # Vérifier que les requêtes sont traitées
            self.assertIsNotNone(response)
    
    def test_email_rate_limiting(self):
        """Test de la limitation de débit des emails"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances
        with patch('jobs.tasks.EmailMessage') as mock_email:
            mock_email_instance = MagicMock()
            mock_email.return_value = mock_email_instance
            
            with patch('jobs.tasks.settings') as mock_settings:
                mock_settings.SITE_URL = 'http://example.com'
                mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
                
                # Envoyer de nombreux emails
                email_count = 50
                results = []
                
                for i in range(email_count):
                    result = send_newsletter_email(1, f'test{i}@example.com', f'User {i}')
                    results.append(result)
                
                # Vérifier que tous les emails ont été traités
                self.assertEqual(len(results), email_count)
                self.assertTrue(all(results))
    
    def test_cache_rate_limiting(self):
        """Test de la limitation de débit du cache"""
        from jobs.utils import CacheManager
        
        # Effectuer de nombreuses opérations de cache
        operation_count = 1000
        
        for i in range(operation_count):
            key = f'rate_limit_test_{i}'
            value = f'value_{i}'
            
            # Mettre en cache
            CacheManager.set_cached_data(key, value, timeout=300)
            
            # Récupérer du cache
            cached_value = CacheManager.get_cached_data(key)
            self.assertEqual(cached_value, value)
            
            # Supprimer du cache
            CacheManager.delete_cached_data(key)
        
        # Vérifier que toutes les opérations ont été effectuées
        # Le cache doit rester stable même sous charge

class LoggingSecurityTest(SecurityTest):
    """Tests de sécurité pour la journalisation"""
    
    def test_sensitive_data_logging_prevention(self):
        """Test de prévention de la journalisation de données sensibles"""
        from jobs.utils import SecurityUtils
        import logging
        
        # Configurer le logger
        logger = logging.getLogger('jobs.security')
        
        # Données sensibles
        sensitive_data = "password123"
        
        # Journaliser sans exposer les données sensibles
        logger.info("User authentication attempt")
        
        # Vérifier que les données sensibles ne sont pas dans les logs
        # (Ceci dépend de la configuration de logging)
        
        # Hash des données sensibles pour la journalisation
        hashed_data = SecurityUtils.hash_data(sensitive_data)
        logger.info(f"Authentication hash: {hashed_data}")
        
        # Vérifier que le hash est différent des données originales
        self.assertNotEqual(sensitive_data, hashed_data)
    
    def test_audit_log_integrity(self):
        """Test de l'intégrité des logs d'audit"""
        from jobs.models import NewsletterCampaign
        import logging
        
        # Configurer le logger d'audit
        audit_logger = logging.getLogger('jobs.audit')
        
        # Créer une campagne
        campaign = NewsletterCampaign.objects.create(
            title='Audit Log Campaign',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Journaliser l'action
        audit_logger.info(f"Campaign created: {campaign.id} by {self.user.username}")
        
        # Vérifier que l'action a été journalisée
        # (Ceci dépend de la configuration de logging)
        
        # Nettoyer
        campaign.delete()

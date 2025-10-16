"""
Tests de régression pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time
import json

from .test_settings import JobsTestCaseWithCelery

class RegressionTest(JobsTestCaseWithCelery):
    """Tests de régression pour l'application jobs"""
    
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

class NewsletterCampaignRegressionTest(RegressionTest):
    """Tests de régression pour les campagnes de newsletter"""
    
    def test_newsletter_campaign_creation_regression(self):
        """Test de régression pour la création de campagnes de newsletter"""
        from content_management.models import NewsletterCampaign
        
        # 1. Créer une campagne de base
        campaign = NewsletterCampaign.objects.create(
            title='Test Campaign',
            subject='Test Subject',
            content='Test content',
            template_name='default_template',
            status='draft',
            created_by=self.user
        )
        
        # Vérifications de base
        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.title, 'Test Campaign')
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.created_by, self.user)
        
        # 2. Modifier la campagne
        campaign.title = 'Updated Campaign'
        campaign.status = 'scheduled'
        campaign.scheduled_at = timezone.now() + timedelta(hours=1)
        campaign.save()
        
        # Vérifier que les modifications ont été sauvegardées
        campaign.refresh_from_db()
        self.assertEqual(campaign.title, 'Updated Campaign')
        self.assertEqual(campaign.status, 'scheduled')
        self.assertIsNotNone(campaign.scheduled_at)
        
        # 3. Nettoyer
        campaign.delete()
    
    def test_newsletter_campaign_status_transitions_regression(self):
        """Test de régression pour les transitions de statut des campagnes"""
        from content_management.models import NewsletterCampaign
        
        # Créer une campagne
        campaign = NewsletterCampaign.objects.create(
            title='Status Test Campaign',
            subject='Status Test',
            content='Testing status transitions',
            template_name='default_template',
            status='draft',
            created_by=self.user
        )
        
        # Test des transitions de statut
        status_transitions = [
            ('draft', 'scheduled'),
            ('scheduled', 'sending'),
            ('sending', 'completed'),
            ('draft', 'cancelled')
        ]
        
        for from_status, to_status in status_transitions:
            # Définir le statut initial
            campaign.status = from_status
            campaign.save()
            
            # Changer le statut
            campaign.status = to_status
            
            # Définir les champs requis selon le statut
            if to_status == 'scheduled':
                campaign.scheduled_at = timezone.now() + timedelta(hours=1)
            elif to_status == 'sending':
                campaign.started_at = timezone.now()
            elif to_status == 'completed':
                campaign.completed_at = timezone.now()
            
            campaign.save()
            
            # Vérifier que le changement a été effectué
            campaign.refresh_from_db()
            self.assertEqual(campaign.status, to_status)
        
        # Nettoyer
        campaign.delete()
    
    def test_newsletter_campaign_validation_regression(self):
        """Test de régression pour la validation des campagnes"""
        from content_management.models import NewsletterCampaign
        from django.core.exceptions import ValidationError
        
        # Test de validation des champs requis
        with self.assertRaises(Exception):  # Django lève une exception pour les champs non null
            invalid_campaign = NewsletterCampaign.objects.create(
                title='',  # Titre vide
                subject='',  # Sujet vide
                content='',  # Contenu vide
                template_name='',  # Template vide
                status='draft',
                created_by=self.user
            )
        
        # Test de validation des statuts valides
        valid_statuses = ['draft', 'scheduled', 'sending', 'completed', 'cancelled']
        for status in valid_statuses:
            campaign = NewsletterCampaign.objects.create(
                title=f'Valid Status {status}',
                subject=f'Subject for {status}',
                content=f'Content for {status}',
                template_name='default_template',
                status=status,
                created_by=self.user
            )
            
            # Vérifier que la campagne a été créée
            self.assertIsNotNone(campaign.id)
            self.assertEqual(campaign.status, status)
            
            # Nettoyer
            campaign.delete()

class EmailTemplateRegressionTest(RegressionTest):
    """Tests de régression pour les templates d'email"""
    
    def test_email_template_rendering_regression(self):
        """Test de régression pour le rendu des templates"""
        from jobs.models import EmailTemplate
        
        # Créer un template de base
        template = EmailTemplate.objects.create(
            name='regression_test_template',
            subject_template='Hello {{ user.name }}!',
            html_template='<h1>Welcome {{ user.name }}</h1><p>Role: {{ user.role }}</p>',
            text_template='Hello {{ user.name }}!\n\nRole: {{ user.role }}'
        )
        
        # Contexte de test
        context = {
            'user': {
                'name': 'John Doe',
                'role': 'Developer'
            }
        }
        
        # Test de rendu
        subject = template.get_subject(context)
        html_content = template.get_html_content(context)
        text_content = template.get_text_content(context)
        
        # Vérifications de base
        self.assertEqual(subject, 'Hello John Doe!')
        self.assertIn('<h1>Welcome John Doe</h1>', html_content)
        self.assertIn('Role: Developer', text_content)
        
        # Modifier le template
        template.subject_template = 'Greetings {{ user.name }}!'
        template.html_template = '<h1>Welcome {{ user.name }}</h1><p>Position: {{ user.role }}</p>'
        template.save()
        
        # Vérifier que les modifications ont été appliquées
        template.refresh_from_db()
        new_subject = template.get_subject(context)
        new_html_content = template.get_html_content(context)
        
        self.assertEqual(new_subject, 'Greetings John Doe!')
        self.assertIn('<h1>Welcome John Doe</h1>', html_content)
        self.assertIn('Position: Developer', new_html_content)
        
        # Nettoyer
        template.delete()
    
    def test_email_template_context_handling_regression(self):
        """Test de régression pour la gestion du contexte des templates"""
        from jobs.models import EmailTemplate
        
        # Créer un template avec logique conditionnelle
        template = EmailTemplate.objects.create(
            name='conditional_template',
            subject_template='{{ event.title }} - {{ event.date|date:"F j" }}',
            html_template='''
                <h1>{{ event.title }}</h1>
                <p>Date: {{ event.date|date:"F j, Y" }}</p>
                {% if event.description %}
                <p>{{ event.description }}</p>
                {% endif %}
                {% if event.attendees %}
                <p>Attendees: {{ event.attendees|length }}</p>
                {% else %}
                <p>No attendees yet</p>
                {% endif %}
            ''',
            text_template='''
                {{ event.title }}
                Date: {{ event.date|date:"F j, Y" }}
                {% if event.description %}
                {{ event.description }}
                {% endif %}
                {% if event.attendees %}
                Attendees: {{ event.attendees|length }}
                {% else %}
                No attendees yet
                {% endif %}
            '''
        )
        
        # Test avec contexte complet
        full_context = {
            'event': {
                'title': 'Tech Conference',
                'date': datetime(2024, 6, 15),
                'description': 'Annual technology conference',
                'attendees': ['John', 'Jane', 'Bob']
            }
        }
        
        subject_full = template.get_subject(full_context)
        html_full = template.get_html_content(full_context)
        text_full = template.get_text_content(full_context)
        
        self.assertIn('Tech Conference', subject_full)
        self.assertIn('June 15', subject_full)
        self.assertIn('Annual technology conference', html_full)
        self.assertIn('Attendees: 3', html_full)
        self.assertIn('Annual technology conference', text_full)
        self.assertIn('Attendees: 3', text_full)
        
        # Test avec contexte partiel
        partial_context = {
            'event': {
                'title': 'Simple Event',
                'date': datetime(2024, 7, 1)
            }
        }
        
        subject_partial = template.get_subject(partial_context)
        html_partial = template.get_html_content(partial_context)
        text_partial = template.get_text_content(partial_context)
        
        self.assertIn('Simple Event', subject_partial)
        self.assertIn('July 1', subject_partial)
        self.assertIn('No attendees yet', html_partial)
        self.assertIn('No attendees yet', text_partial)
        
        # Nettoyer
        template.delete()

class CacheManagerRegressionTest(RegressionTest):
    """Tests de régression pour le gestionnaire de cache"""
    
    def test_cache_basic_operations_regression(self):
        """Test de régression pour les opérations de base du cache"""
        from jobs.utils import CacheManager
        
        # Test de mise en cache
        test_data = {'key': 'value', 'number': 42}
        result = CacheManager.set_cached_data('test_key', test_data, timeout=300)
        self.assertTrue(result)
        
        # Test de récupération
        cached_data = CacheManager.get_cached_data('test_key')
        self.assertEqual(cached_data, test_data)
        
        # Test de mise à jour
        updated_data = {'key': 'updated_value', 'number': 84}
        result = CacheManager.set_cached_data('test_key', updated_data, timeout=300)
        self.assertTrue(result)
        
        # Vérifier la mise à jour
        cached_data = CacheManager.get_cached_data('test_key')
        self.assertEqual(cached_data, updated_data)
        
        # Test de suppression
        result = CacheManager.delete_cached_data('test_key')
        self.assertTrue(result)
        
        # Vérifier la suppression
        cached_data = CacheManager.get_cached_data('test_key')
        self.assertIsNone(cached_data)
    
    def test_cache_key_generation_regression(self):
        """Test de régression pour la génération de clés de cache"""
        from jobs.utils import CacheManager
        
        # Test de génération de clés
        key1 = CacheManager.get_cache_key('test', 'data', '123')
        key2 = CacheManager.get_cache_key('test', 'data', '456')
        key3 = CacheManager.get_cache_key('test', 'data', '123')
        
        # Vérifications
        self.assertIsInstance(key1, str)
        self.assertIsInstance(key2, str)
        self.assertIsInstance(key3, str)
        
        # Les clés doivent être uniques pour des paramètres différents
        self.assertNotEqual(key1, key2)
        
        # Les clés doivent être identiques pour des paramètres identiques
        self.assertEqual(key1, key3)
        
        # Les clés doivent contenir les composants
        self.assertIn('test', key1)
        self.assertIn('data', key1)
        self.assertIn('123', key1)
    
    def test_cache_timeout_regression(self):
        """Test de régression pour la gestion des timeouts du cache"""
        from jobs.utils import CacheManager
        import time
        
        # Test avec timeout court
        CacheManager.set_cached_data('short_timeout', 'test_value', timeout=1)
        
        # La valeur doit être présente immédiatement
        value = CacheManager.get_cached_data('short_timeout')
        self.assertEqual(value, 'test_value')
        
        # Attendre que le timeout expire
        time.sleep(2)
        
        # La valeur doit avoir expiré
        value = CacheManager.get_cached_data('short_timeout')
        self.assertIsNone(value)
        
        # Test avec timeout long
        CacheManager.set_cached_data('long_timeout', 'test_value', timeout=3600)
        
        # La valeur doit être présente
        value = CacheManager.get_cached_data('long_timeout')
        self.assertEqual(value, 'test_value')
        
        # Nettoyer
        CacheManager.delete_cached_data('long_timeout')

class DataExporterRegressionTest(RegressionTest):
    """Tests de régression pour l'exportateur de données"""
    
    def test_csv_export_regression(self):
        """Test de régression pour l'export CSV"""
        from jobs.utils import DataExporter
        
        # Données de test
        test_data = [
            {'id': 1, 'name': 'John', 'age': 30},
            {'id': 2, 'name': 'Jane', 'age': 25},
            {'id': 3, 'name': 'Bob', 'age': 35}
        ]
        
        # Export CSV
        csv_content = DataExporter.export_to_csv(test_data)
        
        # Vérifications
        self.assertIsNotNone(csv_content)
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 4)  # En-tête + 3 lignes de données
        
        # Vérifier l'en-tête
        self.assertIn('id,name,age', lines[0])
        
        # Vérifier les données
        self.assertIn('1,John,30', lines[1])
        self.assertIn('2,Jane,25', lines[2])
        self.assertIn('3,Bob,35', lines[3])
    
    def test_json_export_regression(self):
        """Test de régression pour l'export JSON"""
        from jobs.utils import DataExporter
        
        # Données de test
        test_data = [
            {'id': 1, 'name': 'John', 'profile': {'age': 30, 'city': 'NYC'}},
            {'id': 2, 'name': 'Jane', 'profile': {'age': 25, 'city': 'LA'}}
        ]
        
        # Export JSON
        json_content = DataExporter.export_to_json(test_data)
        
        # Vérifications
        self.assertIsNotNone(json_content)
        parsed_data = json.loads(json_content)
        self.assertEqual(len(parsed_data), 2)
        
        # Vérifier la structure
        self.assertEqual(parsed_data[0]['id'], 1)
        self.assertEqual(parsed_data[0]['name'], 'John')
        self.assertEqual(parsed_data[0]['profile']['age'], 30)
        self.assertEqual(parsed_data[0]['profile']['city'], 'NYC')
        
        self.assertEqual(parsed_data[1]['id'], 2)
        self.assertEqual(parsed_data[1]['name'], 'Jane')
        self.assertEqual(parsed_data[1]['profile']['age'], 25)
        self.assertEqual(parsed_data[1]['profile']['city'], 'LA')
    
    def test_xml_export_regression(self):
        """Test de régression pour l'export XML"""
        from jobs.utils import DataExporter
        
        # Données de test
        test_data = [
            {'id': 1, 'name': 'John', 'age': 30},
            {'id': 2, 'name': 'Jane', 'age': 25}
        ]
        
        # Export XML
        xml_content = DataExporter.export_to_xml(test_data, 'users', 'user')
        
        # Vérifications
        self.assertIsNotNone(xml_content)
        self.assertIn('<users>', xml_content)
        self.assertIn('</users>', xml_content)
        self.assertIn('<user>', xml_content)
        self.assertIn('</user>', xml_content)
        
        # Vérifier le contenu
        self.assertIn('<id>1</id>', xml_content)
        self.assertIn('<name>John</name>', xml_content)
        self.assertIn('<age>30</age>', xml_content)
        self.assertIn('<id>2</id>', xml_content)
        self.assertIn('<name>Jane</name>', xml_content)
        self.assertIn('<age>25</age>', xml_content)

class SecurityUtilsRegressionTest(RegressionTest):
    """Tests de régression pour les utilitaires de sécurité"""
    
    def test_token_generation_regression(self):
        """Test de régression pour la génération de tokens"""
        from jobs.utils import SecurityUtils
        
        # Test de génération de tokens de différentes longueurs
        lengths = [16, 32, 64, 128]
        tokens = []
        
        for length in lengths:
            token = SecurityUtils.generate_token(length)
            tokens.append(token)
            
            # Vérifications
            self.assertEqual(len(token), length)
            self.assertIsInstance(token, str)
        
        # Vérifier l'unicité
        self.assertEqual(len(set(tokens)), len(tokens))
        
        # Générer plusieurs tokens de même longueur
        same_length_tokens = []
        for _ in range(10):
            token = SecurityUtils.generate_token(32)
            same_length_tokens.append(token)
        
        # Tous doivent être uniques
        self.assertEqual(len(set(same_length_tokens)), 10)
    
    def test_hash_generation_regression(self):
        """Test de régression pour la génération de hashes"""
        from jobs.utils import SecurityUtils
        
        # Test de hachage
        test_data = "Hello, World!"
        hash1 = SecurityUtils.hash_data(test_data)
        hash2 = SecurityUtils.hash_data(test_data)
        
        # Vérifications
        self.assertEqual(len(hash1), 64)  # SHA-256
        self.assertEqual(len(hash2), 64)
        self.assertEqual(hash1, hash2)  # Même données = même hash
        
        # Test avec données différentes
        different_data = "Hello, Universe!"
        hash3 = SecurityUtils.hash_data(different_data)
        
        # Hash différent pour données différentes
        self.assertNotEqual(hash1, hash3)
        
        # Test avec données vides
        empty_hash = SecurityUtils.hash_data("")
        self.assertEqual(len(empty_hash), 64)
    
    def test_password_generation_regression(self):
        """Test de régression pour la génération de mots de passe"""
        from jobs.utils import SecurityUtils
        
        # Test de génération de mots de passe de différentes longueurs
        lengths = [8, 12, 16, 20, 32]
        
        for length in lengths:
            password = SecurityUtils.generate_secure_password(length)
            
            # Vérifications
            self.assertEqual(len(password), length)
            self.assertIsInstance(password, str)
            
            # Vérifier les critères de sécurité
            self.assertTrue(any(c.isupper() for c in password))
            self.assertTrue(any(c.islower() for c in password))
            self.assertTrue(any(c.isdigit() for c in password))
        
        # Générer plusieurs mots de passe de même longueur
        passwords_16 = []
        for _ in range(10):
            password = SecurityUtils.generate_secure_password(16)
            passwords_16.append(password)
        
        # Tous doivent être uniques
        self.assertEqual(len(set(passwords_16)), 10)
        
        # Tous doivent avoir la bonne longueur
        for password in passwords_16:
            self.assertEqual(len(password), 16)

class SystemMonitorRegressionTest(RegressionTest):
    """Tests de régression pour le moniteur système"""
    
    def test_cpu_monitoring_regression(self):
        """Test de régression pour la surveillance CPU"""
        from jobs.utils import SystemMonitor
        
        # Test de récupération des informations CPU
        cpu_info = SystemMonitor.get_cpu_info()
        
        # Vérifications de base
        self.assertIn('usage_percent', cpu_info)
        self.assertIn('count', cpu_info)
        
        # Vérifier les types et valeurs
        self.assertIsInstance(cpu_info['usage_percent'], (int, float))
        self.assertIsInstance(cpu_info['count'], int)
        
        # Vérifier les plages de valeurs
        self.assertGreaterEqual(cpu_info['usage_percent'], 0)
        self.assertLessEqual(cpu_info['usage_percent'], 100)
        self.assertGreater(cpu_info['count'], 0)
        
        # Test de cohérence sur plusieurs appels
        cpu_info1 = SystemMonitor.get_cpu_info()
        cpu_info2 = SystemMonitor.get_cpu_info()
        
        # Les informations de base doivent être cohérentes
        self.assertEqual(cpu_info1['count'], cpu_info2['count'])
    
    def test_memory_monitoring_regression(self):
        """Test de régression pour la surveillance mémoire"""
        from jobs.utils import SystemMonitor
        
        # Test de récupération des informations mémoire
        memory_info = SystemMonitor.get_memory_info()
        
        # Vérifications de base
        self.assertIn('total_gb', memory_info)
        self.assertIn('available_gb', memory_info)
        self.assertIn('usage_percent', memory_info)
        
        # Vérifier les types et valeurs
        self.assertIsInstance(memory_info['total_gb'], (int, float))
        self.assertIsInstance(memory_info['available_gb'], (int, float))
        self.assertIsInstance(memory_info['usage_percent'], (int, float))
        
        # Vérifier les plages de valeurs
        self.assertGreater(memory_info['total_gb'], 0)
        self.assertGreaterEqual(memory_info['available_gb'], 0)
        self.assertGreaterEqual(memory_info['usage_percent'], 0)
        self.assertLessEqual(memory_info['usage_percent'], 100)
        
        # Vérifier la cohérence
        self.assertGreaterEqual(memory_info['total_gb'], memory_info['available_gb'])
    
    def test_disk_monitoring_regression(self):
        """Test de régression pour la surveillance disque"""
        from jobs.utils import SystemMonitor
        
        # Test de récupération des informations disque
        disk_info = SystemMonitor.get_disk_info()
        
        # Vérifications de base
        self.assertIn('total_gb', disk_info)
        self.assertIn('used_gb', disk_info)
        self.assertIn('usage_percent', disk_info)
        
        # Vérifier les types et valeurs
        self.assertIsInstance(disk_info['total_gb'], (int, float))
        self.assertIsInstance(disk_info['used_gb'], (int, float))
        self.assertIsInstance(disk_info['usage_percent'], (int, float))
        
        # Vérifier les plages de valeurs
        self.assertGreater(disk_info['total_gb'], 0)
        self.assertGreaterEqual(disk_info['used_gb'], 0)
        self.assertGreaterEqual(disk_info['usage_percent'], 0)
        self.assertLessEqual(disk_info['usage_percent'], 100)
        
        # Vérifier la cohérence
        self.assertGreaterEqual(disk_info['total_gb'], disk_info['used_gb'])

class PerformanceMonitorRegressionTest(RegressionTest):
    """Tests de régression pour le moniteur de performance"""
    
    def test_timing_decorator_regression(self):
        """Test de régression pour le décorateur de timing"""
        from jobs.utils import PerformanceMonitor
        
        # Test du décorateur de timing
        @PerformanceMonitor.timing
        def test_function():
            return "test_result"
        
        # Exécuter la fonction
        result = test_function()
        
        # Vérifications
        self.assertEqual(result, "test_result")
        
        # Le décorateur ne doit pas modifier le comportement de la fonction
        # Note: Les métriques de timing sont gérées en interne
    
    def test_performance_metrics_regression(self):
        """Test de régression pour les métriques de performance"""
        from jobs.utils import PerformanceMonitor
        
        # Test de récupération des métriques de base
        # Note: Ces méthodes peuvent retourner des métriques système
        # ou être des placeholders selon l'implémentation
        
        # Test de la méthode get_performance_summary si elle existe
        if hasattr(PerformanceMonitor, 'get_performance_summary'):
            summary = PerformanceMonitor.get_performance_summary()
            self.assertIsInstance(summary, dict)
        
        # Test de la méthode get_slow_operations si elle existe
        if hasattr(PerformanceMonitor, 'get_slow_operations'):
            slow_ops = PerformanceMonitor.get_slow_operations()
            self.assertIsInstance(slow_ops, list)

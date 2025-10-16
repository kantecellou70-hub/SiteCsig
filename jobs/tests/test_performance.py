"""
Tests de performance pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time
import psutil

from .test_settings import JobsTestCaseWithCelery

class PerformanceTest(JobsTestCaseWithCelery):
    """Tests de performance pour l'application jobs"""
    
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

class TaskPerformanceTest(PerformanceTest):
    """Tests de performance pour les tâches Celery"""
    
    def test_newsletter_email_send_performance(self):
        """Test de performance pour l'envoi d'email de newsletter"""
        from jobs.tasks import send_newsletter_email
        
        # Mock des dépendances
        with patch('jobs.tasks.EmailMessage') as mock_email:
            mock_email_instance = MagicMock()
            mock_email.return_value = mock_email_instance
            
            with patch('jobs.tasks.settings') as mock_settings:
                mock_settings.SITE_URL = 'http://example.com'
                mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
                
                # Mesurer le temps d'exécution
                start_time = time.time()
                
                # Exécuter la tâche
                result = send_newsletter_email(1, 'test@example.com', 'Test User')
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Vérifications
                self.assertTrue(result)
                self.assertLess(execution_time, 1.0)  # Moins d'1 seconde
    
    def test_bulk_newsletter_send_performance(self):
        """Test de performance pour l'envoi en masse de newsletters"""
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
                # Simuler différents nombres d'abonnés
                subscriber_counts = [10, 50, 100, 500]
                
                for count in subscriber_counts:
                    mock_subscribers = [
                        type('MockSubscriber', (), {
                            'email': f'subscriber{i}@example.com',
                            'name': f'Subscriber {i}'
                        })() for i in range(count)
                    ]
                    mock_filter.return_value = mock_subscribers
                    
                    with patch('jobs.tasks.send_newsletter_email.delay') as mock_send:
                        # Mesurer le temps d'exécution
                        start_time = time.time()
                        
                        # Exécuter la tâche
                        result = send_bulk_newsletter(1)
                        
                        end_time = time.time()
                        execution_time = end_time - start_time
                        
                        # Vérifications
                        self.assertTrue(result)
                        self.assertEqual(mock_send.call_count, count)
                        
                        # Vérifier que le temps d'exécution est raisonnable
                        # Plus d'abonnés = plus de temps, mais pas exponentiel
                        expected_max_time = 0.1 + (count * 0.001)  # 0.1s de base + 0.001s par abonné
                        self.assertLess(execution_time, expected_max_time)
    
    def test_email_queue_processing_performance(self):
        """Test de performance pour le traitement de la file d'attente d'emails"""
        from jobs.email_tasks import process_email_queue
        from jobs.models import EmailQueue
        
        # Créer différents nombres d'emails en file d'attente
        email_counts = [10, 50, 100, 500]
        
        for count in email_counts:
            # Créer des emails
            emails = []
            for i in range(count):
                email = EmailQueue.objects.create(
                    to_email=f'recipient{i}@example.com',
                    from_email='sender@example.com',
                    subject=f'Test Email {i}',
                    html_content=f'<h1>Test {i}</h1>'
                )
                emails.append(email)
            
            with patch('jobs.email_tasks.send_email_from_queue.delay') as mock_send:
                # Mesurer le temps d'exécution
                start_time = time.time()
                
                # Traiter la file d'attente
                process_email_queue()
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Vérifications
                self.assertEqual(mock_send.call_count, count)
                
                # Vérifier que le temps d'exécution est raisonnable
                expected_max_time = 0.1 + (count * 0.001)  # 0.1s de base + 0.001s par email
                self.assertLess(execution_time, expected_max_time)
            
            # Nettoyer les emails créés
            for email in emails:
                email.delete()

class CachePerformanceTest(PerformanceTest):
    """Tests de performance pour le cache"""
    
    def test_cache_operations_performance(self):
        """Test de performance pour les opérations de cache"""
        from jobs.utils import CacheManager
        
        # Test de mise en cache
        start_time = time.time()
        
        for i in range(1000):
            CacheManager.set_cached_data(f'key_{i}', f'value_{i}', timeout=300)
        
        set_time = time.time() - start_time
        
        # Test de récupération
        start_time = time.time()
        
        for i in range(1000):
            value = CacheManager.get_cached_data(f'key_{i}')
            self.assertEqual(value, f'value_{i}')
        
        get_time = time.time() - start_time
        
        # Vérifications de performance
        self.assertLess(set_time, 1.0)  # Moins d'1 seconde pour 1000 opérations
        self.assertLess(get_time, 1.0)  # Moins d'1 seconde pour 1000 opérations
        
        # Nettoyer le cache
        for i in range(1000):
            CacheManager.delete_cached_data(f'key_{i}')
    
    def test_cache_key_generation_performance(self):
        """Test de performance pour la génération de clés de cache"""
        from jobs.utils import CacheManager
        
        # Mesurer le temps de génération de nombreuses clés
        start_time = time.time()
        
        keys = []
        for i in range(10000):
            key = CacheManager.get_cache_key('test', str(i))
            keys.append(key)
        
        generation_time = time.time() - start_time
        
        # Vérifications
        self.assertEqual(len(keys), 10000)
        self.assertEqual(len(set(keys)), 10000)  # Toutes les clés sont uniques
        
        # Vérifier que la génération est rapide
        self.assertLess(generation_time, 0.1)  # Moins de 0.1 seconde pour 10000 clés

class SystemMonitoringPerformanceTest(PerformanceTest):
    """Tests de performance pour la surveillance système"""
    
    def test_system_health_check_performance(self):
        """Test de performance pour la vérification de santé du système"""
        from jobs.maintenance_tasks import check_system_health
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        health_status = check_system_health()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifications
        self.assertIn('timestamp', health_status)
        self.assertIn('overall_status', health_status)
        
        # Vérifier que la vérification est rapide
        self.assertLess(execution_time, 5.0)  # Moins de 5 secondes
    
    def test_system_monitor_methods_performance(self):
        """Test de performance pour les méthodes du moniteur système"""
        from jobs.utils import SystemMonitor
        
        # Test de performance pour get_cpu_info
        start_time = time.time()
        
        for _ in range(100):
            cpu_info = SystemMonitor.get_cpu_info()
            self.assertIn('usage_percent', cpu_info)
            self.assertIn('count', cpu_info)
        
        cpu_time = time.time() - start_time
        
        # Test de performance pour get_memory_info
        start_time = time.time()
        
        for _ in range(100):
            memory_info = SystemMonitor.get_memory_info()
            self.assertIn('total_gb', memory_info)
            self.assertIn('available_gb', memory_info)
        
        memory_time = time.time() - start_time
        
        # Test de performance pour get_disk_info
        start_time = time.time()
        
        for _ in range(100):
            disk_info = SystemMonitor.get_disk_info()
            self.assertIn('total_gb', disk_info)
            self.assertIn('used_gb', disk_info)
        
        disk_time = time.time() - start_time
        
        # Vérifications de performance
        self.assertLess(cpu_time, 1.0)      # Moins d'1 seconde pour 100 appels
        self.assertLess(memory_time, 1.0)   # Moins d'1 seconde pour 100 appels
        self.assertLess(disk_time, 1.0)     # Moins d'1 seconde pour 100 appels
    
    def test_performance_monitor_timing_performance(self):
        """Test de performance pour le moniteur de performance"""
        from jobs.utils import PerformanceMonitor
        
        # Test de performance pour le décorateur de timing
        @PerformanceMonitor.timing
        def fast_function():
            return "fast"
        
        @PerformanceMonitor.timing
        def slow_function():
            time.sleep(0.01)  # 10ms
            return "slow"
        
        # Mesurer le temps d'exécution avec le décorateur
        start_time = time.time()
        
        for _ in range(1000):
            result = fast_function()
            self.assertEqual(result, "fast")
        
        fast_time = time.time() - start_time
        
        start_time = time.time()
        
        for _ in range(100):
            result = slow_function()
            self.assertEqual(result, "slow")
        
        slow_time = time.time() - start_time
        
        # Vérifications de performance
        # Le décorateur ne devrait pas ajouter plus de 0.001s par appel
        overhead_per_call = (fast_time / 1000) - (0.001 / 1000)  # Temps par appel - 1ms
        self.assertLess(overhead_per_call, 0.001)  # Moins de 1ms d'overhead par appel
        
        # Le temps total pour les fonctions lentes devrait être principalement le temps de sommeil
        expected_slow_time = 100 * 0.01  # 100 appels * 10ms
        self.assertGreater(slow_time, expected_slow_time)
        self.assertLess(slow_time, expected_slow_time + 0.1)  # Avec une marge de 0.1s

class EmailTemplatePerformanceTest(PerformanceTest):
    """Tests de performance pour les templates d'email"""
    
    def test_template_rendering_performance(self):
        """Test de performance pour le rendu des templates"""
        from jobs.models import EmailTemplate
        
        # Créer un template complexe
        template = EmailTemplate.objects.create(
            name='performance_test_template',
            subject_template='Hello {{ user.name }} from {{ company.name }}!',
            html_template='''
                <h1>Welcome {{ user.name }}</h1>
                <p>Company: {{ company.name }}</p>
                <p>Role: {{ user.role }}</p>
                <p>Department: {{ user.department }}</p>
                <p>Location: {{ user.location }}</p>
                <p>Join Date: {{ user.join_date }}</p>
                <p>Manager: {{ user.manager.name if user.manager else 'None' }}</p>
                <p>Skills: {{ user.skills|join:', ' }}</p>
                <p>Projects: {{ user.projects|length }} active projects</p>
                <p>Last Login: {{ user.last_login|date:"F j, Y" }}</p>
            ''',
            text_template='''
                Welcome {{ user.name }} from {{ company.name }}!
                
                Role: {{ user.role }}
                Department: {{ user.department }}
                Location: {{ user.location }}
                Join Date: {{ user.join_date }}
                Manager: {{ user.manager.name if user.manager else 'None' }}
                Skills: {{ user.skills|join:', ' }}
                Projects: {{ user.projects|length }} active projects
                Last Login: {{ user.last_login|date:"F j, Y" }}
            '''
        )
        
        # Contexte complexe
        context = {
            'user': {
                'name': 'John Doe',
                'role': 'Senior Developer',
                'department': 'Engineering',
                'location': 'San Francisco',
                'join_date': '2020-01-15',
                'manager': {'name': 'Jane Smith'},
                'skills': ['Python', 'Django', 'React', 'PostgreSQL'],
                'projects': [1, 2, 3, 4, 5],
                'last_login': datetime.now()
            },
            'company': {
                'name': 'Tech Innovations Inc.'
            }
        }
        
        # Test de performance pour le rendu
        start_time = time.time()
        
        for _ in range(1000):
            subject = template.get_subject(context)
            html_content = template.get_html_content(context)
            text_content = template.get_text_content(context)
            
            # Vérifications de base
            self.assertIn('John Doe', subject)
            self.assertIn('Tech Innovations Inc.', subject)
            self.assertIn('<h1>Welcome John Doe</h1>', html_content)
            self.assertIn('Senior Developer', text_content)
        
        rendering_time = time.time() - start_time
        
        # Vérifications de performance
        self.assertLess(rendering_time, 2.0)  # Moins de 2 secondes pour 1000 rendus
        
        # Nettoyer
        template.delete()
    
    def test_template_rendering_with_large_context_performance(self):
        """Test de performance pour le rendu avec un contexte volumineux"""
        from jobs.models import EmailTemplate
        
        # Créer un template
        template = EmailTemplate.objects.create(
            name='large_context_template',
            subject_template='Report for {{ date }}',
            html_template='<h1>Report</h1><p>Items: {{ items|length }}</p>',
            text_template='Report\nItems: {{ items|length }}'
        )
        
        # Contexte volumineux
        large_context = {
            'date': '2024-01-01',
            'items': [f'Item {i}' for i in range(10000)]  # 10000 éléments
        }
        
        # Test de performance
        start_time = time.time()
        
        for _ in range(100):
            subject = template.get_subject(large_context)
            html_content = template.get_html_content(large_context)
            text_content = template.get_text_content(large_context)
            
            # Vérifications
            self.assertIn('2024-01-01', subject)
            self.assertIn('10000', html_content)
            self.assertIn('10000', text_content)
        
        rendering_time = time.time() - start_time
        
        # Vérifications de performance
        self.assertLess(rendering_time, 5.0)  # Moins de 5 secondes pour 100 rendus
        
        # Nettoyer
        template.delete()

class DataExportPerformanceTest(PerformanceTest):
    """Tests de performance pour l'export de données"""
    
    def test_csv_export_performance(self):
        """Test de performance pour l'export CSV"""
        from jobs.utils import DataExporter
        
        # Données de test de différentes tailles
        data_sizes = [100, 1000, 10000]
        
        for size in data_sizes:
            # Créer des données
            test_data = [
                {
                    'id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'age': 20 + (i % 50),
                    'city': f'City {i % 10}',
                    'department': f'Dept {i % 5}',
                    'salary': 30000 + (i * 100),
                    'start_date': f'2020-{(i % 12) + 1:02d}-01',
                    'is_active': bool(i % 2),
                    'last_login': f'2024-01-{(i % 28) + 1:02d}'
                }
                for i in range(size)
            ]
            
            # Test de performance
            start_time = time.time()
            
            csv_content = DataExporter.export_to_csv(test_data)
            
            export_time = time.time() - start_time
            
            # Vérifications
            self.assertIsNotNone(csv_content)
            lines = csv_content.strip().split('\n')
            self.assertEqual(len(lines), size + 1)  # +1 pour l'en-tête
            
            # Vérifier que l'export est rapide
            expected_max_time = 0.1 + (size * 0.00001)  # 0.1s de base + 0.00001s par ligne
            self.assertLess(export_time, expected_max_time)
    
    def test_json_export_performance(self):
        """Test de performance pour l'export JSON"""
        from jobs.utils import DataExporter
        import json
        
        # Données de test
        test_data = [
            {
                'id': i,
                'name': f'User {i}',
                'profile': {
                    'age': 20 + (i % 50),
                    'city': f'City {i % 10}',
                    'preferences': {
                        'theme': 'dark' if i % 2 else 'light',
                        'language': 'en' if i % 3 == 0 else 'fr' if i % 3 == 1 else 'es',
                        'notifications': bool(i % 2)
                    }
                },
                'metadata': {
                    'created_at': f'2020-{(i % 12) + 1:02d}-01',
                    'updated_at': f'2024-01-{(i % 28) + 1:02d}',
                    'version': f'1.{i % 10}.{i % 100}'
                }
            }
            for i in range(1000)
        ]
        
        # Test de performance
        start_time = time.time()
        
        json_content = DataExporter.export_to_json(test_data)
        
        export_time = time.time() - start_time
        
        # Vérifications
        self.assertIsNotNone(json_content)
        parsed_data = json.loads(json_content)
        self.assertEqual(len(parsed_data), 1000)
        
        # Vérifier que l'export est rapide
        self.assertLess(export_time, 1.0)  # Moins d'1 seconde
    
    def test_xml_export_performance(self):
        """Test de performance pour l'export XML"""
        from jobs.utils import DataExporter
        
        # Données de test
        test_data = [
            {
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'profile': {
                    'age': 20 + (i % 50),
                    'city': f'City {i % 10}'
                }
            }
            for i in range(1000)
        ]
        
        # Test de performance
        start_time = time.time()
        
        xml_content = DataExporter.export_to_xml(
            test_data, 
            root_name='users', 
            item_name='user'
        )
        
        export_time = time.time() - start_time
        
        # Vérifications
        self.assertIsNotNone(xml_content)
        self.assertIn('<users>', xml_content)
        self.assertIn('</users>', xml_content)
        self.assertIn('<user>', xml_content)
        self.assertIn('</user>', xml_content)
        
        # Vérifier que l'export est rapide
        self.assertLess(export_time, 2.0)  # Moins de 2 secondes

class SecurityUtilsPerformanceTest(PerformanceTest):
    """Tests de performance pour les utilitaires de sécurité"""
    
    def test_token_generation_performance(self):
        """Test de performance pour la génération de tokens"""
        from jobs.utils import SecurityUtils
        
        # Test de performance pour différentes longueurs
        lengths = [16, 32, 64, 128]
        
        for length in lengths:
            start_time = time.time()
            
            tokens = []
            for _ in range(1000):
                token = SecurityUtils.generate_token(length)
                tokens.append(token)
            
            generation_time = time.time() - start_time
            
            # Vérifications
            self.assertEqual(len(tokens), 1000)
            self.assertEqual(len(set(tokens)), 1000)  # Tous uniques
            
            for token in tokens:
                self.assertEqual(len(token), length)
            
            # Vérifier que la génération est rapide
            expected_max_time = 0.1 + (length * 0.0001)  # 0.1s de base + 0.0001s par caractère
            self.assertLess(generation_time, expected_max_time)
    
    def test_hash_generation_performance(self):
        """Test de performance pour la génération de hashes"""
        from jobs.utils import SecurityUtils
        
        # Données de test de différentes tailles
        data_sizes = [100, 1000, 10000, 100000]
        
        for size in data_sizes:
            # Créer des données
            test_data = 'A' * size
            
            start_time = time.time()
            
            hashes = []
            for _ in range(100):
                hash_value = SecurityUtils.hash_data(test_data)
                hashes.append(hash_value)
            
            hash_time = time.time() - start_time
            
            # Vérifications
            self.assertEqual(len(hashes), 100)
            self.assertEqual(len(set(hashes)), 100)  # Tous uniques
            
            for hash_value in hashes:
                self.assertEqual(len(hash_value), 64)  # SHA-256 = 64 caractères hex
            
            # Vérifier que le hachage est rapide
            expected_max_time = 0.1 + (size * 0.000001)  # 0.1s de base + 0.000001s par octet
            self.assertLess(hash_time, expected_max_time)
    
    def test_password_generation_performance(self):
        """Test de performance pour la génération de mots de passe"""
        from jobs.utils import SecurityUtils
        
        # Test de performance pour différentes longueurs
        lengths = [8, 12, 16, 20, 32]
        
        for length in lengths:
            start_time = time.time()
            
            passwords = []
            for _ in range(100):
                password = SecurityUtils.generate_secure_password(length)
                passwords.append(password)
            
            generation_time = time.time() - start_time
            
            # Vérifications
            self.assertEqual(len(passwords), 100)
            self.assertEqual(len(set(passwords)), 100)  # Tous uniques
            
            for password in passwords:
                self.assertEqual(len(password), length)
                # Vérifier les critères de sécurité
                self.assertTrue(any(c.isupper() for c in password))
                self.assertTrue(any(c.islower() for c in password))
                self.assertTrue(any(c.isdigit() for c in password))
            
            # Vérifier que la génération est rapide
            expected_max_time = 0.1 + (length * 0.001)  # 0.1s de base + 0.001s par caractère
            self.assertLess(generation_time, expected_max_time)

class MemoryUsageTest(PerformanceTest):
    """Tests d'utilisation mémoire"""
    
    def test_memory_usage_during_large_operations(self):
        """Test de l'utilisation mémoire pendant de grandes opérations"""
        import psutil
        import os
        
        # Obtenir l'utilisation mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer une opération qui utilise beaucoup de mémoire
        large_data = []
        for i in range(100000):  # 100k éléments
            large_data.append({
                'id': i,
                'name': f'Item {i}',
                'data': 'A' * 100,  # 100 caractères par élément
                'metadata': {
                    'created': f'2024-01-{(i % 28) + 1:02d}',
                    'updated': f'2024-01-{(i % 28) + 1:02d}',
                    'tags': [f'tag{j}' for j in range(5)]
                }
            })
        
        # Obtenir l'utilisation mémoire après l'opération
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Libérer la mémoire
        del large_data
        
        # Obtenir l'utilisation mémoire après libération
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifications
        self.assertGreater(peak_memory, initial_memory)  # La mémoire a augmenté
        self.assertLess(final_memory, peak_memory)       # La mémoire a diminué après libération
        
        # Vérifier que l'utilisation mémoire finale est raisonnable
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 100)  # Moins de 100 MB d'augmentation
    
    def test_cache_memory_usage(self):
        """Test de l'utilisation mémoire du cache"""
        from jobs.utils import CacheManager
        
        # Obtenir l'utilisation mémoire initiale
        import psutil
        import os
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Remplir le cache avec beaucoup de données
        for i in range(10000):
            CacheManager.set_cached_data(
                f'large_key_{i}', 
                'A' * 1000,  # 1KB par clé
                timeout=300
            )
        
        # Obtenir l'utilisation mémoire après remplissage du cache
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vider le cache
        cache.clear()
        
        # Obtenir l'utilisation mémoire après vidage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifications
        self.assertGreater(peak_memory, initial_memory)  # La mémoire a augmenté
        self.assertLess(final_memory, peak_memory)       # La mémoire a diminué après vidage
        
        # Vérifier que l'utilisation mémoire finale est raisonnable
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 50)  # Moins de 50 MB d'augmentation

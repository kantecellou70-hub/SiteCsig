"""
Tests de stress pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time
import threading
import concurrent.futures
import psutil
import os

from .test_settings import JobsTestCaseWithCelery

class StressTest(JobsTestCaseWithCelery):
    """Tests de stress pour l'application jobs"""
    
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

class ConcurrentTaskExecutionTest(StressTest):
    """Tests de stress pour l'exécution concurrente de tâches"""
    
    def test_concurrent_newsletter_email_sending(self):
        """Test de stress pour l'envoi concurrent d'emails de newsletter"""
        from jobs.tasks import send_newsletter_email
        
        # Nombre de tâches concurrentes
        num_tasks = 100
        
        # Mock des dépendances
        with patch('jobs.tasks.EmailMessage') as mock_email:
            mock_email_instance = MagicMock()
            mock_email.return_value = mock_email_instance
            
            with patch('jobs.tasks.settings') as mock_settings:
                mock_settings.SITE_URL = 'http://example.com'
                mock_settings.DEFAULT_FROM_EMAIL = 'noreply@example.com'
                
                # Fonction pour exécuter une tâche
                def execute_task(task_id):
                    return send_newsletter_email(1, f'test{task_id}@example.com', f'User {task_id}')
                
                # Exécuter les tâches de manière concurrente
                start_time = time.time()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(execute_task, i) for i in range(num_tasks)]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Vérifications
                self.assertEqual(len(results), num_tasks)
                self.assertTrue(all(result for result in results))
                
                # Vérifier que l'exécution concurrente est plus rapide que séquentielle
                self.assertLess(execution_time, num_tasks * 0.01)  # Moins de 10ms par tâche
    
    def test_concurrent_cache_operations(self):
        """Test de stress pour les opérations concurrentes sur le cache"""
        from jobs.utils import CacheManager
        
        # Nombre d'opérations concurrentes
        num_operations = 1000
        
        # Fonction pour effectuer des opérations de cache
        def cache_operation(operation_id):
            # Mise en cache
            CacheManager.set_cached_data(f'stress_key_{operation_id}', f'value_{operation_id}', timeout=300)
            
            # Récupération
            value = CacheManager.get_cached_data(f'stress_key_{operation_id}')
            
            # Suppression
            CacheManager.delete_cached_data(f'stress_key_{operation_id}')
            
            return value == f'value_{operation_id}'
        
        # Exécuter les opérations de manière concurrente
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(cache_operation, i) for i in range(num_operations)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifications
        self.assertEqual(len(results), num_operations)
        self.assertTrue(all(result for result in results))
        
        # Vérifier que l'exécution concurrente est rapide
        self.assertLess(execution_time, 10.0)  # Moins de 10 secondes pour 1000 opérations

class HighVolumeDataTest(StressTest):
    """Tests de stress pour le traitement de gros volumes de données"""
    
    def test_large_newsletter_campaign_processing(self):
        """Test de stress pour le traitement de grandes campagnes de newsletter"""
        from jobs.tasks import send_bulk_newsletter
        
        # Simuler une campagne avec beaucoup d'abonnés
        subscriber_counts = [1000, 5000, 10000]
        
        for count in subscriber_counts:
            # Mock des dépendances
            with patch('jobs.tasks.NewsletterCampaign.objects.get') as mock_get_campaign:
                mock_get_campaign.return_value = type('MockCampaign', (), {
                    'id': 1,
                    'title': f"Large Campaign {count}",
                    'can_be_sent': MagicMock(return_value=True),
                    'status': 'draft',
                    'started_at': None,
                    'completed_at': None,
                    'save': MagicMock()
                })()
                
                with patch('jobs.tasks.Newsletter.objects.filter') as mock_filter:
                    # Créer beaucoup d'abonnés simulés
                    mock_subscribers = [
                        type('MockSubscriber', (), {
                            'id': i,
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
                        expected_max_time = 1.0 + (count * 0.0001)  # 1s de base + 0.0001s par abonné
                        self.assertLess(execution_time, expected_max_time)
    
    def test_large_data_export_performance(self):
        """Test de stress pour l'export de gros volumes de données"""
        from jobs.utils import DataExporter
        
        # Créer de gros volumes de données
        data_sizes = [10000, 50000, 100000]
        
        for size in data_sizes:
            # Créer des données de test
            test_data = [
                {
                    'id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'age': 20 + (i % 50),
                    'city': f'City {i % 100}',
                    'department': f'Dept {i % 20}',
                    'salary': 30000 + (i * 10),
                    'start_date': f'2020-{(i % 12) + 1:02d}-01',
                    'is_active': bool(i % 2),
                    'last_login': f'2024-01-{(i % 28) + 1:02d}',
                    'profile': {
                        'bio': f'Bio for user {i}',
                        'interests': [f'interest{j}' for j in range(5)],
                        'skills': [f'skill{j}' for j in range(3)]
                    }
                }
                for i in range(size)
            ]
            
            # Test d'export CSV
            start_time = time.time()
            csv_content = DataExporter.export_to_csv(test_data)
            csv_time = time.time() - start_time
            
            # Test d'export JSON
            start_time = time.time()
            json_content = DataExporter.export_to_json(test_data)
            json_time = time.time() - start_time
            
            # Test d'export XML
            start_time = time.time()
            xml_content = DataExporter.export_to_xml(test_data, 'users', 'user')
            xml_time = time.time() - start_time
            
            # Vérifications
            self.assertIsNotNone(csv_content)
            self.assertIsNotNone(json_content)
            self.assertIsNotNone(xml_content)
            
            # Vérifier que les exports sont rapides même pour de gros volumes
            expected_csv_time = 0.5 + (size * 0.00001)  # 0.5s de base + 0.00001s par ligne
            expected_json_time = 0.3 + (size * 0.000005)  # 0.3s de base + 0.000005s par ligne
            expected_xml_time = 1.0 + (size * 0.00002)  # 1s de base + 0.00002s par ligne
            
            self.assertLess(csv_time, expected_csv_time)
            self.assertLess(json_time, expected_json_time)
            self.assertLess(xml_time, expected_xml_time)

class MemoryStressTest(StressTest):
    """Tests de stress pour l'utilisation mémoire"""
    
    def test_memory_usage_with_large_datasets(self):
        """Test de stress pour l'utilisation mémoire avec de gros ensembles de données"""
        import psutil
        import os
        
        # Obtenir l'utilisation mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Créer de gros ensembles de données
        large_datasets = []
        
        for dataset_id in range(10):
            dataset = {
                'id': dataset_id,
                'name': f'Dataset {dataset_id}',
                'data': [f'Data point {i}' for i in range(10000)],  # 10k points par dataset
                'metadata': {
                    'created': f'2024-01-{dataset_id + 1:02d}',
                    'size': 10000,
                    'tags': [f'tag{j}' for j in range(20)]
                },
                'nested_data': {
                    'level1': {
                        'level2': {
                            'level3': [f'nested_{i}' for i in range(1000)]
                        }
                    }
                }
            }
            large_datasets.append(dataset)
        
        # Obtenir l'utilisation mémoire après création des datasets
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Effectuer des opérations sur les datasets
        processed_data = []
        for dataset in large_datasets:
            # Traitement simulé
            processed = {
                'id': dataset['id'],
                'name': dataset['name'],
                'data_count': len(dataset['data']),
                'total_tags': len(dataset['metadata']['tags']),
                'nested_count': len(dataset['nested_data']['level1']['level2']['level3'])
            }
            processed_data.append(processed)
        
        # Obtenir l'utilisation mémoire après traitement
        processing_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Libérer la mémoire
        del large_datasets
        del processed_data
        
        # Obtenir l'utilisation mémoire après libération
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifications
        self.assertGreater(peak_memory, initial_memory)  # La mémoire a augmenté
        self.assertLess(final_memory, peak_memory)       # La mémoire a diminué après libération
        
        # Vérifier que l'utilisation mémoire finale est raisonnable
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 200)  # Moins de 200 MB d'augmentation

class SystemResourceStressTest(StressTest):
    """Tests de stress pour les ressources système"""
    
    def test_cpu_intensive_operations(self):
        """Test de stress pour les opérations intensives en CPU"""
        from jobs.utils import SystemMonitor
        
        # Mesurer l'utilisation CPU initiale
        initial_cpu = SystemMonitor.get_cpu_info()['usage_percent']
        
        # Effectuer des opérations intensives en CPU
        def cpu_intensive_task():
            # Calcul intensif
            result = 0
            for i in range(1000000):
                result += i * i
            return result
        
        # Exécuter plusieurs tâches intensives en parallèle
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(4)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        execution_time = time.time() - start_time
        
        # Mesurer l'utilisation CPU après les opérations
        final_cpu = SystemMonitor.get_cpu_info()['usage_percent']
        
        # Vérifications
        self.assertEqual(len(results), 4)
        self.assertTrue(all(result > 0 for result in results))
        
        # Vérifier que les opérations ont été exécutées
        self.assertGreater(execution_time, 0.1)  # Au moins 100ms
        
        # L'utilisation CPU peut avoir augmenté temporairement
        # mais le système devrait rester stable
    
    def test_memory_intensive_operations(self):
        """Test de stress pour les opérations intensives en mémoire"""
        from jobs.utils import SystemMonitor
        
        # Mesurer l'utilisation mémoire initiale
        initial_memory = SystemMonitor.get_memory_info()['usage_percent']
        
        # Effectuer des opérations intensives en mémoire
        def memory_intensive_task():
            # Créer de gros objets en mémoire
            large_objects = []
            for i in range(100):
                large_object = {
                    'id': i,
                    'data': 'A' * 10000,  # 10KB par objet
                    'array': list(range(1000)),
                    'nested': {
                        'level1': [f'data_{j}' for j in range(100)],
                        'level2': {'key': 'value' * 100}
                    }
                }
                large_objects.append(large_object)
            
            # Effectuer des opérations sur les objets
            total_size = sum(len(obj['data']) for obj in large_objects)
            total_elements = sum(len(obj['array']) for obj in large_objects)
            
            return total_size, total_elements
        
        # Exécuter plusieurs tâches intensives en mémoire
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(memory_intensive_task) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        execution_time = time.time() - start_time
        
        # Mesurer l'utilisation mémoire après les opérations
        final_memory = SystemMonitor.get_memory_info()['usage_percent']
        
        # Vérifications
        self.assertEqual(len(results), 3)
        for total_size, total_elements in results:
            self.assertEqual(total_size, 1000000)  # 100 * 10KB
            self.assertEqual(total_elements, 100000)  # 100 * 1000
        
        # Vérifier que les opérations ont été exécutées
        self.assertGreater(execution_time, 0.1)  # Au moins 100ms
        
        # L'utilisation mémoire peut avoir augmenté temporairement
        # mais le système devrait rester stable

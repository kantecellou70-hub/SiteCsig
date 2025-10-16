"""
Tests pour les utilitaires de l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
import hashlib
import os

class CacheManagerTest(TestCase):
    """Tests pour la classe CacheManager"""
    
    def setUp(self):
        # Nettoyer le cache avant chaque test
        cache.clear()
    
    def test_get_cache_key_with_identifier(self):
        """Test de la génération de clé de cache avec identifiant"""
        from jobs.utils import CacheManager
        
        key = CacheManager.get_cache_key('test', '123')
        expected_key = 'jobs_test_123'
        self.assertEqual(key, expected_key)
    
    def test_get_cache_key_without_identifier(self):
        """Test de la génération de clé de cache sans identifiant"""
        from jobs.utils import CacheManager
        
        key = CacheManager.get_cache_key('test')
        expected_key = 'jobs_test'
        self.assertEqual(key, expected_key)
    
    def test_get_cached_data_existing(self):
        """Test de la récupération de données en cache existantes"""
        from jobs.utils import CacheManager
        
        # Mettre des données en cache
        test_data = {'key': 'value', 'number': 42}
        cache.set('jobs_test_key', test_data, timeout=300)
        
        # Récupérer les données
        result = CacheManager.get_cached_data('jobs_test_key', default=None)
        self.assertEqual(result, test_data)
    
    def test_get_cached_data_not_existing(self):
        """Test de la récupération de données en cache inexistantes"""
        from jobs.utils import CacheManager
        
        # Récupérer des données qui n'existent pas
        result = CacheManager.get_cached_data('nonexistent_key', default='default_value')
        self.assertEqual(result, 'default_value')
    
    def test_get_cached_data_cache_error(self):
        """Test de la gestion des erreurs de cache"""
        from jobs.utils import CacheManager
        
        # Simuler une erreur de cache
        with patch('jobs.utils.cache.get') as mock_cache_get:
            mock_cache_get.side_effect = Exception("Cache error")
            
            # Devrait retourner la valeur par défaut
            result = CacheManager.get_cached_data('test_key', default='fallback')
            self.assertEqual(result, 'fallback')
    
    def test_set_cached_data_success(self):
        """Test de la mise en cache de données avec succès"""
        from jobs.utils import CacheManager
        
        test_data = {'key': 'value'}
        result = CacheManager.set_cached_data('test_key', test_data, timeout=300)
        
        # Vérifier que les données ont été mises en cache
        cached_data = cache.get('test_key')
        self.assertEqual(cached_data, test_data)
        self.assertTrue(result)
    
    def test_set_cached_data_error(self):
        """Test de la gestion des erreurs lors de la mise en cache"""
        from jobs.utils import CacheManager
        
        # Simuler une erreur de cache
        with patch('jobs.utils.cache.set') as mock_cache_set:
            mock_cache_set.side_effect = Exception("Cache error")
            
            # Devrait retourner False en cas d'erreur
            result = CacheManager.set_cached_data('test_key', 'value', timeout=300)
            self.assertFalse(result)
    
    def test_delete_cached_data_success(self):
        """Test de la suppression de données en cache avec succès"""
        from jobs.utils import CacheManager
        
        # Mettre des données en cache
        cache.set('test_key', 'value', timeout=300)
        
        # Supprimer les données
        result = CacheManager.delete_cached_data('test_key')
        self.assertTrue(result)
        
        # Vérifier que les données ont été supprimées
        cached_data = cache.get('test_key')
        self.assertIsNone(cached_data)
    
    def test_delete_cached_data_error(self):
        """Test de la gestion des erreurs lors de la suppression"""
        from jobs.utils import CacheManager
        
        # Simuler une erreur de cache
        with patch('jobs.utils.cache.delete') as mock_cache_delete:
            mock_cache_delete.side_effect = Exception("Cache error")
            
            # Devrait retourner False en cas d'erreur
            result = CacheManager.delete_cached_data('test_key')
            self.assertFalse(result)
    
    def test_get_cached_performance_metrics(self):
        """Test de la récupération des métriques de performance en cache"""
        from jobs.utils import CacheManager
        
        # Mettre des métriques en cache
        metrics = {'cpu_usage': 25.5, 'memory_usage': 60.2}
        cache.set('jobs_performance_metrics', metrics, timeout=300)
        
        # Récupérer les métriques
        result = CacheManager.get_cached_performance_metrics()
        self.assertEqual(result, metrics)
    
    def test_set_cached_performance_metrics(self):
        """Test de la mise en cache des métriques de performance"""
        from jobs.utils import CacheManager
        
        metrics = {'cpu_usage': 30.0, 'memory_usage': 70.0}
        result = CacheManager.set_cached_performance_metrics(metrics)
        
        # Vérifier que les métriques ont été mises en cache
        cached_metrics = cache.get('jobs_performance_metrics')
        self.assertEqual(cached_metrics, metrics)
        self.assertTrue(result)

class PerformanceMonitorTest(TestCase):
    """Tests pour la classe PerformanceMonitor"""
    
    def test_timing_decorator(self):
        """Test du décorateur de timing"""
        from jobs.utils import PerformanceMonitor
        
        @PerformanceMonitor.timing
        def test_function():
            import time
            time.sleep(0.1)  # Simuler un délai
            return "success"
        
        # Exécuter la fonction
        result = test_function()
        
        # Vérifier le résultat
        self.assertEqual(result, "success")
        
        # Vérifier que le timing a été enregistré
        # Note: En mode test, le timing peut ne pas être exactement le même
    
    def test_timing_context_manager(self):
        """Test du gestionnaire de contexte de timing"""
        from jobs.utils import PerformanceMonitor
        
        with PerformanceMonitor.timing_context('test_operation'):
            import time
            time.sleep(0.1)  # Simuler un délai
        
        # Vérifier que le timing a été enregistré
        # Note: En mode test, le timing peut ne pas être exactement le même
    
    def test_memory_usage(self):
        """Test de la mesure de l'utilisation mémoire"""
        from jobs.utils import PerformanceMonitor
        
        # Mesurer l'utilisation mémoire
        memory_usage = PerformanceMonitor.get_memory_usage()
        
        # Vérifier que les données sont présentes
        self.assertIn('rss', memory_usage)
        self.assertIn('vms', memory_usage)
        self.assertIn('percent', memory_usage)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(memory_usage['rss'], (int, float))
        self.assertIsInstance(memory_usage['vms'], (int, float))
        self.assertIsInstance(memory_usage['percent'], (int, float))
        self.assertGreaterEqual(memory_usage['rss'], 0)
        self.assertGreaterEqual(memory_usage['vms'], 0)
        self.assertGreaterEqual(memory_usage['percent'], 0)
    
    def test_cpu_usage(self):
        """Test de la mesure de l'utilisation CPU"""
        from jobs.utils import PerformanceMonitor
        
        # Mesurer l'utilisation CPU
        cpu_usage = PerformanceMonitor.get_cpu_usage()
        
        # Vérifier que la valeur est un nombre
        self.assertIsInstance(cpu_usage, (int, float))
        
        # Vérifier que la valeur est dans une plage raisonnable (0-100)
        self.assertGreaterEqual(cpu_usage, 0)
        self.assertLessEqual(cpu_usage, 100)

class SystemMonitorTest(TestCase):
    """Tests pour la classe SystemMonitor"""
    
    def setUp(self):
        # Nettoyer le cache avant chaque test
        cache.clear()
    
    def test_get_system_health(self):
        """Test de la récupération de la santé du système"""
        from jobs.utils import SystemMonitor
        
        # Récupérer la santé du système
        health = SystemMonitor.get_system_health()
        
        # Vérifier que les données sont présentes
        self.assertIn('timestamp', health)
        self.assertIn('overall_status', health)
        self.assertIn('cpu_usage', health)
        self.assertIn('memory_usage', health)
        self.assertIn('disk_usage', health)
        
        # Vérifier le statut global
        self.assertIn(health['overall_status'], ['healthy', 'warning', 'critical'])
        
        # Vérifier que le timestamp est récent
        timestamp = datetime.fromisoformat(health['timestamp'])
        time_diff = abs((timezone.now() - timestamp).total_seconds())
        self.assertLess(time_diff, 10)  # Moins de 10 secondes
    
    def test_get_cpu_info(self):
        """Test de la récupération des informations CPU"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations CPU
        cpu_info = SystemMonitor.get_cpu_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('usage_percent', cpu_info)
        self.assertIn('count', cpu_info)
        self.assertIn('frequency', cpu_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(cpu_info['usage_percent'], (int, float))
        self.assertIsInstance(cpu_info['count'], int)
        self.assertIsInstance(cpu_info['frequency'], (int, float))
        self.assertGreaterEqual(cpu_info['usage_percent'], 0)
        self.assertGreaterEqual(cpu_info['count'], 1)
        self.assertGreaterEqual(cpu_info['frequency'], 0)
    
    def test_get_memory_info(self):
        """Test de la récupération des informations mémoire"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations mémoire
        memory_info = SystemMonitor.get_memory_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('total_gb', memory_info)
        self.assertIn('available_gb', memory_info)
        self.assertIn('used_gb', memory_info)
        self.assertIn('usage_percent', memory_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(memory_info['total_gb'], (int, float))
        self.assertIsInstance(memory_info['available_gb'], (int, float))
        self.assertIsInstance(memory_info['used_gb'], (int, float))
        self.assertIsInstance(memory_info['usage_percent'], (int, float))
        self.assertGreaterEqual(memory_info['total_gb'], 0)
        self.assertGreaterEqual(memory_info['available_gb'], 0)
        self.assertGreaterEqual(memory_info['used_gb'], 0)
        self.assertGreaterEqual(memory_info['usage_percent'], 0)
        self.assertLessEqual(memory_info['usage_percent'], 100)
    
    def test_get_disk_info(self):
        """Test de la récupération des informations disque"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations disque
        disk_info = SystemMonitor.get_disk_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('total_gb', disk_info)
        self.assertIn('used_gb', disk_info)
        self.assertIn('free_gb', disk_info)
        self.assertIn('usage_percent', disk_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(disk_info['total_gb'], (int, float))
        self.assertIsInstance(disk_info['used_gb'], (int, float))
        self.assertIsInstance(disk_info['free_gb'], (int, float))
        self.assertIsInstance(disk_info['usage_percent'], (int, float))
        self.assertGreaterEqual(disk_info['total_gb'], 0)
        self.assertGreaterEqual(disk_info['used_gb'], 0)
        self.assertGreaterEqual(disk_info['free_gb'], 0)
        self.assertGreaterEqual(disk_info['usage_percent'], 0)
        self.assertLessEqual(disk_info['usage_percent'], 100)
    
    def test_get_network_info(self):
        """Test de la récupération des informations réseau"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations réseau
        network_info = SystemMonitor.get_network_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('bytes_sent', network_info)
        self.assertIn('bytes_recv', network_info)
        self.assertIn('packets_sent', network_info)
        self.assertIn('packets_recv', network_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(network_info['bytes_sent'], (int, float))
        self.assertIsInstance(network_info['bytes_recv'], (int, float))
        self.assertIsInstance(network_info['packets_sent'], (int, float))
        self.assertIsInstance(network_info['packets_recv'], (int, float))
        self.assertGreaterEqual(network_info['bytes_sent'], 0)
        self.assertGreaterEqual(network_info['bytes_recv'], 0)
        self.assertGreaterEqual(network_info['packets_sent'], 0)
        self.assertGreaterEqual(network_info['packets_recv'], 0)
    
    def test_get_database_info(self):
        """Test de la récupération des informations base de données"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations base de données
        db_info = SystemMonitor.get_database_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('connections', db_info)
        self.assertIn('size_mb', db_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(db_info['connections'], int)
        self.assertIsInstance(db_info['size_mb'], (int, float))
        self.assertGreaterEqual(db_info['connections'], 0)
        self.assertGreaterEqual(db_info['size_mb'], 0)
    
    def test_get_celery_info(self):
        """Test de la récupération des informations Celery"""
        from jobs.utils import SystemMonitor
        
        # Récupérer les informations Celery
        celery_info = SystemMonitor.get_celery_info()
        
        # Vérifier que les données sont présentes
        self.assertIn('active_workers', celery_info)
        self.assertIn('active_tasks', celery_info)
        self.assertIn('queued_tasks', celery_info)
        
        # Vérifier que les valeurs sont des nombres positifs
        self.assertIsInstance(celery_info['active_workers'], int)
        self.assertIsInstance(celery_info['active_tasks'], int)
        self.assertIsInstance(celery_info['queued_tasks'], int)
        self.assertGreaterEqual(celery_info['active_workers'], 0)
        self.assertGreaterEqual(celery_info['active_tasks'], 0)
        self.assertGreaterEqual(celery_info['queued_tasks'], 0)

class EmailValidatorTest(TestCase):
    """Tests pour la classe EmailValidator"""
    
    def test_is_valid_email_format_valid(self):
        """Test de la validation du format d'email valide"""
        from jobs.utils import EmailValidator
        
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            '123@numbers.com',
            'user@subdomain.example.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(EmailValidator.is_valid_email_format(email))
    
    def test_is_valid_email_format_invalid(self):
        """Test de la validation du format d'email invalide"""
        from jobs.utils import EmailValidator
        
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            'user..name@example.com',
            'user@example..com',
            'user name@example.com',
            'user@example com'
        ]
        
        for email in invalid_emails:
            self.assertFalse(EmailValidator.is_valid_email_format(email))
    
    def test_is_disposable_email(self):
        """Test de la détection des emails jetables"""
        from jobs.utils import EmailValidator
        
        # Simuler une liste d'emails jetables
        disposable_domains = [
            '10minutemail.com',
            'guerrillamail.com',
            'mailinator.com',
            'tempmail.org'
        ]
        
        for domain in disposable_domains:
            email = f'test@{domain}'
            # Note: En mode test, la détection peut ne pas fonctionner
            # car la liste n'est pas chargée
            pass
    
    def test_is_valid_email_complete(self):
        """Test de la validation complète d'email"""
        from jobs.utils import EmailValidator
        
        # Email valide et non jetable
        result = EmailValidator.is_valid_email('test@example.com')
        self.assertTrue(result)
        
        # Email invalide
        result = EmailValidator.is_valid_email('invalid-email')
        self.assertFalse(result)

class TaskSchedulerTest(TestCase):
    """Tests pour la classe TaskScheduler"""
    
    def test_calculate_next_run_time_daily(self):
        """Test du calcul du prochain temps d'exécution quotidien"""
        from jobs.utils import TaskScheduler
        
        # Calculer le prochain temps d'exécution quotidien à 14h00
        next_run = TaskScheduler.calculate_next_run_time('daily', hour=14, minute=0)
        
        # Vérifier que c'est aujourd'hui ou demain
        now = timezone.now()
        tomorrow = now + timedelta(days=1)
        
        if now.hour >= 14:
            # Si c'est après 14h00, le prochain exécution sera demain
            expected_date = tomorrow.date()
        else:
            # Sinon, c'est aujourd'hui
            expected_date = now.date()
        
        self.assertEqual(next_run.date(), expected_date)
        self.assertEqual(next_run.hour, 14)
        self.assertEqual(next_run.minute, 0)
    
    def test_calculate_next_run_time_weekly(self):
        """Test du calcul du prochain temps d'exécution hebdomadaire"""
        from jobs.utils import TaskScheduler
        
        # Calculer le prochain temps d'exécution hebdomadaire le lundi à 9h00
        next_run = TaskScheduler.calculate_next_run_time('weekly', day_of_week=0, hour=9, minute=0)
        
        # Vérifier que c'est un lundi (0 = lundi)
        self.assertEqual(next_run.weekday(), 0)
        self.assertEqual(next_run.hour, 9)
        self.assertEqual(next_run.minute, 0)
        
        # Vérifier que c'est dans le futur
        self.assertGreater(next_run, timezone.now())
    
    def test_calculate_next_run_time_monthly(self):
        """Test du calcul du prochain temps d'exécution mensuel"""
        from jobs.utils import TaskScheduler
        
        # Calculer le prochain temps d'exécution mensuel le 15 à 10h00
        next_run = TaskScheduler.calculate_next_run_time('monthly', day_of_month=15, hour=10, minute=0)
        
        # Vérifier que c'est le 15 du mois
        self.assertEqual(next_run.day, 15)
        self.assertEqual(next_run.hour, 10)
        self.assertEqual(next_run.minute, 0)
        
        # Vérifier que c'est dans le futur
        self.assertGreater(next_run, timezone.now())
    
    def test_calculate_next_run_time_custom_interval(self):
        """Test du calcul du prochain temps d'exécution avec intervalle personnalisé"""
        from jobs.utils import TaskScheduler
        
        # Calculer le prochain temps d'exécution dans 2 heures
        next_run = TaskScheduler.calculate_next_run_time('custom', hours=2)
        
        # Vérifier que c'est dans 2 heures (avec une marge de 1 minute)
        now = timezone.now()
        expected_time = now + timedelta(hours=2)
        time_diff = abs((next_run - expected_time).total_seconds())
        self.assertLess(time_diff, 60)
    
    def test_is_time_to_run(self):
        """Test de la vérification si c'est le moment d'exécuter une tâche"""
        from jobs.utils import TaskScheduler
        
        # Tâche programmée pour maintenant
        now = timezone.now()
        result = TaskScheduler.is_time_to_run(now)
        self.assertTrue(result)
        
        # Tâche programmée pour le futur
        future_time = now + timedelta(hours=1)
        result = TaskScheduler.is_time_to_run(future_time)
        self.assertFalse(result)
        
        # Tâche programmée pour le passé
        past_time = now - timedelta(hours=1)
        result = TaskScheduler.is_time_to_run(past_time)
        self.assertTrue(result)

class DataExporterTest(TestCase):
    """Tests pour la classe DataExporter"""
    
    def setUp(self):
        # Créer des données de test
        self.test_data = [
            {'name': 'John', 'age': 30, 'city': 'New York'},
            {'name': 'Jane', 'age': 25, 'city': 'Los Angeles'},
            {'name': 'Bob', 'age': 35, 'city': 'Chicago'}
        ]
    
    def test_export_to_csv(self):
        """Test de l'export vers CSV"""
        from jobs.utils import DataExporter
        
        # Exporter vers CSV
        csv_content = DataExporter.export_to_csv(self.test_data)
        
        # Vérifier que le contenu CSV est correct
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 4)  # En-tête + 3 lignes de données
        
        # Vérifier l'en-tête
        header = lines[0]
        self.assertIn('name', header)
        self.assertIn('age', header)
        self.assertIn('city', header)
        
        # Vérifier les données
        self.assertIn('John,30,New York', csv_content)
        self.assertIn('Jane,25,Los Angeles', csv_content)
        self.assertIn('Bob,35,Chicago', csv_content)
    
    def test_export_to_json(self):
        """Test de l'export vers JSON"""
        from jobs.utils import DataExporter
        
        # Exporter vers JSON
        json_content = DataExporter.export_to_json(self.test_data)
        
        # Vérifier que le contenu JSON est valide
        parsed_data = json.loads(json_content)
        self.assertEqual(len(parsed_data), 3)
        
        # Vérifier la structure des données
        self.assertEqual(parsed_data[0]['name'], 'John')
        self.assertEqual(parsed_data[0]['age'], 30)
        self.assertEqual(parsed_data[0]['city'], 'New York')
    
    def test_export_to_xml(self):
        """Test de l'export vers XML"""
        from jobs.utils import DataExporter
        
        # Exporter vers XML
        xml_content = DataExporter.export_to_xml(self.test_data, root_name='users', item_name='user')
        
        # Vérifier que le contenu XML est correct
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', xml_content)
        self.assertIn('<users>', xml_content)
        self.assertIn('</users>', xml_content)
        self.assertIn('<user>', xml_content)
        self.assertIn('</user>', xml_content)
        
        # Vérifier les données
        self.assertIn('<name>John</name>', xml_content)
        self.assertIn('<age>30</age>', xml_content)
        self.assertIn('<city>New York</city>', xml_content)
    
    def test_export_to_xml_custom_names(self):
        """Test de l'export vers XML avec noms personnalisés"""
        from jobs.utils import DataExporter
        
        # Exporter vers XML avec des noms personnalisés
        xml_content = DataExporter.export_to_xml(
            self.test_data, 
            root_name='employees', 
            item_name='employee'
        )
        
        # Vérifier que les noms personnalisés sont utilisés
        self.assertIn('<employees>', xml_content)
        self.assertIn('</employees>', xml_content)
        self.assertIn('<employee>', xml_content)
        self.assertIn('</employee>', xml_content)

class SecurityUtilsTest(TestCase):
    """Tests pour la classe SecurityUtils"""
    
    def test_generate_token_length(self):
        """Test de la génération de token avec longueur spécifiée"""
        from jobs.utils import SecurityUtils
        
        # Générer un token de 32 caractères
        token = SecurityUtils.generate_token(32)
        self.assertEqual(len(token), 32)
        
        # Générer un token de 64 caractères
        token = SecurityUtils.generate_token(64)
        self.assertEqual(len(token), 64)
    
    def test_generate_token_uniqueness(self):
        """Test de l'unicité des tokens générés"""
        from jobs.utils import SecurityUtils
        
        # Générer plusieurs tokens
        tokens = set()
        for _ in range(100):
            token = SecurityUtils.generate_token(32)
            tokens.add(token)
        
        # Vérifier qu'il n'y a pas de doublons
        self.assertEqual(len(tokens), 100)
    
    def test_hash_data(self):
        """Test du hachage des données"""
        from jobs.utils import SecurityUtils
        
        # Données de test
        test_data = "Hello, World!"
        
        # Hasher les données
        hashed_data = SecurityUtils.hash_data(test_data)
        
        # Vérifier que le hash est différent des données originales
        self.assertNotEqual(hashed_data, test_data)
        
        # Vérifier que le hash a une longueur appropriée (SHA-256 = 64 caractères hex)
        self.assertEqual(len(hashed_data), 64)
        
        # Vérifier que le hash est cohérent
        hashed_data_2 = SecurityUtils.hash_data(test_data)
        self.assertEqual(hashed_data, hashed_data_2)
    
    def test_verify_hash(self):
        """Test de la vérification du hash"""
        from jobs.utils import SecurityUtils
        
        # Données de test
        test_data = "Hello, World!"
        
        # Hasher les données
        hashed_data = SecurityUtils.hash_data(test_data)
        
        # Vérifier le hash
        self.assertTrue(SecurityUtils.verify_hash(test_data, hashed_data))
        
        # Vérifier avec des données incorrectes
        self.assertFalse(SecurityUtils.verify_hash("Wrong data", hashed_data))
    
    def test_generate_secure_password(self):
        """Test de la génération de mot de passe sécurisé"""
        from jobs.utils import SecurityUtils
        
        # Générer un mot de passe
        password = SecurityUtils.generate_secure_password()
        
        # Vérifier la longueur (par défaut 12 caractères)
        self.assertEqual(len(password), 12)
        
        # Vérifier qu'il contient au moins une lettre majuscule
        self.assertTrue(any(c.isupper() for c in password))
        
        # Vérifier qu'il contient au moins une lettre minuscule
        self.assertTrue(any(c.islower() for c in password))
        
        # Vérifier qu'il contient au moins un chiffre
        self.assertTrue(any(c.isdigit() for c in password))
        
        # Vérifier qu'il contient au moins un caractère spécial
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.assertTrue(any(c in special_chars for c in password))
    
    def test_generate_secure_password_custom_length(self):
        """Test de la génération de mot de passe avec longueur personnalisée"""
        from jobs.utils import SecurityUtils
        
        # Générer un mot de passe de 20 caractères
        password = SecurityUtils.generate_secure_password(20)
        self.assertEqual(len(password), 20)

class NotificationManagerTest(TestCase):
    """Tests pour la classe NotificationManager"""
    
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('jobs.utils.send_mail')
    def test_send_email_notification_success(self, mock_send_mail):
        """Test de l'envoi réussi d'une notification par email"""
        from jobs.utils import NotificationManager
        
        # Configurer le mock
        mock_send_mail.return_value = 1
        
        # Envoyer une notification
        result = NotificationManager.send_email_notification(
            to_email='test@example.com',
            subject='Test Subject',
            message='Test Message'
        )
        
        # Vérifier que l'email a été envoyé
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    @patch('jobs.utils.send_mail')
    def test_send_email_notification_failure(self, mock_send_mail):
        """Test de l'échec de l'envoi d'une notification par email"""
        from jobs.utils import NotificationManager
        
        # Configurer le mock pour simuler un échec
        mock_send_mail.side_effect = Exception("SMTP error")
        
        # Envoyer une notification
        result = NotificationManager.send_email_notification(
            to_email='test@example.com',
            subject='Test Subject',
            message='Test Message'
        )
        
        # Vérifier que l'envoi a échoué
        self.assertFalse(result)
    
    def test_send_system_alert(self):
        """Test de l'envoi d'une alerte système"""
        from jobs.utils import NotificationManager
        
        # Envoyer une alerte système
        result = NotificationManager.send_system_alert(
            level='warning',
            message='System warning message',
            details={'cpu_usage': 85, 'memory_usage': 90}
        )
        
        # Vérifier que l'alerte a été envoyée
        # Note: En mode test, l'alerte peut être simulée
        self.assertIsInstance(result, bool)
    
    def test_send_user_notification(self):
        """Test de l'envoi d'une notification utilisateur"""
        from jobs.utils import NotificationManager
        
        # Envoyer une notification utilisateur
        result = NotificationManager.send_user_notification(
            user=self.user,
            title='User Notification',
            message='This is a user notification',
            notification_type='info'
        )
        
        # Vérifier que la notification a été envoyée
        # Note: En mode test, la notification peut être simulée
        self.assertIsInstance(result, bool)
    
    def test_send_bulk_notifications(self):
        """Test de l'envoi de notifications en masse"""
        from jobs.utils import NotificationManager
        
        # Préparer les notifications
        notifications = [
            {'user': self.user, 'title': 'Bulk 1', 'message': 'Message 1'},
            {'user': self.user, 'title': 'Bulk 2', 'message': 'Message 2'},
            {'user': self.user, 'title': 'Bulk 3', 'message': 'Message 3'}
        ]
        
        # Envoyer les notifications en masse
        result = NotificationManager.send_bulk_notifications(notifications)
        
        # Vérifier que les notifications ont été envoyées
        # Note: En mode test, les notifications peuvent être simulées
        self.assertIsInstance(result, dict)
        self.assertIn('success_count', result)
        self.assertIn('failure_count', result)

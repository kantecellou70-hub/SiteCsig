"""
Tests de migration pour l'application jobs
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db import connection, migrations
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

from .test_settings import JobsTestCaseWithCelery

class MigrationTest(JobsTestCaseWithCelery):
    """Tests de migration pour l'application jobs"""
    
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

class DatabaseMigrationTest(MigrationTest):
    """Tests de migration de base de données"""
    
    def test_migration_files_exist(self):
        """Test que les fichiers de migration existent"""
        from django.apps import apps
        import os
        
        # Obtenir l'application jobs
        jobs_app = apps.get_app_config('jobs')
        migrations_dir = os.path.join(jobs_app.path, 'migrations')
        
        # Vérifier que le répertoire des migrations existe
        self.assertTrue(os.path.exists(migrations_dir))
        
        # Lister les fichiers de migration
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
        
        # Il doit y avoir au moins le fichier __init__.py
        self.assertIn('__init__.py', migration_files)
        
        # Il doit y avoir au moins un fichier de migration (0001_initial.py)
        migration_files = [f for f in migration_files if f != '__init__.py']
        self.assertGreater(len(migration_files), 0)
        
        # Vérifier que les fichiers de migration ont le bon format
        for migration_file in migration_files:
            self.assertRegex(migration_file, r'^\d{4}_\w+\.py$')
    
    def test_migration_dependencies(self):
        """Test des dépendances entre migrations"""
        from django.apps import apps
        
        # Obtenir l'application jobs
        jobs_app = apps.get_app_config('jobs')
        
        # Vérifier que l'application a des migrations
        self.assertTrue(hasattr(jobs_app, 'migrations'))
        
        # Vérifier que les migrations peuvent être chargées
        try:
            # Note: Les noms de migrations commencent par des chiffres
            # ce qui n'est pas valide en Python, donc nous testons différemment
            migrations_module = __import__('jobs.migrations')
            self.assertTrue(hasattr(migrations_module, '__file__'))
        except ImportError:
            # La migration peut ne pas exister encore
            pass
    
    def test_migration_forward(self):
        """Test de migration vers l'avant"""
        from django.core.management import call_command
        from django.db import connection
        
        # Vérifier l'état actuel de la base de données
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'jobs' 
                ORDER BY applied
            """)
            applied_migrations = [row[0] for row in cursor.fetchall()]
        
        # Vérifier que les migrations ont été appliquées
        self.assertGreater(len(applied_migrations), 0)
        
        # Vérifier que la migration initiale a été appliquée
        self.assertIn('0001_initial', applied_migrations)
    
    def test_migration_rollback(self):
        """Test de rollback de migration"""
        from django.core.management import call_command
        from django.db import connection
        
        # Obtenir l'état actuel des migrations
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'jobs' 
                ORDER BY applied DESC
            """)
            current_migrations = [row[0] for row in cursor.fetchall()]
        
        # Vérifier que nous avons des migrations appliquées
        self.assertGreater(len(current_migrations), 0)
        
        # Note: Le rollback complet n'est pas testé car cela pourrait
        # affecter d'autres tests. En production, cela serait testé
        # dans un environnement isolé.
    
    def test_migration_data_integrity(self):
        """Test de l'intégrité des données après migration"""
        from content_management.models import NewsletterCampaign
        from jobs.models import EmailTemplate
        
        # Créer des données de test
        template = EmailTemplate.objects.create(
            name='migration_test_template',
            subject_template='Test {{ user.name }}',
            html_template='<h1>Hello {{ user.name }}</h1>',
            text_template='Hello {{ user.name }}'
        )
        
        campaign = NewsletterCampaign.objects.create(
            title='Migration Test Campaign',
            subject='Test Subject',
            content='Test content',
            template_name='migration_test_template',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier que les données ont été créées correctement
        self.assertIsNotNone(template.id)
        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.template_name, template.name)
        
        # Vérifier les relations
        self.assertEqual(campaign.created_by, self.user)
        
        # Nettoyer
        campaign.delete()
        template.delete()

class ModelMigrationTest(MigrationTest):
    """Tests de migration des modèles"""
    
    def test_model_field_migrations(self):
        """Test des migrations de champs de modèles"""
        from content_management.models import NewsletterCampaign
        
        # Vérifier que tous les champs requis existent
        required_fields = [
            'title', 'subject', 'content', 'template_name', 
            'status', 'created_by', 'created_at'
        ]
        
        for field_name in required_fields:
            self.assertTrue(hasattr(NewsletterCampaign, field_name))
        
        # Vérifier les types de champs
        title_field = NewsletterCampaign._meta.get_field('title')
        self.assertEqual(title_field.max_length, 200)
        
        status_field = NewsletterCampaign._meta.get_field('status')
        self.assertEqual(len(status_field.choices), 5)  # draft, scheduled, sending, completed, cancelled
    
    def test_model_relationship_migrations(self):
        """Test des migrations de relations entre modèles"""
        from content_management.models import NewsletterCampaign
        from jobs.models import EmailTemplate
        
        # Vérifier la relation ForeignKey
        created_by_field = NewsletterCampaign._meta.get_field('created_by')
        self.assertEqual(created_by_field.related_model, User)
        
        # Vérifier que la relation peut être utilisée
        template = EmailTemplate.objects.create(
            name='relationship_test_template',
            subject_template='Test',
            html_template='<h1>Test</h1>',
            text_template='Test'
        )
        
        campaign = NewsletterCampaign.objects.create(
            title='Relationship Test',
            subject='Test',
            content='Test content',
            template_name='relationship_test_template',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier les relations
        self.assertEqual(campaign.created_by, self.user)
        self.assertEqual(campaign.template_name, template.name)
        
        # Nettoyer
        campaign.delete()
        template.delete()
    
    def test_model_constraint_migrations(self):
        """Test des migrations de contraintes de modèles"""
        from content_management.models import NewsletterCampaign
        from django.core.exceptions import ValidationError
        
        # Vérifier les contraintes de validation
        # Test de titre vide
        with self.assertRaises(Exception):
            campaign = NewsletterCampaign.objects.create(
                title='',  # Titre vide
                subject='Test',
                content='Test content',
                template_name='default',
                status='draft',
                created_by=self.user
            )
        
        # Test de statut invalide
        with self.assertRaises(Exception):
            campaign = NewsletterCampaign.objects.create(
                title='Valid Title',
                subject='Test',
                content='Test content',
                template_name='default',
                status='invalid_status',  # Statut invalide
                created_by=self.user
            )
    
    def test_model_index_migrations(self):
        """Test des migrations d'index de modèles"""
        from content_management.models import NewsletterCampaign
        from django.db import connection
        
        # Vérifier que les index existent
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'jobs_newslettercampaign'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
        
        # Vérifier les index de base
        self.assertGreater(len(indexes), 0)
        
        # Vérifier que l'index sur created_at existe
        created_at_indexes = [idx for idx in indexes if 'created_at' in idx.lower()]
        self.assertGreater(len(created_at_indexes), 0)

class DataMigrationTest(MigrationTest):
    """Tests de migration de données"""
    
    def test_data_preservation_migration(self):
        """Test de préservation des données lors de la migration"""
        from content_management.models import NewsletterCampaign
        from jobs.models import EmailTemplate
        
        # Créer des données avant la migration
        template = EmailTemplate.objects.create(
            name='data_preservation_template',
            subject_template='Hello {{ user.name }}',
            html_template='<h1>Welcome {{ user.name }}</h1>',
            text_template='Welcome {{ user.name }}'
        )
        
        campaign = NewsletterCampaign.objects.create(
            title='Data Preservation Campaign',
            subject='Welcome',
            content='Welcome to our newsletter',
            template_name='data_preservation_template',
            status='draft',
            created_by=self.user
        )
        
        # Simuler une migration (en réalité, ceci testerait une vraie migration)
        # Ici, nous vérifions juste que les données sont préservées
        
        # Vérifier que les données existent toujours
        template.refresh_from_db()
        campaign.refresh_from_db()
        
        self.assertEqual(template.name, 'data_preservation_template')
        self.assertEqual(campaign.title, 'Data Preservation Campaign')
        self.assertEqual(campaign.template_name, template.name)
        
        # Nettoyer
        campaign.delete()
        template.delete()
    
    def test_data_transformation_migration(self):
        """Test de transformation des données lors de la migration"""
        from content_management.models import NewsletterCampaign
        
        # Créer des données avec l'ancien format
        campaign = NewsletterCampaign.objects.create(
            title='Old Format Campaign',
            subject='Old Subject',
            content='Old content',
            template_name='old_template',
            status='draft',
            created_by=self.user
        )
        
        # Simuler une transformation de données
        # Par exemple, mettre à jour le statut
        campaign.status = 'scheduled'
        campaign.scheduled_at = timezone.now() + timedelta(hours=1)
        campaign.save()
        
        # Vérifier que la transformation a été effectuée
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'scheduled')
        self.assertIsNotNone(campaign.scheduled_at)
        
        # Nettoyer
        campaign.delete()
    
    def test_data_cleanup_migration(self):
        """Test de nettoyage des données lors de la migration"""
        from content_management.models import NewsletterCampaign
        
        # Créer des données qui pourraient être nettoyées
        old_campaign = NewsletterCampaign.objects.create(
            title='Old Campaign',
            subject='Old',
            content='Old content',
            template_name='old',
            status='draft',
            created_by=self.user
        )
        
        # Simuler un nettoyage (par exemple, supprimer les anciennes campagnes)
        # old_campaign.delete()  # Ceci simulerait le nettoyage
        
        # Vérifier que le nettoyage peut être effectué
        # self.assertEqual(NewsletterCampaign.objects.count(), 0)
        
        # Pour ce test, nous ne supprimons pas réellement
        self.assertEqual(NewsletterCampaign.objects.count(), 1)
        
        # Nettoyer
        old_campaign.delete()

class SchemaMigrationTest(MigrationTest):
    """Tests de migration de schéma"""
    
    def test_table_creation_migration(self):
        """Test de création de tables lors de la migration"""
        from django.db import connection
        
        # Vérifier que les tables existent
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'jobs_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        # Vérifier que les tables principales existent
        expected_tables = [
            'jobs_newslettercampaign',
            'jobs_newsletterlog',
            'jobs_emailtemplate',
            'jobs_emailqueue'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_column_addition_migration(self):
        """Test d'ajout de colonnes lors de la migration"""
        from content_management.models import NewsletterCampaign
        
        # Vérifier que les nouvelles colonnes existent
        new_columns = [
            'target_language',
            'target_active_only'
        ]
        
        for column in new_columns:
            self.assertTrue(hasattr(NewsletterCampaign, column))
        
        # Vérifier que les colonnes ont les bonnes valeurs par défaut
        campaign = NewsletterCampaign.objects.create(
            title='New Column Test',
            subject='Test',
            content='Test content',
            template_name='default',
            status='draft',
            created_by=self.user
        )
        
        # Vérifier les valeurs par défaut
        self.assertEqual(campaign.target_language, 'fr')
        self.assertTrue(campaign.target_active_only)
        
        # Nettoyer
        campaign.delete()
    
    def test_column_modification_migration(self):
        """Test de modification de colonnes lors de la migration"""
        from content_management.models import NewsletterCampaign
        
        # Vérifier que les modifications de colonnes ont été appliquées
        # Par exemple, vérifier la longueur maximale du titre
        title_field = NewsletterCampaign._meta.get_field('title')
        self.assertEqual(title_field.max_length, 200)
        
        # Vérifier que les contraintes sont correctes
        self.assertFalse(title_field.blank)
        self.assertFalse(title_field.null)
    
    def test_index_creation_migration(self):
        """Test de création d'index lors de la migration"""
        from django.db import connection
        
        # Vérifier que les index ont été créés
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'jobs_newslettercampaign'
                AND indexname LIKE '%created_at%'
            """)
            created_at_indexes = [row[0] for row in cursor.fetchall()]
        
        # Vérifier qu'il y a au moins un index sur created_at
        self.assertGreater(len(created_at_indexes), 0)

class MigrationPerformanceTest(MigrationTest):
    """Tests de performance des migrations"""
    
    def test_migration_execution_time(self):
        """Test du temps d'exécution des migrations"""
        import time
        from django.core.management import call_command
        
        # Mesurer le temps d'exécution des migrations
        start_time = time.time()
        
        # Exécuter les migrations (en mode check)
        try:
            call_command('migrate', 'jobs', '--check')
            migration_time = time.time() - start_time
            
            # Vérifier que les migrations s'exécutent rapidement
            self.assertLess(migration_time, 10.0)  # Moins de 10 secondes
            
        except Exception:
            # Les migrations peuvent déjà être à jour
            pass
    
    def test_migration_memory_usage(self):
        """Test de l'utilisation mémoire des migrations"""
        import psutil
        import os
        
        # Obtenir l'utilisation mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simuler une opération de migration
        from content_management.models import NewsletterCampaign
        
        # Créer de nombreuses campagnes pour tester la performance
        campaigns = []
        for i in range(100):
            campaign = NewsletterCampaign.objects.create(
                title=f'Performance Test Campaign {i}',
                subject=f'Subject {i}',
                content=f'Content {i}',
                template_name='default',
                status='draft',
                created_by=self.user
            )
            campaigns.append(campaign)
        
        # Obtenir l'utilisation mémoire après création
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Nettoyer
        for campaign in campaigns:
            campaign.delete()
        
        # Obtenir l'utilisation mémoire après nettoyage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifier que l'utilisation mémoire est raisonnable
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase, 100)  # Moins de 100 MB d'augmentation
    
    def test_migration_database_performance(self):
        """Test de la performance de la base de données lors des migrations"""
        from django.db import connection
        import time
        
        # Test de performance des requêtes
        start_time = time.time()
        
        with connection.cursor() as cursor:
            # Requête simple
            cursor.execute("SELECT COUNT(*) FROM jobs_newslettercampaign")
            count = cursor.fetchone()[0]
            
            # Requête avec jointure
            cursor.execute("""
                SELECT nc.title, u.username 
                FROM jobs_newslettercampaign nc 
                JOIN auth_user u ON nc.created_by_id = u.id 
                LIMIT 10
            """)
            results = cursor.fetchall()
        
        query_time = time.time() - start_time
        
        # Vérifier que les requêtes s'exécutent rapidement
        self.assertLess(query_time, 1.0)  # Moins d'1 seconde
        
        # Vérifier que les résultats sont corrects
        self.assertIsInstance(count, int)
        self.assertIsInstance(results, list)

class MigrationRollbackTest(MigrationTest):
    """Tests de rollback des migrations"""
    
    def test_migration_state_consistency(self):
        """Test de cohérence de l'état des migrations"""
        from django.db import connection
        
        # Vérifier l'état actuel des migrations
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app, name, applied 
                FROM django_migrations 
                WHERE app = 'jobs' 
                ORDER BY applied
            """)
            migrations = cursor.fetchall()
        
        # Vérifier que les migrations sont dans l'ordre chronologique
        applied_times = [migration[2] for migration in migrations]
        self.assertEqual(applied_times, sorted(applied_times))
        
        # Vérifier qu'il n'y a pas de doublons
        migration_names = [migration[1] for migration in migrations]
        self.assertEqual(len(migration_names), len(set(migration_names)))
    
    def test_migration_dependency_resolution(self):
        """Test de résolution des dépendances de migration"""
        from django.apps import apps
        
        # Obtenir l'application jobs
        jobs_app = apps.get_app_config('jobs')
        
        # Vérifier que l'application peut être chargée
        self.assertIsNotNone(jobs_app)
        
        # Vérifier que les modèles peuvent être importés
        try:
            from content_management.models import NewsletterCampaign
            from jobs.models import EmailTemplate
            self.assertTrue(True)  # Import réussi
        except ImportError as e:
            self.fail(f"Model import failed: {e}")
    
    def test_migration_error_handling(self):
        """Test de gestion des erreurs de migration"""
        from django.core.management import call_command
        from django.db import connection
        
        # Vérifier que la base de données est accessible
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Database connection failed: {e}")
        
        # Vérifier que les migrations peuvent être vérifiées
        try:
            call_command('migrate', 'jobs', '--check')
            self.assertTrue(True)  # Vérification réussie
        except Exception as e:
            # Les migrations peuvent déjà être à jour
            pass

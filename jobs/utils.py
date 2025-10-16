"""
Utilitaires pour l'application jobs
"""
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db import connection
from django.core.mail import get_connection
import psutil

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestionnaire de cache pour l'application jobs
    """
    
    @staticmethod
    def get_cache_key(prefix: str, identifier: str = None) -> str:
        """
        Génère une clé de cache standardisée
        """
        if identifier:
            return f"jobs_{prefix}_{identifier}"
        return f"jobs_{prefix}"
    
    @staticmethod
    def get_cached_data(key: str, default: Any = None) -> Any:
        """
        Récupère des données du cache
        """
        try:
            return cache.get(key)
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération du cache {key}: {str(e)}")
            return default
    
    @staticmethod
    def set_cached_data(key: str, data: Any, timeout: int = 300) -> bool:
        """
        Stocke des données dans le cache
        """
        try:
            cache.set(key, data, timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Erreur lors du stockage dans le cache {key}: {str(e)}")
            return False
    
    @staticmethod
    def delete_cached_data(key: str) -> bool:
        """
        Supprime des données du cache
        """
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Erreur lors de la suppression du cache {key}: {str(e)}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """
        Efface tous les éléments du cache correspondant à un pattern
        """
        try:
            # Note: Django cache ne supporte pas les patterns globaux
            # Cette méthode est un placeholder pour une implémentation future
            logger.info(f"Effacement du pattern de cache: {pattern}")
            return 0
        except Exception as e:
            logger.warning(f"Erreur lors de l'effacement du pattern {pattern}: {str(e)}")
            return 0
    
    @staticmethod
    def get_cached_performance_metrics() -> Dict[str, Any]:
        """
        Récupère les métriques de performance mises en cache
        """
        return CacheManager.get_cached_data('jobs_performance_metrics', {})
    
    @staticmethod
    def set_cached_performance_metrics(metrics: Dict[str, Any]) -> bool:
        """
        Stocke les métriques de performance dans le cache
        """
        return CacheManager.set_cached_data('jobs_performance_metrics', metrics, timeout=600)
    
    @staticmethod
    def get_cached_system_health() -> Dict[str, Any]:
        """
        Récupère la santé du système mise en cache
        """
        return CacheManager.get_cached_data('jobs_system_health', {})
    
    @staticmethod
    def set_cached_system_health(health: Dict[str, Any]) -> bool:
        """
        Stocke la santé du système dans le cache
        """
        return CacheManager.set_cached_data('jobs_system_health', health, timeout=300)

class PerformanceMonitor:
    """
    Moniteur de performance pour l'application jobs
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
    
    def start_operation(self, operation_name: str) -> None:
        """
        Démarre le chronométrage d'une opération
        """
        self.metrics[operation_name] = {
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        }
    
    def end_operation(self, operation_name: str) -> float:
        """
        Termine le chronométrage d'une opération et retourne la durée
        """
        if operation_name in self.metrics:
            self.metrics[operation_name]['end_time'] = time.time()
            duration = self.metrics[operation_name]['end_time'] - self.metrics[operation_name]['start_time']
            self.metrics[operation_name]['duration'] = duration
            return duration
        return 0.0
    
    def get_operation_duration(self, operation_name: str) -> float:
        """
        Récupère la durée d'une opération
        """
        if operation_name in self.metrics:
            return self.metrics[operation_name].get('duration', 0.0)
        return 0.0
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Récupère toutes les métriques
        """
        return self.metrics.copy()
    
    def reset(self) -> None:
        """
        Réinitialise le moniteur
        """
        self.start_time = time.time()
        self.metrics = {}

class SystemMonitor:
    """
    Moniteur de santé du système
    """
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Récupère les informations système de base
        """
        try:
            return {
                'timestamp': timezone.now().isoformat(),
                'platform': psutil.sys.platform,
                'python_version': psutil.sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_partitions': len(psutil.disk_partitions())
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations système: {str(e)}")
            return {}
    
    @staticmethod
    def get_cpu_usage() -> Dict[str, Any]:
        """
        Récupère l'utilisation du CPU
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            return {
                'usage_percent': cpu_percent,
                'frequency_current': cpu_freq.current if cpu_freq else None,
                'frequency_min': cpu_freq.min if cpu_freq else None,
                'frequency_max': cpu_freq.max if cpu_freq else None,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisation CPU: {str(e)}")
            return {}
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """
        Récupère l'utilisation de la mémoire
        """
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisation mémoire: {str(e)}")
            return {}
    
    @staticmethod
    def get_disk_usage(path: str = None) -> Dict[str, Any]:
        """
        Récupère l'utilisation du disque
        """
        try:
            if not path:
                path = settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else '/'
            
            disk_usage = psutil.disk_usage(path)
            
            return {
                'path': path,
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': (disk_usage.used / disk_usage.total) * 100
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisation disque: {str(e)}")
            return {}
    
    @staticmethod
    def get_network_usage() -> Dict[str, Any]:
        """
        Récupère l'utilisation du réseau
        """
        try:
            network_io = psutil.net_io_counters()
            
            return {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
                'errin': network_io.errin,
                'errout': network_io.errout,
                'dropin': network_io.dropin,
                'dropout': network_io.dropout
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisation réseau: {str(e)}")
            return {}
    
    @staticmethod
    def get_database_connections() -> Dict[str, Any]:
        """
        Récupère les informations sur les connexions de base de données
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity")
                active_connections = cursor.fetchone()[0]
                
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                active_queries = cursor.fetchone()[0]
                
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'")
                idle_connections = cursor.fetchone()[0]
                
                return {
                    'total_connections': active_connections,
                    'active_queries': active_queries,
                    'idle_connections': idle_connections,
                    'max_connections': getattr(settings, 'DATABASE_MAX_CONNECTIONS', 100)
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des connexions DB: {str(e)}")
            return {}
    
    @staticmethod
    def get_celery_status() -> Dict[str, Any]:
        """
        Récupère le statut de Celery
        """
        try:
            from celery import current_app
            
            inspect = current_app.control.inspect()
            
            # Statut des workers
            active_workers = inspect.active()
            registered_workers = inspect.registered()
            stats_workers = inspect.stats()
            
            worker_count = len(active_workers) if active_workers else 0
            registered_count = len(registered_workers) if registered_workers else 0
            
            # Statistiques des tâches
            task_stats = {}
            if stats_workers:
                for worker_name, stats in stats_workers.items():
                    task_stats[worker_name] = {
                        'pool': stats.get('pool', {}),
                        'total': stats.get('total', {}),
                        'load': stats.get('load', {})
                    }
            
            return {
                'active_workers': worker_count,
                'registered_workers': registered_count,
                'worker_stats': task_stats,
                'queues': getattr(current_app.conf, 'task_routes', {})
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut Celery: {str(e)}")
            return {}
    
    @staticmethod
    def get_comprehensive_health_status() -> Dict[str, Any]:
        """
        Récupère un statut de santé complet du système
        """
        try:
            health_status = {
                'timestamp': timezone.now().isoformat(),
                'overall_status': 'healthy',
                'system_info': SystemMonitor.get_system_info(),
                'cpu': SystemMonitor.get_cpu_usage(),
                'memory': SystemMonitor.get_memory_usage(),
                'disk': SystemMonitor.get_disk_usage(),
                'network': SystemMonitor.get_network_usage(),
                'database': SystemMonitor.get_database_connections(),
                'celery': SystemMonitor.get_celery_status(),
                'warnings': [],
                'errors': []
            }
            
            # Évaluer la santé globale
            warnings = []
            errors = []
            
            # Vérifier l'utilisation CPU
            if health_status['cpu'].get('usage_percent', 0) > 90:
                warnings.append("Utilisation CPU élevée")
                health_status['overall_status'] = 'warning'
            elif health_status['cpu'].get('usage_percent', 0) > 95:
                errors.append("Utilisation CPU critique")
                health_status['overall_status'] = 'critical'
            
            # Vérifier l'utilisation mémoire
            if health_status['memory'].get('percent', 0) > 90:
                warnings.append("Utilisation mémoire élevée")
                health_status['overall_status'] = 'warning'
            elif health_status['memory'].get('percent', 0) > 95:
                errors.append("Utilisation mémoire critique")
                health_status['overall_status'] = 'critical'
            
            # Vérifier l'utilisation disque
            if health_status['disk'].get('percent', 0) > 90:
                warnings.append("Espace disque faible")
                health_status['overall_status'] = 'warning'
            elif health_status['disk'].get('percent', 0) > 95:
                errors.append("Espace disque critique")
                health_status['overall_status'] = 'critical'
            
            # Vérifier les connexions de base de données
            db_connections = health_status['database'].get('total_connections', 0)
            max_connections = health_status['database'].get('max_connections', 100)
            if db_connections > max_connections * 0.8:
                warnings.append("Connexions de base de données élevées")
                health_status['overall_status'] = 'warning'
            
            # Vérifier Celery
            if health_status['celery'].get('active_workers', 0) == 0:
                errors.append("Aucun worker Celery actif")
                health_status['overall_status'] = 'critical'
            
            health_status['warnings'] = warnings
            health_status['errors'] = errors
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut de santé: {str(e)}")
            return {
                'timestamp': timezone.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }

class EmailValidator:
    """
    Validateur d'emails
    """
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Vérifie si un email est valide
        """
        import re
        
        # Pattern basique pour la validation d'email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email or not isinstance(email, str):
            return False
        
        return bool(re.match(pattern, email))
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalise un email (minuscules, espaces supprimés)
        """
        if not email:
            return ""
        
        return email.strip().lower()
    
    @staticmethod
    def extract_domain(email: str) -> str:
        """
        Extrait le domaine d'un email
        """
        if not email or '@' not in email:
            return ""
        
        return email.split('@')[1]
    
    @staticmethod
    def is_disposable_email(email: str) -> bool:
        """
        Vérifie si un email provient d'un service jetable
        """
        # Liste des domaines jetables connus (à étendre)
        disposable_domains = {
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'throwaway.email', 'yopmail.com'
        }
        
        domain = EmailValidator.extract_domain(email)
        return domain in disposable_domains

class TaskScheduler:
    """
    Planificateur de tâches
    """
    
    @staticmethod
    def calculate_next_run_time(schedule_type: str, **kwargs) -> datetime:
        """
        Calcule la prochaine heure d'exécution d'une tâche
        """
        now = timezone.now()
        
        if schedule_type == 'hourly':
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        elif schedule_type == 'daily':
            hour = kwargs.get('hour', 0)
            minute = kwargs.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif schedule_type == 'weekly':
            day_of_week = kwargs.get('day_of_week', 0)  # 0 = Lundi
            hour = kwargs.get('hour', 0)
            minute = kwargs.get('minute', 0)
            
            current_day = now.weekday()
            days_ahead = day_of_week - current_day
            
            if days_ahead <= 0:
                days_ahead += 7
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
            return next_run
        
        elif schedule_type == 'monthly':
            day_of_month = kwargs.get('day_of_month', 1)
            hour = kwargs.get('hour', 0)
            minute = kwargs.get('minute', 0)
            
            if now.day > day_of_month:
                # Passer au mois suivant
                if now.month == 12:
                    next_month = now.replace(year=now.year + 1, month=1, day=day_of_month)
                else:
                    next_month = now.replace(month=now.month + 1, day=day_of_month)
            else:
                next_month = now.replace(day=day_of_month)
            
            return next_month.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        else:
            # Par défaut, exécuter dans 1 heure
            return now + timedelta(hours=1)
    
    @staticmethod
    def is_time_to_run(last_run: datetime, schedule_type: str, **kwargs) -> bool:
        """
        Vérifie s'il est temps d'exécuter une tâche
        """
        now = timezone.now()
        next_run = TaskScheduler.calculate_next_run_time(schedule_type, **kwargs)
        
        return now >= next_run

class DataExporter:
    """
    Exportateur de données
    """
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exporte des données au format CSV
        """
        import csv
        import tempfile
        import os
        
        if not data:
            return ""
        
        if not filename:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"export_{timestamp}.csv"
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        
        try:
            # Écrire les données CSV
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            temp_file.close()
            
            # Lire le contenu du fichier
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Supprimer le fichier temporaire
            os.unlink(temp_file.name)
            
            return content
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {str(e)}")
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return ""
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Exporte des données au format JSON
        """
        try:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {str(e)}")
            return "[]"
    
    @staticmethod
    def export_to_xml(data: List[Dict[str, Any]], root_element: str = "data", item_element: str = "item") -> str:
        """
        Exporte des données au format XML
        """
        try:
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_element}>\n'
            
            for item in data:
                xml_content += f'  <{item_element}>\n'
                for key, value in item.items():
                    # Nettoyer la clé pour XML
                    clean_key = key.replace(' ', '_').replace('-', '_').lower()
                    xml_content += f'    <{clean_key}>{value}</{clean_key}>\n'
                xml_content += f'  </{item_element}>\n'
            
            xml_content += f'</{root_element}>'
            return xml_content
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export XML: {str(e)}")
            return ""

class SecurityUtils:
    """
    Utilitaires de sécurité
    """
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Génère un token sécurisé
        """
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha256') -> str:
        """
        Hash des données avec l'algorithme spécifié
        """
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        else:
            raise ValueError(f"Algorithme de hash non supporté: {algorithm}")
    
    @staticmethod
    def validate_file_upload(file_obj, allowed_extensions: List[str], max_size: int) -> Dict[str, Any]:
        """
        Valide un fichier uploadé
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Vérifier l'extension
            if hasattr(file_obj, 'name'):
                file_extension = file_obj.name.split('.')[-1].lower()
                if file_extension not in allowed_extensions:
                    result['errors'].append(f"Extension de fichier non autorisée: {file_extension}")
            
            # Vérifier la taille
            if hasattr(file_obj, 'size'):
                if file_obj.size > max_size:
                    result['errors'].append(f"Fichier trop volumineux: {file_obj.size} bytes (max: {max_size})")
                elif file_obj.size > max_size * 0.8:
                    result['warnings'].append("Fichier proche de la limite de taille")
            
            # Si pas d'erreurs, le fichier est valide
            if not result['errors']:
                result['valid'] = True
            
        except Exception as e:
            result['errors'].append(f"Erreur lors de la validation: {str(e)}")
        
        return result

class NotificationManager:
    """
    Gestionnaire de notifications
    """
    
    @staticmethod
    def send_email_notification(to_email: str, subject: str, message: str, priority: int = 2) -> bool:
        """
        Envoie une notification par email
        """
        try:
            from django.core.mail import send_mail
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False
            )
            
            logger.info(f"Notification email envoyée à {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification email: {str(e)}")
            return False
    
    @staticmethod
    def send_system_alert(alert_type: str, message: str, severity: str = 'warning') -> bool:
        """
        Envoie une alerte système
        """
        try:
            # Log de l'alerte
            if severity == 'critical':
                logger.critical(f"ALERTE CRITIQUE [{alert_type}]: {message}")
            elif severity == 'error':
                logger.error(f"ALERTE ERREUR [{alert_type}]: {message}")
            elif severity == 'warning':
                logger.warning(f"ALERTE AVERTISSEMENT [{alert_type}]: {message}")
            else:
                logger.info(f"ALERTE INFO [{alert_type}]: {message}")
            
            # Envoyer aux administrateurs si configuré
            if hasattr(settings, 'ADMIN_EMAILS') and severity in ['critical', 'error']:
                for admin_email in settings.ADMIN_EMAILS:
                    NotificationManager.send_email_notification(
                        admin_email,
                        f"ALERTE SYSTÈME: {alert_type}",
                        f"Type: {alert_type}\nSévérité: {severity}\nMessage: {message}",
                        priority=4
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte système: {str(e)}")
            return False

# Instances globales
cache_manager = CacheManager()
performance_monitor = PerformanceMonitor()
system_monitor = SystemMonitor()
email_validator = EmailValidator()
task_scheduler = TaskScheduler()
data_exporter = DataExporter()
security_utils = SecurityUtils()
notification_manager = NotificationManager()

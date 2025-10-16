"""
Exceptions personnalisées pour l'application jobs
"""

class JobsBaseException(Exception):
    """Exception de base pour l'application jobs"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> dict:
        """Convertit l'exception en dictionnaire"""
        return {
            'error': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'exception_type': self.__class__.__name__
        }

class EmailTemplateException(JobsBaseException):
    """Exception liée aux templates d'email"""
    
    def __init__(self, message: str, template_name: str = None, details: dict = None):
        super().__init__(message, 'EMAIL_TEMPLATE_ERROR', details)
        self.template_name = template_name
        if self.template_name:
            self.details['template_name'] = self.template_name

class EmailQueueException(JobsBaseException):
    """Exception liée à la file d'attente des emails"""
    
    def __init__(self, message: str, email_id: int = None, details: dict = None):
        super().__init__(message, 'EMAIL_QUEUE_ERROR', details)
        self.email_id = email_id
        if self.email_id:
            self.details['email_id'] = self.email_id

class NewsletterException(JobsBaseException):
    """Exception liée aux newsletters"""
    
    def __init__(self, message: str, campaign_id: int = None, subscriber_email: str = None, details: dict = None):
        super().__init__(message, 'NEWSLETTER_ERROR', details)
        self.campaign_id = campaign_id
        self.subscriber_email = subscriber_email
        if self.campaign_id:
            self.details['campaign_id'] = self.campaign_id
        if self.subscriber_email:
            self.details['subscriber_email'] = self.subscriber_email

class TaskExecutionException(JobsBaseException):
    """Exception liée à l'exécution des tâches"""
    
    def __init__(self, message: str, task_id: str = None, task_name: str = None, details: dict = None):
        super().__init__(message, 'TASK_EXECUTION_ERROR', details)
        self.task_id = task_id
        self.task_name = task_name
        if self.task_id:
            self.details['task_id'] = self.task_id
        if self.task_name:
            self.details['task_name'] = self.task_name

class WorkerException(JobsBaseException):
    """Exception liée aux workers Celery"""
    
    def __init__(self, message: str, worker_name: str = None, details: dict = None):
        super().__init__(message, 'WORKER_ERROR', details)
        self.worker_name = worker_name
        if self.worker_name:
            self.details['worker_name'] = self.worker_name

class QueueException(JobsBaseException):
    """Exception liée aux queues Celery"""
    
    def __init__(self, message: str, queue_name: str = None, details: dict = None):
        super().__init__(message, 'QUEUE_ERROR', details)
        self.queue_name = queue_name
        if self.queue_name:
            self.details['queue_name'] = self.queue_name

class SystemHealthException(JobsBaseException):
    """Exception liée à la santé du système"""
    
    def __init__(self, message: str, component: str = None, details: dict = None):
        super().__init__(message, 'SYSTEM_HEALTH_ERROR', details)
        self.component = component
        if self.component:
            self.details['component'] = self.component

class ConfigurationException(JobsBaseException):
    """Exception liée à la configuration"""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        super().__init__(message, 'CONFIGURATION_ERROR', details)
        self.config_key = config_key
        if self.config_key:
            self.details['config_key'] = self.config_key

class ValidationException(JobsBaseException):
    """Exception liée à la validation des données"""
    
    def __init__(self, message: str, field_name: str = None, value: any = None, details: dict = None):
        super().__init__(message, 'VALIDATION_ERROR', details)
        self.field_name = field_name
        self.value = value
        if self.field_name:
            self.details['field_name'] = self.field_name
        if self.value is not None:
            self.details['value'] = str(self.value)

class DatabaseException(JobsBaseException):
    """Exception liée à la base de données"""
    
    def __init__(self, message: str, table_name: str = None, operation: str = None, details: dict = None):
        super().__init__(message, 'DATABASE_ERROR', details)
        self.table_name = table_name
        self.operation = operation
        if self.table_name:
            self.details['table_name'] = self.table_name
        if self.operation:
            self.details['operation'] = self.operation

class EmailDeliveryException(JobsBaseException):
    """Exception liée à la livraison des emails"""
    
    def __init__(self, message: str, recipient: str = None, smtp_error: str = None, details: dict = None):
        super().__init__(message, 'EMAIL_DELIVERY_ERROR', details)
        self.recipient = recipient
        self.smtp_error = smtp_error
        if self.recipient:
            self.details['recipient'] = self.recipient
        if self.smtp_error:
            self.details['smtp_error'] = self.smtp_error

class RateLimitException(JobsBaseException):
    """Exception liée aux limites de taux"""
    
    def __init__(self, message: str, limit_type: str = None, current_count: int = None, max_count: int = None, details: dict = None):
        super().__init__(message, 'RATE_LIMIT_ERROR', details)
        self.limit_type = limit_type
        self.current_count = current_count
        self.max_count = max_count
        if self.limit_type:
            self.details['limit_type'] = self.limit_type
        if self.current_count is not None:
            self.details['current_count'] = self.current_count
        if self.max_count is not None:
            self.details['max_count'] = self.max_count

class ResourceNotFoundException(JobsBaseException):
    """Exception liée aux ressources non trouvées"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: any = None, details: dict = None):
        super().__init__(message, 'RESOURCE_NOT_FOUND', details)
        self.resource_type = resource_type
        self.resource_id = resource_id
        if self.resource_type:
            self.details['resource_type'] = self.resource_type
        if self.resource_id is not None:
            self.details['resource_id'] = str(self.resource_id)

class PermissionException(JobsBaseException):
    """Exception liée aux permissions"""
    
    def __init__(self, message: str, user_id: int = None, required_permission: str = None, details: dict = None):
        super().__init__(message, 'PERMISSION_ERROR', details)
        self.user_id = user_id
        self.required_permission = required_permission
        if self.user_id:
            self.details['user_id'] = self.user_id
        if self.required_permission:
            self.details['required_permission'] = self.required_permission

class TimeoutException(JobsBaseException):
    """Exception liée aux timeouts"""
    
    def __init__(self, message: str, timeout_seconds: int = None, operation: str = None, details: dict = None):
        super().__init__(message, 'TIMEOUT_ERROR', details)
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        if self.timeout_seconds:
            self.details['timeout_seconds'] = self.timeout_seconds
        if self.operation:
            self.details['operation'] = self.operation

class RetryableException(JobsBaseException):
    """Exception qui peut être retentée"""
    
    def __init__(self, message: str, max_retries: int = None, current_retry: int = None, retry_after: int = None, details: dict = None):
        super().__init__(message, 'RETRYABLE_ERROR', details)
        self.max_retries = max_retries
        self.current_retry = current_retry
        self.retry_after = retry_after
        if self.max_retries is not None:
            self.details['max_retries'] = self.max_retries
        if self.current_retry is not None:
            self.details['current_retry'] = self.current_retry
        if self.retry_after is not None:
            self.details['retry_after'] = self.retry_after

class BulkOperationException(JobsBaseException):
    """Exception liée aux opérations en masse"""
    
    def __init__(self, message: str, total_items: int = None, successful_items: int = None, failed_items: int = None, details: dict = None):
        super().__init__(message, 'BULK_OPERATION_ERROR', details)
        self.total_items = total_items
        self.successful_items = successful_items
        self.failed_items = failed_items
        if self.total_items is not None:
            self.details['total_items'] = self.total_items
        if self.successful_items is not None:
            self.details['successful_items'] = self.successful_items
        if self.failed_items is not None:
            self.details['failed_items'] = self.failed_items

# Exceptions spécifiques aux templates
class TemplateNotFoundException(EmailTemplateException):
    """Exception levée quand un template n'est pas trouvé"""
    
    def __init__(self, template_name: str):
        super().__init__(f"Template '{template_name}' non trouvé", template_name)

class TemplateValidationException(EmailTemplateException):
    """Exception levée quand un template est invalide"""
    
    def __init__(self, template_name: str, validation_errors: list):
        super().__init__(f"Template '{template_name}' invalide", template_name, {'validation_errors': validation_errors})

class TemplateRenderingException(EmailTemplateException):
    """Exception levée lors du rendu d'un template"""
    
    def __init__(self, template_name: str, context: dict, original_error: str):
        super().__init__(f"Erreur lors du rendu du template '{template_name}'", template_name, {
            'context': context,
            'original_error': original_error
        })

# Exceptions spécifiques aux emails
class EmailCreationException(EmailQueueException):
    """Exception levée lors de la création d'un email"""
    
    def __init__(self, message: str, email_data: dict = None):
        super().__init__(message, details={'email_data': email_data})

class EmailSendingException(EmailQueueException):
    """Exception levée lors de l'envoi d'un email"""
    
    def __init__(self, email_id: int, smtp_error: str = None):
        super().__init__(f"Erreur lors de l'envoi de l'email {email_id}", email_id, {'smtp_error': smtp_error})

class EmailRetryException(EmailQueueException):
    """Exception levée lors de la retry d'un email"""
    
    def __init__(self, email_id: int, max_retries: int, current_retry: int):
        super().__init__(f"Impossible de relancer l'email {email_id} (retry {current_retry}/{max_retries})", email_id, {
            'max_retries': max_retries,
            'current_retry': current_retry
        })

# Exceptions spécifiques aux newsletters
class NewsletterCampaignException(NewsletterException):
    """Exception levée lors de la gestion d'une campagne de newsletter"""
    
    def __init__(self, message: str, campaign_id: int):
        super().__init__(message, campaign_id)

class NewsletterSubscriberException(NewsletterException):
    """Exception levée lors de la gestion d'un abonné"""
    
    def __init__(self, message: str, subscriber_email: str):
        super().__init__(message, subscriber_email=subscriber_email)

class NewsletterDeliveryException(NewsletterException):
    """Exception levée lors de la livraison d'une newsletter"""
    
    def __init__(self, campaign_id: int, subscriber_email: str, delivery_error: str):
        super().__init__(f"Erreur de livraison pour la campagne {campaign_id}", campaign_id, subscriber_email, {
            'delivery_error': delivery_error
        })

# Exceptions spécifiques aux tâches
class TaskNotFoundException(TaskExecutionException):
    """Exception levée quand une tâche n'est pas trouvée"""
    
    def __init__(self, task_id: str):
        super().__init__(f"Tâche '{task_id}' non trouvée", task_id)

class TaskExecutionTimeoutException(TaskExecutionException, TimeoutException):
    """Exception levée quand une tâche expire"""
    
    def __init__(self, task_id: str, timeout_seconds: int):
        super().__init__(f"Tâche '{task_id}' expirée après {timeout_seconds} secondes", task_id, timeout_seconds)

class TaskRetryException(TaskExecutionException, RetryableException):
    """Exception levée lors de la retry d'une tâche"""
    
    def __init__(self, task_id: str, max_retries: int, current_retry: int):
        super().__init__(f"Retry de la tâche '{task_id}' ({current_retry}/{max_retries})", task_id, max_retries, current_retry)

# Exceptions spécifiques aux workers
class WorkerNotFoundException(WorkerException):
    """Exception levée quand un worker n'est pas trouvé"""
    
    def __init__(self, worker_name: str):
        super().__init__(f"Worker '{worker_name}' non trouvé", worker_name)

class WorkerShutdownException(WorkerException):
    """Exception levée lors de l'arrêt d'un worker"""
    
    def __init__(self, worker_name: str, shutdown_error: str = None):
        super().__init__(f"Erreur lors de l'arrêt du worker '{worker_name}'", worker_name, {'shutdown_error': shutdown_error})

# Exceptions spécifiques aux queues
class QueueNotFoundException(QueueException):
    """Exception levée quand une queue n'est pas trouvée"""
    
    def __init__(self, queue_name: str):
        super().__init__(f"Queue '{queue_name}' non trouvée", queue_name)

class QueuePurgeException(QueueException):
    """Exception levée lors du vidage d'une queue"""
    
    def __init__(self, queue_name: str, purge_error: str = None):
        super().__init__(f"Erreur lors du vidage de la queue '{queue_name}'", queue_name, {'purge_error': purge_error})

# Exceptions spécifiques au système
class SystemResourceException(SystemHealthException):
    """Exception levée quand une ressource système est épuisée"""
    
    def __init__(self, component: str, resource_type: str, current_usage: float, max_usage: float):
        super().__init__(f"Ressource {resource_type} épuisée pour {component}: {current_usage}/{max_usage}", component, {
            'resource_type': resource_type,
            'current_usage': current_usage,
            'max_usage': max_usage
        })

class SystemConnectionException(SystemHealthException):
    """Exception levée lors de problèmes de connexion"""
    
    def __init__(self, component: str, connection_type: str, connection_error: str):
        super().__init__(f"Erreur de connexion {connection_type} pour {component}", component, {
            'connection_type': connection_type,
            'connection_error': connection_error
        })

# Exceptions spécifiques à la configuration
class MissingConfigurationException(ConfigurationException):
    """Exception levée quand une configuration est manquante"""
    
    def __init__(self, config_key: str):
        super().__init__(f"Configuration manquante: {config_key}", config_key)

class InvalidConfigurationException(ConfigurationException):
    """Exception levée quand une configuration est invalide"""
    
    def __init__(self, config_key: str, config_value: any, expected_format: str = None):
        super().__init__(f"Configuration invalide pour {config_key}: {config_value}", config_key, {
            'config_value': config_value,
            'expected_format': expected_format
        })

# Exceptions spécifiques à la validation
class FieldValidationException(ValidationException):
    """Exception levée lors de la validation d'un champ"""
    
    def __init__(self, field_name: str, value: any, validation_rule: str, details: dict = None):
        super().__init__(f"Validation échouée pour le champ '{field_name}': {validation_rule}", field_name, value, details)

class RequiredFieldException(ValidationException):
    """Exception levée quand un champ requis est manquant"""
    
    def __init__(self, field_name: str):
        super().__init__(f"Champ requis manquant: {field_name}", field_name)

class InvalidFormatException(ValidationException):
    """Exception levée quand le format d'un champ est invalide"""
    
    def __init__(self, field_name: str, value: any, expected_format: str):
        super().__init__(f"Format invalide pour le champ '{field_name}': attendu {expected_format}", field_name, value, {
            'expected_format': expected_format
        })

# Exceptions spécifiques à la base de données
class DatabaseConnectionException(DatabaseException):
    """Exception levée lors de problèmes de connexion à la base de données"""
    
    def __init__(self, connection_error: str):
        super().__init__(f"Erreur de connexion à la base de données: {connection_error}", operation='connection', details={
            'connection_error': connection_error
        })

class DatabaseQueryException(DatabaseException):
    """Exception levée lors de problèmes de requête"""
    
    def __init__(self, table_name: str, operation: str, query_error: str):
        super().__init__(f"Erreur de requête sur {table_name}: {operation}", table_name, operation, {
            'query_error': query_error
        })

class DatabaseConstraintException(DatabaseException):
    """Exception levée lors de violations de contraintes"""
    
    def __init__(self, table_name: str, constraint_name: str, constraint_error: str):
        super().__init__(f"Violation de contrainte sur {table_name}: {constraint_name}", table_name, operation='constraint', details={
            'constraint_name': constraint_name,
            'constraint_error': constraint_error
        })

# Exceptions spécifiques à la livraison d'emails
class SMTPConnectionException(EmailDeliveryException):
    """Exception levée lors de problèmes de connexion SMTP"""
    
    def __init__(self, recipient: str, smtp_error: str):
        super().__init__(f"Erreur de connexion SMTP pour {recipient}", recipient, smtp_error)

class SMTPAuthenticationException(EmailDeliveryException):
    """Exception levée lors de problèmes d'authentification SMTP"""
    
    def __init__(self, recipient: str, smtp_error: str):
        super().__init__(f"Erreur d'authentification SMTP pour {recipient}", recipient, smtp_error)

class SMTPRecipientException(EmailDeliveryException):
    """Exception levée lors de problèmes avec le destinataire"""
    
    def __init__(self, recipient: str, smtp_error: str):
        super().__init__(f"Erreur de destinataire SMTP pour {recipient}", recipient, smtp_error)

# Exceptions spécifiques aux limites de taux
class EmailRateLimitException(RateLimitException):
    """Exception levée lors de dépassement des limites d'envoi d'emails"""
    
    def __init__(self, limit_type: str, current_count: int, max_count: int):
        super().__init__(f"Limite de taux dépassée pour {limit_type}: {current_count}/{max_count}", limit_type, current_count, max_count)

class TaskRateLimitException(RateLimitException):
    """Exception levée lors de dépassement des limites d'exécution de tâches"""
    
    def __init__(self, limit_type: str, current_count: int, max_count: int):
        super().__init__(f"Limite de taux dépassée pour {limit_type}: {current_count}/{max_count}", limit_type, current_count, max_count)

# Exceptions spécifiques aux ressources
class EmailTemplateNotFoundException(ResourceNotFoundException):
    """Exception levée quand un template d'email n'est pas trouvé"""
    
    def __init__(self, template_id: int):
        super().__init__(f"Template d'email {template_id} non trouvé", "EmailTemplate", template_id)

class EmailQueueNotFoundException(ResourceNotFoundException):
    """Exception levée quand un email en file d'attente n'est pas trouvé"""
    
    def __init__(self, email_id: int):
        super().__init__(f"Email en file d'attente {email_id} non trouvé", "EmailQueue", email_id)

class NewsletterLogNotFoundException(ResourceNotFoundException):
    """Exception levée quand un log de newsletter n'est pas trouvé"""
    
    def __init__(self, log_id: int):
        super().__init__(f"Log de newsletter {log_id} non trouvé", "NewsletterLog", log_id)

# Exceptions spécifiques aux permissions
class EmailTemplatePermissionException(PermissionException):
    """Exception levée lors de problèmes de permission sur les templates d'email"""
    
    def __init__(self, user_id: int, required_permission: str):
        super().__init__(f"Permission insuffisante pour accéder aux templates d'email", user_id, required_permission)

class EmailQueuePermissionException(PermissionException):
    """Exception levée lors de problèmes de permission sur la file d'attente des emails"""
    
    def __init__(self, user_id: int, required_permission: str):
        super().__init__(f"Permission insuffisante pour accéder à la file d'attente des emails", user_id, required_permission)

class NewsletterPermissionException(PermissionException):
    """Exception levée lors de problèmes de permission sur les newsletters"""
    
    def __init__(self, user_id: int, required_permission: str):
        super().__init__(f"Permission insuffisante pour accéder aux newsletters", user_id, required_permission)

# Exceptions spécifiques aux timeouts
class EmailSendingTimeoutException(TimeoutException, EmailDeliveryException):
    """Exception levée lors de timeout d'envoi d'email"""
    
    def __init__(self, recipient: str, timeout_seconds: int):
        super().__init__(f"Timeout lors de l'envoi de l'email à {recipient}", timeout_seconds, "email_sending")

class TaskExecutionTimeoutException(TimeoutException, TaskExecutionException):
    """Exception levée lors de timeout d'exécution de tâche"""
    
    def __init__(self, task_id: str, timeout_seconds: int):
        super().__init__(f"Timeout lors de l'exécution de la tâche {task_id}", timeout_seconds, "task_execution")

# Exceptions spécifiques aux opérations en masse
class EmailBulkOperationException(BulkOperationException, EmailQueueException):
    """Exception levée lors d'opérations en masse sur les emails"""
    
    def __init__(self, message: str, total_items: int, successful_items: int, failed_items: int):
        super().__init__(message, total_items, successful_items, failed_items)

class NewsletterBulkOperationException(BulkOperationException, NewsletterException):
    """Exception levée lors d'opérations en masse sur les newsletters"""
    
    def __init__(self, message: str, total_items: int, successful_items: int, failed_items: int):
        super().__init__(message, total_items, successful_items, failed_items)

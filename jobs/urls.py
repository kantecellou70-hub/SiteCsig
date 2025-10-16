"""
URLs pour l'application jobs
"""
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Dashboard des tâches
    path('dashboard/', views.jobs_dashboard, name='dashboard'),
    
    # Gestion des tâches
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<str:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<str:task_id>/cancel/', views.cancel_task, name='cancel_task'),
    path('tasks/<str:task_id>/retry/', views.retry_task, name='retry_task'),
    
    # Gestion des workers
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<str:worker_name>/', views.worker_detail, name='worker_detail'),
    path('workers/<str:worker_name>/shutdown/', views.shutdown_worker, name='shutdown_worker'),
    
    # Gestion des queues
    path('queues/', views.queue_list, name='queue_list'),
    path('queues/<str:queue_name>/', views.queue_detail, name='queue_detail'),
    path('queues/<str:queue_name>/purge/', views.purge_queue, name='purge_queue'),
    
    # Gestion des tâches programmées
    path('scheduler/', views.scheduler_status, name='scheduler_status'),
    path('scheduler/start/', views.start_scheduler, name='start_scheduler'),
    path('scheduler/stop/', views.stop_scheduler, name='stop_scheduler'),
    
    # Gestion des emails
    path('emails/', views.email_queue_list, name='email_queue_list'),
    path('emails/<int:email_id>/', views.email_queue_detail, name='email_queue_detail'),
    path('emails/<int:email_id>/retry/', views.retry_email, name='retry_email'),
    path('emails/<int:email_id>/cancel/', views.cancel_email, name='cancel_email'),
    
    # Gestion des templates d'email
    path('templates/', views.email_template_list, name='email_template_list'),
    path('templates/create/', views.email_template_create, name='email_template_create'),
    path('templates/<int:template_id>/', views.email_template_detail, name='email_template_detail'),
    path('templates/<int:template_id>/edit/', views.email_template_edit, name='email_template_edit'),
    path('templates/<int:template_id>/delete/', views.email_template_delete, name='email_template_delete'),
    
    # Gestion des logs de newsletter
    path('newsletter-logs/', views.newsletter_log_list, name='newsletter_log_list'),
    path('newsletter-logs/<int:log_id>/', views.newsletter_log_detail, name='newsletter_log_detail'),
    
    # API pour les tâches
    path('api/tasks/', views.api_task_list, name='api_task_list'),
    path('api/tasks/<str:task_id>/', views.api_task_detail, name='api_task_detail'),
    path('api/workers/', views.api_worker_list, name='api_worker_list'),
    path('api/queues/', views.api_queue_list, name='api_queue_list'),
    
    # Actions en masse
    path('bulk-actions/', views.bulk_actions, name='bulk_actions'),
    path('bulk-actions/email-queue/', views.bulk_email_queue_action, name='bulk_email_queue_action'),
    path('bulk-actions/newsletter-logs/', views.bulk_newsletter_log_action, name='bulk_newsletter_log_action'),
    
    # Statistiques et rapports
    path('stats/', views.jobs_statistics, name='statistics'),
    path('stats/email/', views.email_statistics, name='email_statistics'),
    path('stats/newsletter/', views.newsletter_statistics, name='newsletter_statistics'),
    path('stats/performance/', views.performance_statistics, name='performance_statistics'),
    
    # Configuration et maintenance
    path('config/', views.jobs_configuration, name='configuration'),
    path('config/email/', views.email_configuration, name='email_configuration'),
    path('config/celery/', views.celery_configuration, name='celery_configuration'),
    
    # Maintenance
    path('maintenance/', views.maintenance_tasks, name='maintenance_tasks'),
    path('maintenance/cleanup/', views.run_cleanup_tasks, name='run_cleanup_tasks'),
    path('maintenance/health-check/', views.run_health_check, name='run_health_check'),
    path('maintenance/backup/', views.run_backup_task, name='run_backup_task'),
    
    # Monitoring en temps réel
    path('monitoring/', views.realtime_monitoring, name='realtime_monitoring'),
    path('monitoring/workers/', views.worker_monitoring, name='worker_monitoring'),
    path('monitoring/queues/', views.queue_monitoring, name='queue_monitoring'),
    path('monitoring/tasks/', views.task_monitoring, name='task_monitoring'),
    
    # Webhooks pour les notifications
    path('webhooks/task-completed/', views.task_completed_webhook, name='task_completed_webhook'),
    path('webhooks/task-failed/', views.task_failed_webhook, name='task_failed_webhook'),
    path('webhooks/worker-status/', views.worker_status_webhook, name='worker_status_webhook'),
}

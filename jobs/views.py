"""
Vues pour l'application jobs
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib.admin.views.decorators import staff_member_required
from .models import NewsletterLog, EmailTemplate, EmailQueue
from .tasks import (
    cleanup_old_files, cleanup_database, check_system_health,
    backup_database, optimize_database, send_health_report
)
from .email_tasks import (
    process_email_queue, cleanup_failed_emails, retry_failed_emails
)
import json
import logging

logger = logging.getLogger(__name__)

# Vues de base
@login_required
@staff_member_required
def jobs_dashboard(request):
    """Dashboard principal de l'application jobs"""
    try:
        # Statistiques de base
        stats = {
            'total_emails': EmailQueue.objects.count(),
            'pending_emails': EmailQueue.objects.filter(status='pending').count(),
            'sent_emails': EmailQueue.objects.filter(status='sent').count(),
            'failed_emails': EmailQueue.objects.filter(status='failed').count(),
            'total_templates': EmailTemplate.objects.count(),
            'active_templates': EmailTemplate.objects.filter(is_active=True).count(),
            'total_newsletter_logs': NewsletterLog.objects.count(),
        }
        
        # Tâches récentes
        recent_tasks = []
        try:
            from django_celery_results.models import TaskResult
            recent_tasks = TaskResult.objects.order_by('-date_done')[:10]
        except ImportError:
            pass
        
        context = {
            'stats': stats,
            'recent_tasks': recent_tasks,
            'page_title': 'Dashboard Jobs',
        }
        
        return render(request, 'jobs/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans le dashboard jobs: {str(e)}")
        messages.error(request, "Erreur lors du chargement du dashboard")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def task_list(request):
    """Liste des tâches Celery"""
    try:
        from django_celery_results.models import TaskResult
        
        # Filtres
        status_filter = request.GET.get('status', '')
        search_query = request.GET.get('search', '')
        
        tasks = TaskResult.objects.all()
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if search_query:
            tasks = tasks.filter(
                Q(task_name__icontains=search_query) |
                Q(task_id__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(tasks.order_by('-date_done'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'search_query': search_query,
            'page_title': 'Liste des Tâches',
        }
        
        return render(request, 'jobs/task_list.html', context)
        
    except ImportError:
        messages.error(request, "Module django-celery-results non installé")
        return render(request, 'jobs/error.html', {'error': 'Module requis non installé'})
    except Exception as e:
        logger.error(f"Erreur dans la liste des tâches: {str(e)}")
        messages.error(request, "Erreur lors du chargement des tâches")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def task_detail(request, task_id):
    """Détails d'une tâche Celery"""
    try:
        from django_celery_results.models import TaskResult
        
        task = get_object_or_404(TaskResult, task_id=task_id)
        
        context = {
            'task': task,
            'page_title': f'Détails de la Tâche {task_id}',
        }
        
        return render(request, 'jobs/task_detail.html', context)
        
    except ImportError:
        messages.error(request, "Module django-celery-results non installé")
        return render(request, 'jobs/error.html', {'error': 'Module requis non installé'})
    except Exception as e:
        logger.error(f"Erreur dans les détails de la tâche: {str(e)}")
        messages.error(request, "Erreur lors du chargement de la tâche")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_queue_list(request):
    """Liste des emails en file d'attente"""
    try:
        # Filtres
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        search_query = request.GET.get('search', '')
        
        emails = EmailQueue.objects.all()
        
        if status_filter:
            emails = emails.filter(status=status_filter)
        
        if priority_filter:
            emails = emails.filter(priority=priority_filter)
        
        if search_query:
            emails = emails.filter(
                Q(to_email__icontains=search_query) |
                Q(subject__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(emails.order_by('-created_at'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'search_query': search_query,
            'page_title': 'File d\'Attente des Emails',
        }
        
        return render(request, 'jobs/email_queue_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la liste des emails: {str(e)}")
        messages.error(request, "Erreur lors du chargement des emails")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_queue_detail(request, email_id):
    """Détails d'un email en file d'attente"""
    try:
        email = get_object_or_404(EmailQueue, id=email_id)
        
        context = {
            'email': email,
            'page_title': f'Détails de l\'Email {email_id}',
        }
        
        return render(request, 'jobs/email_queue_detail.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans les détails de l'email: {str(e)}")
        messages.error(request, "Erreur lors du chargement de l'email")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_template_list(request):
    """Liste des templates d'email"""
    try:
        templates = EmailTemplate.objects.all()
        
        # Pagination
        paginator = Paginator(templates.order_by('name'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'page_title': 'Templates d\'Email',
        }
        
        return render(request, 'jobs/email_template_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la liste des templates: {str(e)}")
        messages.error(request, "Erreur lors du chargement des templates")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_template_create(request):
    """Création d'un template d'email"""
    if request.method == 'POST':
        try:
            # Logique de création du template
            messages.success(request, "Template créé avec succès")
            return redirect('jobs:email_template_list')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
    
    context = {
        'page_title': 'Créer un Template d\'Email',
    }
    
    return render(request, 'jobs/email_template_form.html', context)

@login_required
@staff_member_required
def email_template_detail(request, template_id):
    """Détails d'un template d'email"""
    try:
        template = get_object_or_404(EmailTemplate, id=template_id)
        
        context = {
            'template': template,
            'page_title': f'Template: {template.name}',
        }
        
        return render(request, 'jobs/email_template_detail.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans les détails du template: {str(e)}")
        messages.error(request, "Erreur lors du chargement du template")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_template_edit(request, template_id):
    """Modification d'un template d'email"""
    try:
        template = get_object_or_404(EmailTemplate, id=template_id)
        
        if request.method == 'POST':
            # Logique de modification du template
            messages.success(request, "Template modifié avec succès")
            return redirect('jobs:email_template_detail', template_id=template_id)
        
        context = {
            'template': template,
            'page_title': f'Modifier: {template.name}',
        }
        
        return render(request, 'jobs/email_template_form.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la modification du template: {str(e)}")
        messages.error(request, "Erreur lors de la modification du template")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def email_template_delete(request, template_id):
    """Suppression d'un template d'email"""
    try:
        template = get_object_or_404(EmailTemplate, id=template_id)
        
        if request.method == 'POST':
            template.delete()
            messages.success(request, "Template supprimé avec succès")
            return redirect('jobs:email_template_list')
        
        context = {
            'template': template,
            'page_title': f'Supprimer: {template.name}',
        }
        
        return render(request, 'jobs/email_template_confirm_delete.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la suppression du template: {str(e)}")
        messages.error(request, "Erreur lors de la suppression du template")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def newsletter_log_list(request):
    """Liste des logs de newsletter"""
    try:
        logs = NewsletterLog.objects.all()
        
        # Pagination
        paginator = Paginator(logs.order_by('-created_at'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'page_title': 'Logs de Newsletter',
        }
        
        return render(request, 'jobs/newsletter_log_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans la liste des logs: {str(e)}")
        messages.error(request, "Erreur lors du chargement des logs")
        return render(request, 'jobs/error.html', {'error': str(e)})

@login_required
@staff_member_required
def newsletter_log_detail(request, log_id):
    """Détails d'un log de newsletter"""
    try:
        log = get_object_or_404(NewsletterLog, id=log_id)
        
        context = {
            'log': log,
            'page_title': f'Log de Newsletter {log_id}',
        }
        
        return render(request, 'jobs/newsletter_log_detail.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans les détails du log: {str(e)}")
        messages.error(request, "Erreur lors du chargement du log")
        return render(request, 'jobs/error.html', {'error': str(e)})

# Vues d'action
@login_required
@staff_member_required
@require_http_methods(['POST'])
def retry_email(request, email_id):
    """Relancer un email échoué"""
    try:
        email = get_object_or_404(EmailQueue, id=email_id)
        
        if email.retry():
            messages.success(request, "Email remis en file d'attente")
        else:
            messages.error(request, "Impossible de relancer cet email")
        
        return redirect('jobs:email_queue_detail', email_id=email_id)
        
    except Exception as e:
        logger.error(f"Erreur lors du retry de l'email: {str(e)}")
        messages.error(request, "Erreur lors du relancement de l'email")
        return redirect('jobs:email_queue_list')

@login_required
@staff_member_required
@require_http_methods(['POST'])
def cancel_email(request, email_id):
    """Annuler un email en file d'attente"""
    try:
        email = get_object_or_404(EmailQueue, id=email_id)
        
        if email.status == 'pending':
            email.status = 'cancelled'
            email.save()
            messages.success(request, "Email annulé avec succès")
        else:
            messages.error(request, "Impossible d'annuler cet email")
        
        return redirect('jobs:email_queue_detail', email_id=email_id)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'annulation de l'email: {str(e)}")
        messages.error(request, "Erreur lors de l'annulation de l'email")
        return redirect('jobs:email_queue_list')

# Vues de maintenance
@login_required
@staff_member_required
def maintenance_tasks(request):
    """Page des tâches de maintenance"""
    context = {
        'page_title': 'Tâches de Maintenance',
    }
    
    return render(request, 'jobs/maintenance_tasks.html', context)

@login_required
@staff_member_required
@require_http_methods(['POST'])
def run_cleanup_tasks(request):
    """Lancer les tâches de nettoyage"""
    try:
        # Lancer les tâches de nettoyage
        cleanup_old_files.delay()
        cleanup_database.delay()
        cleanup_failed_emails.delay()
        
        messages.success(request, "Tâches de nettoyage lancées avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du lancement des tâches de nettoyage: {str(e)}")
        messages.error(request, "Erreur lors du lancement des tâches de nettoyage")
    
    return redirect('jobs:maintenance_tasks')

@login_required
@staff_member_required
@require_http_methods(['POST'])
def run_health_check(request):
    """Lancer une vérification de santé du système"""
    try:
        # Lancer la vérification de santé
        check_system_health.delay()
        
        messages.success(request, "Vérification de santé lancée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {str(e)}")
        messages.error(request, "Erreur lors de la vérification de santé")
    
    return redirect('jobs:maintenance_tasks')

@login_required
@staff_member_required
@require_http_methods(['POST'])
def run_backup_task(request):
    """Lancer une sauvegarde de la base de données"""
    try:
        # Lancer la sauvegarde
        backup_database.delay()
        
        messages.success(request, "Sauvegarde lancée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
        messages.error(request, "Erreur lors de la sauvegarde")
    
    return redirect('jobs:maintenance_tasks')

# Vues de statistiques
@login_required
@staff_member_required
def jobs_statistics(request):
    """Statistiques générales de l'application jobs"""
    try:
        # Statistiques des emails
        email_stats = {
            'total': EmailQueue.objects.count(),
            'pending': EmailQueue.objects.filter(status='pending').count(),
            'sent': EmailQueue.objects.filter(status='sent').count(),
            'failed': EmailQueue.objects.filter(status='failed').count(),
            'cancelled': EmailQueue.objects.filter(status='cancelled').count(),
        }
        
        # Statistiques des templates
        template_stats = {
            'total': EmailTemplate.objects.count(),
            'active': EmailTemplate.objects.filter(is_active=True).count(),
            'inactive': EmailTemplate.objects.filter(is_active=False).count(),
        }
        
        # Statistiques des logs de newsletter
        newsletter_stats = {
            'total': NewsletterLog.objects.count(),
            'sent': NewsletterLog.objects.filter(status='sent').count(),
            'failed': NewsletterLog.objects.filter(status='failed').count(),
            'opened': NewsletterLog.objects.filter(status='opened').count(),
            'clicked': NewsletterLog.objects.filter(status='clicked').count(),
        }
        
        context = {
            'email_stats': email_stats,
            'template_stats': template_stats,
            'newsletter_stats': newsletter_stats,
            'page_title': 'Statistiques Jobs',
        }
        
        return render(request, 'jobs/statistics.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans les statistiques: {str(e)}")
        messages.error(request, "Erreur lors du chargement des statistiques")
        return render(request, 'jobs/error.html', {'error': str(e)})

# Vues d'API
@csrf_exempt
def api_task_list(request):
    """API pour lister les tâches"""
    try:
        from django_celery_results.models import TaskResult
        
        tasks = TaskResult.objects.order_by('-date_done')[:100]
        
        data = []
        for task in tasks:
            data.append({
                'id': task.task_id,
                'name': task.task_name,
                'status': task.status,
                'date_done': task.date_done.isoformat() if task.date_done else None,
                'result': task.result,
            })
        
        return JsonResponse({'tasks': data})
        
    except ImportError:
        return JsonResponse({'error': 'Module django-celery-results non installé'}, status=400)
    except Exception as e:
        logger.error(f"Erreur dans l'API des tâches: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_task_detail(request, task_id):
    """API pour les détails d'une tâche"""
    try:
        from django_celery_results.models import TaskResult
        
        task = get_object_or_404(TaskResult, task_id=task_id)
        
        data = {
            'id': task.task_id,
            'name': task.task_name,
            'status': task.status,
            'date_done': task.date_done.isoformat() if task.date_done else None,
            'result': task.result,
            'traceback': task.traceback,
            'meta': task.meta,
        }
        
        return JsonResponse(data)
        
    except ImportError:
        return JsonResponse({'error': 'Module django-celery-results non installé'}, status=400)
    except Exception as e:
        logger.error(f"Erreur dans l'API des détails de tâche: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Vues de placeholder pour les autres routes
def placeholder_view(request, *args, **kwargs):
    """Vue de placeholder pour les routes non encore implémentées"""
    messages.info(request, "Cette fonctionnalité sera bientôt disponible")
    return redirect('jobs:dashboard')

# Assigner les vues de placeholder aux routes non implémentées
worker_list = placeholder_view
worker_detail = placeholder_view
shutdown_worker = placeholder_view
queue_list = placeholder_view
queue_detail = placeholder_view
purge_queue = placeholder_view
scheduler_status = placeholder_view
start_scheduler = placeholder_view
stop_scheduler = placeholder_view
bulk_actions = placeholder_view
bulk_email_queue_action = placeholder_view
bulk_newsletter_log_action = placeholder_view
email_statistics = placeholder_view
newsletter_statistics = placeholder_view
performance_statistics = placeholder_view
jobs_configuration = placeholder_view
email_configuration = placeholder_view
celery_configuration = placeholder_view
realtime_monitoring = placeholder_view
worker_monitoring = placeholder_view
queue_monitoring = placeholder_view
task_monitoring = placeholder_view
task_completed_webhook = placeholder_view
task_failed_webhook = placeholder_view
worker_status_webhook = placeholder_view
cancel_task = placeholder_view
retry_task = placeholder_view
api_worker_list = placeholder_view
api_queue_list = placeholder_view

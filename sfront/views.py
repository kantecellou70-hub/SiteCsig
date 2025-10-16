from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from content_management.models import (
    Article, Event, Program, Project, Partner, TeamMember, 
    Personna, Blog, SiteSettings, AboutPage, CityDistrict, CoreValue, Newsletter,
    Category, HeroStatistic, Achievement
)

def home(request):
    """Page d'accueil"""
    try:
        # Récupérer les données pour la page d'accueil
        featured_article = Article.objects.filter(
        status='published', 
        is_featured=True
        ).first()
        
        # Si pas d'article mis en avant, prendre le plus récent
        if not featured_article:
            featured_article = Article.objects.filter(
                status='published'
            ).order_by('-published_at').first()
        
        # 3 programmes récents pour la section domaines
        programs = Program.objects.filter(
            status='published'
        ).order_by('-created_at')[:3]
        
        # Articles pour la section actualités
        latest_article = Article.objects.filter(
            status='published'
        ).order_by('-published_at').first()
        
        second_article = Article.objects.filter(
            status='published'
        ).order_by('-published_at')[1:2].first()
        
        third_article = Article.objects.filter(
            status='published'
        ).order_by('-published_at')[2:3].first()
        
        # Événement le plus récent
        latest_event = Event.objects.filter(
        status='published'
        ).order_by('-start_date').first()
        
        # Partenaires
        partners = Partner.objects.filter(is_active=True).order_by('order', 'name')[:8]
        
        # Nouvelles sections
        # Valeurs fondamentales
        core_values = CoreValue.objects.filter(is_active=True).order_by('order', 'name')[:6]
        
        # Projets de recherche
        projects = Project.objects.all(
        ).order_by('-start_date')[:3]
        
        # Membres de l'équipe
        team_members = TeamMember.objects.filter(is_active=True).order_by('-order', 'last_name', 'first_name')[:4]
        
        # Statistiques héro
        hero_stats = HeroStatistic.objects.filter(is_active=True).order_by('order', 'number')[:4]
        
        # Réalisations
        achievements = Achievement.objects.filter(is_active=True).order_by('order', 'text')[:3]
        
        context = {
            'featured_article': featured_article,
            'programs': programs,
            'latest_article': latest_article,
            'second_article': second_article,
            'third_article': third_article,
            'latest_event': latest_event,
            'partners': partners,
            'core_values': core_values,
            'projects': projects,
            'team_members': team_members,
            'hero_stats': hero_stats,
            'achievements': achievements,
        }
    except Exception as e:
        # En cas d'erreur, utiliser des listes vides
        context = {
            'featured_article': None,
            'programs': [],
            'latest_article': None,
            'second_article': None,
            'third_article': None,
            'latest_event': None,
            'partners': [],
            'core_values': [],
            'projects': [],
            'team_members': [],
            'hero_stats': [],
            'achievements': [],
        }
    
    return render(request, 'sfront/home.html', context)

def about(request):
    """Page À propos"""
    try:
        about_page = AboutPage.get_active_page()
    except:
        about_page = None
    
    # Récupérer les quartiers de la cité
    try:
        city_districts = CityDistrict.objects.filter(is_active=True).order_by('order', 'name')
    except:
        city_districts = []
    
    # Récupérer les valeurs fondamentales
    try:
        core_values = CoreValue.objects.filter(is_active=True).order_by('order', 'name')
    except:
        core_values = []
    
    context = {
        'about_page': about_page,
        'city_districts': city_districts,
        'core_values': core_values,
    }
    return render(request, 'sfront/about.html', context)

def mission(request):
    """Page Mission & Vision"""
    context = {
        'page_title': 'Mission & Vision',
    }
    return render(request, 'sfront/mission.html', context)

def team(request):
    """Page équipe avec pagination"""
    team_members = TeamMember.objects.filter(is_active=True).order_by('-order', 'last_name', 'first_name')
    
    # Pagination : 10 membres par page
    paginator = Paginator(team_members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'team_members': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'sfront/team.html', context)

def team_member_detail(request, slug):
    """Page de détail d'un membre d'équipe"""
    member = get_object_or_404(TeamMember, slug=slug, is_active=True)
    
    context = {
        'member': member,
    }
    return render(request, 'sfront/team_member_detail.html', context)

def programs(request):
    """Page Programmes"""
    programs_list = Program.objects.filter(status='published').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(programs_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Nos programmes',
        'page_obj': page_obj,
        'programs': page_obj,
    }
    return render(request, 'sfront/programs.html', context)

def program_detail(request, slug):
    """Détail d'un programme"""
    program = get_object_or_404(Program, slug=slug, status='published')
    
    # Programmes similaires
    similar_programs = Program.objects.filter(
        status='published'
    ).exclude(pk=program.pk)[:3]
    
    context = {
        'program': program,
        'similar_programs': similar_programs,
        'page_title': program.title,
    }
    return render(request, 'sfront/program_detail.html', context)

def projects(request):
    """Page Projets"""
    projects_list = Project.objects.all(
    ).order_by('-start_date')
    
    # Pagination
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Nos projets',
        'page_obj': page_obj,
        'projects': page_obj,
    }
    return render(request, 'sfront/projects.html', context)

def project_detail(request, slug):
    """Détail d'un projet"""
    project = get_object_or_404(Project, slug=slug)
    
    # Projets similaires
    similar_projects = Project.objects.filter(
        status__in=['active', 'completed']
    ).exclude(pk=project.pk)[:3]
    
    context = {
        'project': project,
        'similar_projects': similar_projects,
        'page_title': project.title,
    }
    return render(request, 'sfront/project_detail.html', context)



def innovation(request):
    """Page Innovation"""
    context = {
        'page_title': 'Innovation',
    }
    return render(request, 'sfront/innovation.html', context)

def formation(request):
    """Page Formation"""
    context = {
        'page_title': 'Formation',
    }
    return render(request, 'sfront/formation.html', context)

def news(request):
    """Page Actualités"""
    articles_list = Article.objects.filter(status='published').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Actualités',
        'page_obj': page_obj,
        'articles': page_obj,
    }
    return render(request, 'sfront/news.html', context)

def article_detail(request, slug):
    """Détail d'un article"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Articles similaires
    similar_articles = Article.objects.filter(
        status='published',
        category=article.category
    ).exclude(pk=article.pk)[:3]
    
    context = {
        'article': article,
        'similar_articles': similar_articles,
        'page_title': article.title,
    }
    return render(request, 'sfront/article_detail.html', context)

def events(request):
    """Page Événements"""
    events_list = Event.objects.filter(status='published').order_by('-start_date')
    
    # Pagination
    paginator = Paginator(events_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Événements',
        'page_obj': page_obj,
        'events': page_obj,
    }
    return render(request, 'sfront/events.html', context)

def event_detail(request, slug):
    """Détail d'un événement"""
    event = get_object_or_404(Event, slug=slug, status='published')
    
    # Récupérer toutes les informations détaillées de l'événement avec optimisations
    days = event.days.all().prefetch_related(
        'activities__intervenants'
    ).order_by('date', 'day_number')
    
    # FAQ publique organisée par catégorie
    faqs = event.faqs.filter(is_public=True).order_by('category', 'order')
    
    # Organisateurs avec toutes les informations
    organizers = event.organizers.all().order_by('order')
    
    # Tags de l'événement
    tags = event.tags.all()
    
    # Événements similaires (même type ou catégorie)
    similar_events = Event.objects.filter(
        status='published'
    ).exclude(pk=event.pk).order_by('-start_date')[:3]
    
    # Vérifier si l'événement a un formulaire d'inscription
    has_registration_form = hasattr(event, 'registration_form') and event.registration_form.is_active
    
    # Récupérer le formulaire d'inscription si disponible
    registration_form = None
    if has_registration_form:
        registration_form = event.registration_form
    
    # Compter le nombre total d'intervenants
    total_intervenants = sum(
        day.activities.count() for day in days
    )
    
    # Compter le nombre total d'activités
    total_activities = sum(
        day.activities.count() for day in days
    )
    
    # Vérifier si l'événement est multi-jours
    is_multi_day = event.start_date != event.end_date
    
    # Calculer la durée en jours
    duration_days = (event.end_date - event.start_date).days + 1 if is_multi_day else 1
    
    context = {
        'event': event,
        'days': days,
        'faqs': faqs,
        'organizers': organizers,
        'tags': tags,
        'similar_events': similar_events,
        'has_registration_form': has_registration_form,
        'registration_form': registration_form,
        'page_title': event.title,
        'now': timezone.now(),
        'total_intervenants': total_intervenants,
        'total_activities': total_activities,
        'is_multi_day': is_multi_day,
        'duration_days': duration_days,
    }
    return render(request, 'sfront/event_detail.html', context)

def personnas(request):
    """Page Personnalités"""
    personnas_list = Personna.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(personnas_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Personnalités',
        'page_obj': page_obj,
        'personnas': page_obj,
    }
    return render(request, 'sfront/personnas.html', context)

def persona_detail(request, slug):
    """Détail d'une personnalité"""
    personna = get_object_or_404(Personna, slug=slug, is_active=True)
    
    # Blogs de cette personnalité
    blogs = Blog.objects.filter(
        personna=personna,
        status='published',
        is_active=True
    ).order_by('-published_at')
    
    context = {
        'personna': personna,
        'blogs': blogs,
        'page_title': personna.name,
    }
    return render(request, 'sfront/persona_detail.html', context)

def contact(request):
    """Page Contact"""
    context = {
        'page_title': 'Contact',
    }
    return render(request, 'sfront/contact.html', context)

def search(request):
    """Vue de recherche complète dans tous les contenus"""
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    results = {}
    total_results = 0
    
    if query:
        # Recherche dans les articles
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            status='published'
        )
        if category_filter and category_filter != 'all':
            articles = articles.filter(category__slug=category_filter)
        articles = articles[:15]
        results['articles'] = articles
        total_results += articles.count()
        
        # Recherche dans les programmes
        programs = Program.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(level__icontains=query),
            status='published'
        )[:15]
        results['programs'] = programs
        total_results += programs.count()
        
        # Recherche dans les événements
        events = Event.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(scientific_field__icontains=query) |
            Q(target_audience__icontains=query) |
            Q(location__icontains=query) |
            Q(city__icontains=query),
            status='published'
        )[:15]
        results['events'] = events
        total_results += events.count()
        
        # Recherche dans les blogs
        blogs = Blog.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query),
            status='published',
            is_active=True
        )[:15]
        results['blogs'] = blogs
        total_results += blogs.count()
        
        # Recherche dans les personnalités
        personnas = Personna.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )[:15]
        results['personnas'] = personnas
        total_results += personnas.count()
        
        # Recherche dans les membres de l'équipe
        team_members = TeamMember.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(job_title__icontains=query) |
            Q(biography__icontains=query),
            is_active=True
        )[:15]
        results['team_members'] = team_members
        total_results += team_members.count()
        
        # Recherche dans les partenaires
        partners = Partner.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )[:15]
        results['partners'] = partners
        total_results += partners.count()
        
        # Recherche dans les catégories
        categories = Category.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )[:10]
        results['categories'] = categories
        total_results += categories.count()
        
        # Recherche dans les valeurs fondamentales
        core_values = CoreValue.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )[:10]
        results['core_values'] = core_values
        total_results += core_values.count()
        
        # Recherche dans les quartiers de la cité
        city_districts = CityDistrict.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            is_active=True
        )[:10]
        results['city_districts'] = city_districts
        total_results += city_districts.count()
        
        # Recherche dans les statistiques héro
        hero_stats = HeroStatistic.objects.filter(
            Q(number__icontains=query) | 
            Q(label__icontains=query),
            is_active=True
        )[:10]
        results['hero_stats'] = hero_stats
        total_results += hero_stats.count()
        
        # Recherche dans les réalisations
        achievements = Achievement.objects.filter(
            Q(icon__icontains=query) | 
            Q(text__icontains=query),
            is_active=True
        )[:10]
        results['achievements'] = achievements
        total_results += achievements.count()
        
        results['query'] = query
        results['total_results'] = total_results
    
    # Récupérer toutes les catégories pour le filtre
    all_categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_title': 'Recherche',
        'results': results,
        'query': query,
        'all_categories': all_categories,
        'category_filter': category_filter,
    }
    return render(request, 'sfront/search.html', context)

def privacy(request):
    """Page Politique de confidentialité"""
    context = {
        'page_title': 'Politique de confidentialité',
    }
    return render(request, 'sfront/privacy.html', context)

def terms(request):
    """Page Conditions d'utilisation"""
    context = {
        'page_title': 'Conditions d\'utilisation',
    }
    return render(request, 'sfront/terms.html', context)

def legal(request):
    """Page Mentions légales"""
    context = {
        'page_title': 'Mentions légales',
    }
    return render(request, 'sfront/legal.html', context)

def sitemap(request):
    """Page Plan du site"""
    context = {
        'page_title': 'Plan du site',
    }
    return render(request, 'sfront/sitemap.html', context)

def accessibility(request):
    """Page Accessibilité"""
    context = {
        'page_title': 'Accessibilité',
    }
    return render(request, 'sfront/accessibility.html', context)


# ============================================================================
# VUES API POUR LES PERSONNALITÉS ET BLOGS
# ============================================================================

@require_http_methods(["GET"])
def personnas_api(request):
    """API pour récupérer toutes les personnalités actives"""
    try:
        personnas = Personna.objects.filter(is_active=True).order_by('-featured', '-created_at')
        
        data = []
        for personna in personnas:
            data.append({
                'id': personna.id,
                'name': personna.name,
                'slug': personna.slug,
                'description': personna.description,
                'featured': personna.featured,
                'blogs_count': personna.blogs_count,
                'created_at': personna.created_at.strftime('%d/%m/%Y') if personna.created_at else None,
            })
        
        return JsonResponse({
            'success': True,
            'personnas': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def persona_blogs_api(request, slug):
    """API pour récupérer les blogs d'une personnalité"""
    try:
        personna = get_object_or_404(Personna, slug=slug, is_active=True)
        blogs = Blog.objects.filter(
            personna=personna,
            status='published',
            is_active=True
        ).order_by('-published_at', '-created_at')
        
        data = []
        for blog in blogs:
            data.append({
                'id': blog.id,
                'title': blog.title,
                'slug': blog.slug,
                'excerpt': blog.excerpt,
                'published_at': blog.published_at.strftime('%d/%m/%Y') if blog.published_at else None,
                'reading_time': blog.reading_time,
                'views_count': blog.views_count,
            })
        
        return JsonResponse({
            'success': True,
            'personna': {
                'id': personna.id,
                'name': personna.name,
                'slug': personna.slug,
                'description': personna.description,
            },
            'blogs': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def blog_detail_api(request, slug):
    """API pour récupérer le détail d'un blog"""
    try:
        blog = get_object_or_404(Blog, slug=slug, status='published', is_active=True)
        
        data = {
            'id': blog.id,
            'title': blog.title,
            'slug': blog.slug,
            'content': blog.content,
            'excerpt': blog.excerpt,
            'published_at': blog.published_at.strftime('%d/%m/%Y') if blog.published_at else None,
            'reading_time': blog.reading_time,
            'views_count': blog.views_count,
            'personna': {
                'id': blog.personna.id,
                'name': blog.personna.name,
                'slug': blog.personna.slug,
            } if blog.personna else None,
        }
        
        return JsonResponse({
            'success': True,
            'blog': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """API pour s'inscrire à la newsletter"""
    try:
        import json
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        language = data.get('language', 'fr')
        
        # Validation de base
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'L\'adresse email est requise'
            }, status=400)
        
        # Vérifier si l'email est déjà inscrit
        existing_subscriber = Newsletter.objects.filter(email=email).first()
        if existing_subscriber:
            if existing_subscriber.is_active:
                return JsonResponse({
                    'success': False,
                    'error': 'Cette adresse email est déjà inscrite à la newsletter'
                }, status=400)
            else:
                # Réactiver l'abonnement
                existing_subscriber.is_active = True
                existing_subscriber.first_name = first_name
                existing_subscriber.last_name = last_name
                existing_subscriber.language = language
                existing_subscriber.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Votre abonnement à la newsletter a été réactivé avec succès !',
                    'subscriber': {
                        'email': existing_subscriber.email,
                        'first_name': existing_subscriber.first_name,
                        'last_name': existing_subscriber.last_name,
                        'language': existing_subscriber.language
                    }
                })
        
        # Créer un nouvel abonné
        subscriber = Newsletter.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            language=language,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Inscription à la newsletter réussie ! Vous recevrez bientôt nos actualités.',
            'subscriber': {
                'email': subscriber.email,
                'first_name': subscriber.first_name,
                'last_name': subscriber.last_name,
                'language': subscriber.language
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Une erreur est survenue lors de l\'inscription'
        }, status=500)


@require_http_methods(["POST"])
def newsletter_unsubscribe(request):
    """API pour se désinscrire de la newsletter"""
    try:
        import json
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'L\'adresse email est requise'
            }, status=400)
        
        # Trouver l'abonné
        subscriber = Newsletter.objects.filter(email=email).first()
        if not subscriber:
            return JsonResponse({
                'success': False,
                'error': 'Cette adresse email n\'est pas inscrite à la newsletter'
            }, status=400)
        
        # Désactiver l'abonnement
        subscriber.is_active = False
        subscriber.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Vous avez été désinscrit de la newsletter avec succès.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Une erreur est survenue lors de la désinscription'
        }, status=500)



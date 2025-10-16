from django.urls import path
from . import views

app_name = 'sfront'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    
    # Pages À propos
    path('a-propos/', views.about, name='about'),
    path('mission-vision/', views.mission, name='mission'),
    path('equipe/', views.team, name='team'),
    path('equipe/<slug:slug>/', views.team_member_detail, name='team_member_detail'),
    
    # Pages Programmes
    path('programmes/', views.programs, name='programs'),
    path('programmes/<slug:slug>/', views.program_detail, name='program_detail'),

    path('innovation/', views.innovation, name='innovation'),
    path('formation/', views.formation, name='formation'),
    
    # Pages Projets
    path('projets/', views.projects, name='projects'),
    path('projets/<slug:slug>/', views.project_detail, name='project_detail'),
    
    # Pages Actualités et Événements
    path('actualites/', views.news, name='news'),
    path('actualites/<slug:slug>/', views.article_detail, name='article_detail'),
    path('evenements/', views.events, name='events'),
    path('evenements/<slug:slug>/', views.event_detail, name='event_detail'),
    
    # Pages Personnalités
    path('personnalites/', views.personnas, name='personnas'),
    path('personnalites/<slug:slug>/', views.persona_detail, name='persona_detail'),
    
    # Pages de contact et autres
    path('contact/', views.contact, name='contact'),
    
    # Pages légales
    path('politique-confidentialite/', views.privacy, name='privacy'),
    path('conditions-utilisation/', views.terms, name='terms'),
    path('mentions-legales/', views.legal, name='legal'),
    path('plan-du-site/', views.sitemap, name='sitemap'),
    path('accessibilite/', views.accessibility, name='accessibility'),
    
    # Page de recherche
    path('recherche/', views.search, name='search'),
    
    # API pour les personnalités et blogs
    path('api/personnas/', views.personnas_api, name='personnas_api'),
    path('api/personnas/<slug:slug>/blogs/', views.persona_blogs_api, name='personna_blogs_api'),
    path('api/blogs/<slug:slug>/', views.blog_detail_api, name='blog_detail_api'),
    
    # API pour la newsletter
    path('api/newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('api/newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
]

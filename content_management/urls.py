from django.urls import path
from . import views

app_name = 'content_management'

urlpatterns = [
    # Tableau de bord
    path('', views.dashboard, name='dashboard'),
    
    # Gestion des catégories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Gestion des articles
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('articles/<int:pk>/status/', views.article_status_change, name='article_status_change'),
    path('articles/bulk-action/', views.bulk_article_action, name='bulk_article_action'),
    path('articles/toggle-feature/', views.toggle_feature, name='toggle_feature'),
    path('articles/delete/', views.delete_article, name='delete_article'),
    
    # Événements
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Gestion des composants d'événements
    path('events/<int:pk>/agenda/', views.event_manage_agenda, name='event_manage_agenda'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/edit/', views.event_day_edit, name='event_day_edit'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/delete/', views.event_day_delete, name='event_day_delete'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/activities/', views.event_day_activities, name='event_day_activities'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/activities/create/', views.event_activity_create, name='event_activity_create'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/activities/<int:activity_pk>/edit/', views.event_activity_edit, name='event_activity_edit'),
    path('events/<int:event_pk>/agenda/<int:day_pk>/activities/<int:activity_pk>/delete/', views.event_activity_delete, name='event_activity_delete'),
    path('events/<int:event_pk>/intervenants/', views.event_manage_intervenants, name='event_manage_intervenants'),
    path('events/<int:event_pk>/faq/', views.event_manage_faq, name='event_manage_faq'),
    path('events/<int:event_pk>/faq/create/', views.event_faq_create, name='event_faq_create'),
    path('events/<int:event_pk>/faq/<int:faq_pk>/edit/', views.event_faq_edit, name='event_faq_edit'),
    path('events/<int:event_pk>/faq/<int:faq_pk>/delete/', views.event_faq_delete, name='event_faq_delete'),
    path('events/<int:event_pk>/organizers/', views.event_manage_organizers, name='event_manage_organizers'),
    path('events/<int:event_pk>/organizers/<int:organizer_pk>/edit/', views.event_organizer_edit, name='event_organizer_edit'),
    path('events/<int:event_pk>/organizers/<int:organizer_pk>/delete/', views.event_organizer_delete, name='event_organizer_delete'),
    
    # Gestion des formulaires d'inscription
    path('events/<int:event_pk>/registration-form/', views.event_registration_form_manage, name='event_registration_form_manage'),
    path('events/<int:event_pk>/registration-form/edit/', views.event_registration_form_edit, name='event_registration_form_edit'),
                    path('events/<int:event_pk>/registration-form/fields/', views.event_registration_form_fields, name='event_registration_form_fields'),
                path('events/<int:event_pk>/registration-form/fields/<int:field_pk>/data/', views.event_registration_form_field_data, name='event_registration_form_field_data'),
                path('events/<int:event_pk>/registration-form/fields/<int:field_pk>/options/', views.event_registration_form_field_options, name='event_registration_form_field_options'),
    path('events/<int:event_pk>/registrations/', views.event_registrations_list, name='event_registrations_list'),
    path('events/<int:event_pk>/registrations/<int:registration_pk>/', views.event_registration_detail, name='event_registration_detail'),
    path('events/<int:event_pk>/registrations/<int:registration_pk>/status/', views.event_registration_status_change, name='event_registration_status_change'),
    path('events/<int:event_pk>/registrations/bulk-action/', views.event_registrations_bulk_action, name='event_registrations_bulk_action'),
    path('events/<int:event_pk>/registrations/export/', views.event_registrations_export, name='event_registrations_export'),
    
    # URLs publiques pour l'inscription (redirigées vers sfront)
    # path('events/<int:event_pk>/register/', views.event_registration_public, name='event_registration_public'),
    # path('events/<int:event_pk>/register/<int:registration_pk>/confirmation/', views.event_registration_confirmation, name='event_registration_confirmation'),
    
    # Tags d'événements
    path('event-tags/', views.event_tag_list, name='event_tag_list'),
    path('event-tags/create/', views.event_tag_create, name='event_tag_create'),
    path('event-tags/<int:pk>/edit/', views.event_tag_edit, name='event_tag_edit'),
    path('event-tags/<int:pk>/delete/', views.event_tag_delete, name='event_tag_delete'),
    
    # API AJAX pour événements
    path('api/event-toggle-status/', views.event_toggle_status, name='event_toggle_status'),
    path('api/event-toggle-feature/', views.event_toggle_feature, name='event_toggle_feature'),
    path('api/delete-event/', views.delete_event, name='delete_event'),
    path('api/bulk-event-action/', views.bulk_event_action, name='bulk_event_action'),
    
    # Gestion des intervenants
    path('intervenants/', views.event_intervenant_list, name='event_intervenant_list'),
    path('intervenants/create/', views.event_intervenant_create, name='event_intervenant_create'),
    path('intervenants/<int:pk>/edit/', views.event_intervenant_edit, name='event_intervenant_edit'),
    path('intervenants/<int:pk>/delete/', views.event_intervenant_delete, name='event_intervenant_delete'),
    
    # API pour la gestion des intervenants dans les activités
    path('api/activity-intervenants/<int:activity_id>/', views.api_activity_intervenants, name='api_activity_intervenants'),
    path('api/all-intervenants/', views.api_all_intervenants, name='api_all_intervenants'),
    path('api/activity-add-intervenants/<int:activity_id>/', views.api_activity_add_intervenants, name='api_activity_add_intervenants'),
    path('api/activity-remove-intervenant/<int:activity_id>/<int:intervenant_id>/', views.api_activity_remove_intervenant, name='api_activity_remove_intervenant'),
    path('api/intervenant-details/<int:intervenant_id>/', views.api_intervenant_details, name='api_intervenant_details'),
    
    # Gestion des projets
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/bulk-action/', views.bulk_project_action, name='bulk_project_action'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Gestion des partenaires de projet
    path('projects/<int:project_pk>/partners/add/', views.project_partner_add, name='project_partner_add'),
    path('projects/<int:project_pk>/partners/<int:partner_pk>/edit/', views.project_partner_edit, name='project_partner_edit'),
    path('projects/<int:project_pk>/partners/<int:partner_pk>/delete/', views.project_partner_delete, name='project_partner_delete'),
    
    # Gestion des programmes
    path('programs/', views.program_list, name='program_list'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:pk>/', views.program_detail, name='program_detail'),
    path('programs/<int:pk>/edit/', views.program_edit, name='program_edit'),
    path('programs/<int:pk>/delete/', views.program_delete, name='program_delete'),
    
    # Gestion des partenaires
    path('partners/', views.partner_list, name='partner_list'),
    path('partners/create/', views.partner_create, name='partner_create'),
    path('partners/<int:pk>/', views.partner_detail, name='partner_detail'),
    path('partners/<int:pk>/edit/', views.partner_edit, name='partner_edit'),
    path('partners/<int:pk>/delete/', views.partner_delete, name='partner_delete'),
    path('partners/<int:pk>/confirm-delete/', views.partner_confirm_delete, name='partner_confirm_delete'),
    path('partners/<int:pk>/toggle-status/', views.partner_toggle_status, name='partner_toggle_status'),
    path('partners/bulk-action/', views.bulk_partner_action, name='bulk_partner_action'),
    
    # Gestion des newsletters
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.newsletter_create, name='newsletter_create'),
    path('newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter_edit'),
    path('newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter_delete'),
    path('newsletters/<int:pk>/send/', views.newsletter_send, name='newsletter_send'),
    path('newsletters/bulk-action/', views.bulk_newsletter_action, name='bulk_newsletter_action'),
    path('newsletters/export/', views.newsletter_export, name='newsletter_export'),
    
    # Nouvelles fonctionnalités de gestion des newsletters
    path('newsletters/subscribers/', views.newsletter_subscribers_management, name='newsletter_subscribers_management'),
    path('newsletters/statistics/', views.newsletter_statistics, name='newsletter_statistics'),
    path('newsletters/settings/', views.newsletter_settings, name='newsletter_settings'),
    path('newsletters/notifications/', views.newsletter_notifications, name='newsletter_notifications'),

    # Messages de contact
    path('contact-messages/', views.contact_message_list, name='contact_message_list'),
    path('contact-messages/<int:pk>/', views.contact_message_detail, name='contact_message_detail'),
    path('contact-messages/<int:pk>/delete/', views.contact_message_delete, name='contact_message_delete'),
    path('contact-messages/bulk-action/', views.bulk_contact_message_action, name='bulk_contact_message_action'),
    
    # Paramètres du site
    path('site-settings/', views.site_settings, name='site_settings'),
    
                # Utilisateurs et rôles
            path('users/', views.user_list, name='user_list'),
            path('users/create/', views.user_create, name='user_create'),
            path('users/<int:pk>/', views.user_detail, name='user_detail'),
            path('roles/', views.role_list, name='role_list'),
            path('roles/create/', views.role_create, name='role_create'),
            path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
            path('roles/<int:pk>/', views.role_detail, name='role_detail'),
    
    # Newsletter
    path('newsletters/subscribers/', views.newsletter_subscribers_management, name='newsletter_subscribers_management'),
    path('newsletters/statistics/', views.newsletter_statistics, name='newsletter_statistics'),
    path('newsletters/settings/', views.newsletter_settings, name='newsletter_settings'),
    path('newsletters/notifications/', views.newsletter_notifications, name='newsletter_notifications'),

    # API AJAX
    path('api/delete-category/', views.delete_category_ajax, name='delete_category_ajax'),
    path('api/category-toggle-status/', views.category_toggle_status, name='category_toggle_status'),
    path('api/delete-image/', views.delete_image, name='delete_image'),
    path('api/reorder-images/', views.reorder_images, name='reorder_images'),

    # Équipe
    path('equipe/', views.team_member_list, name='team_member_list'),
    path('equipe/creer/', views.team_member_create, name='team_member_create'),
    path('equipe/<slug:slug>/', views.team_member_detail, name='team_member_detail'),
    path('equipe/<int:pk>/modifier/', views.team_member_edit, name='team_member_edit'),
    path('equipe/<slug:slug>/supprimer/', views.team_member_delete, name='team_member_delete'),
    path('equipe/<slug:slug>/toggle-status/', views.team_member_toggle_status, name='team_member_toggle_status'),
    path('equipe/bulk-action/', views.bulk_team_member_action, name='bulk_team_member_action'),

    # ===== SALLES DE CONFÉRENCE =====
    path('salles/', views.conference_room_list, name='conference_room_list'),
    path('salles/creer/', views.conference_room_create, name='conference_room_create'),
    path('salles/<slug:slug>/', views.conference_room_detail, name='conference_room_detail'),
    path('salles/<slug:slug>/modifier/', views.conference_room_edit, name='conference_room_edit'),
    path('salles/<slug:slug>/supprimer/', views.conference_room_delete, name='conference_room_delete'),
    
    # ===== ORGANISATIONS EXTERNES =====
    path('organisations/', views.external_organization_list, name='external_organization_list'),
    path('organisations/creer/', views.external_organization_create, name='external_organization_create'),
    path('organisations/<slug:slug>/', views.external_organization_detail, name='external_organization_detail'),
    path('organisations/<slug:slug>/modifier/', views.external_organization_edit, name='external_organization_edit'),
    path('organisations/<slug:slug>/supprimer/', views.external_organization_delete, name='external_organization_delete'),
    
    # ===== RÉSERVATIONS DE SALLE =====
    path('reservations/', views.room_booking_list, name='room_booking_list'),
    path('reservations/creer/', views.room_booking_create, name='room_booking_create'),
    path('reservations/<int:pk>/', views.room_booking_detail, name='room_booking_detail'),
    path('reservations/<int:pk>/modifier/', views.room_booking_edit, name='room_booking_edit'),
    path('reservations/<int:pk>/supprimer/', views.room_booking_delete, name='room_booking_delete'),
    path('reservations/<int:pk>/toggle-status/', views.room_booking_toggle_status, name='room_booking_toggle_status'),
    path('reservations/calendrier/', views.room_booking_calendar, name='room_booking_calendar'),
    path('reservations/verifier-conflits/', views.check_booking_conflicts, name='check_booking_conflicts'),
    
    # ===== MAINTENANCE DES SALLES =====
    path('maintenance/', views.room_maintenance_list, name='room_maintenance_list'),
    path('maintenance/creer/', views.room_maintenance_create, name='room_maintenance_create'),
    path('maintenance/<int:pk>/', views.room_maintenance_detail, name='room_maintenance_detail'),
    path('maintenance/<int:pk>/modifier/', views.room_maintenance_edit, name='room_maintenance_edit'),
    path('maintenance/<int:pk>/supprimer/', views.room_maintenance_delete, name='room_maintenance_delete'),
    
    # ===== TABLEAU DE BORD DES SALLES =====
    path('dashboard-salles/', views.dashboard_rooms, name='dashboard_rooms'),

    # ============================================================================
    # GESTION DES PERSONNAS
    # ============================================================================
    path('personnas/', views.personna_list, name='personna_list'),
    path('personnas/creer/', views.personna_create, name='personna_create'),
    path('personnas/<slug:slug>/', views.personna_detail, name='personna_detail'),
    path('personnas/<slug:slug>/modifier/', views.personna_edit, name='personna_edit'),
    path('personnas/<slug:slug>/supprimer/', views.personna_delete, name='personna_delete'),
    path('personnas/<slug:slug>/toggle-status/', views.personna_toggle_status, name='personna_toggle_status'),
    path('personnas/<slug:slug>/toggle-featured/', views.personna_toggle_featured, name='personna_toggle_featured'),
    
    # ============================================================================
    # GESTION DES BLOGS
    # ============================================================================
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/creer/', views.blog_create, name='blog_create'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blogs/<slug:slug>/modifier/', views.blog_edit, name='blog_edit'),
    path('blogs/<slug:slug>/supprimer/', views.blog_delete, name='blog_delete'),
    path('blogs/<slug:slug>/toggle-status/', views.blog_toggle_status, name='blog_toggle_status'),
    path('blogs/<slug:slug>/toggle-active/', views.blog_toggle_active, name='blog_toggle_active'),
    path('blogs/<slug:slug>/toggle-featured/', views.blog_toggle_featured, name='blog_toggle_featured'),
    
    # ============================================================================
    # TEST CKEDITOR5
    # ============================================================================
    path('test-ckeditor/', views.test_ckeditor, name='test_ckeditor'),

    # Page À propos
    path('about-page/', views.about_page_edit, name='about_page_edit'),
    path('about-page/preview/', views.about_page_preview, name='about_page_preview'),
    
    # Statistiques hero
    path('hero-statistics/', views.hero_statistic_list, name='hero_statistic_list'),
    path('hero-statistics/create/', views.hero_statistic_create, name='hero_statistic_create'),
    path('hero-statistics/<int:pk>/edit/', views.hero_statistic_edit, name='hero_statistic_edit'),
    
    # Réalisations
    path('achievements/', views.achievement_list, name='achievement_list'),
    path('achievements/create/', views.achievement_create, name='achievement_create'),
    path('achievements/<int:pk>/edit/', views.achievement_edit, name='achievement_edit'),
    
    # Quartiers de la cité
    path('city-districts/', views.city_district_list, name='city_district_list'),
    path('city-districts/create/', views.city_district_create, name='city_district_create'),
    path('city-districts/<int:pk>/edit/', views.city_district_edit, name='city_district_edit'),
    
    # Valeurs fondamentales
    path('core-values/', views.core_value_list, name='core_value_list'),
    path('core-values/create/', views.core_value_create, name='core_value_create'),
    path('core-values/<int:pk>/edit/', views.core_value_edit, name='core_value_edit'),
    
    # ============================================================================
    # GESTION DES CAMPAGNES DE NEWSLETTER
    # ============================================================================
    path('newsletter-campaigns/', views.newsletter_campaign_list, name='newsletter_campaign_list'),
    path('newsletter-campaigns/creer/', views.newsletter_campaign_create, name='newsletter_campaign_create'),
    path('newsletter-campaigns/<int:pk>/', views.newsletter_campaign_detail, name='newsletter_campaign_detail'),
    path('newsletter-campaigns/<int:pk>/modifier/', views.newsletter_campaign_edit, name='newsletter_campaign_edit'),
    path('newsletter-campaigns/<int:pk>/edit/', views.newsletter_campaign_edit, name='newsletter_campaign_edit'),
    path('newsletter-campaigns/<int:pk>/supprimer/', views.newsletter_campaign_delete, name='newsletter_campaign_delete'),
    path('newsletter-campaigns/<int:pk>/envoyer/', views.newsletter_campaign_send, name='newsletter_campaign_send'),
    path('newsletter-campaigns/<int:pk>/programmer/', views.newsletter_campaign_schedule, name='newsletter_campaign_schedule'),
    path('newsletter-campaigns/<int:pk>/dupliquer/', views.newsletter_campaign_duplicate, name='newsletter_campaign_duplicate'),
    path('newsletter-campaigns/bulk-action/', views.bulk_newsletter_campaign_action, name='bulk_newsletter_campaign_action'),
    path('newsletter-campaigns/export/', views.export_newsletter_campaigns, name='export_newsletter_campaigns'),
    
    # ============================================================================
    # GESTION DES ABONNÉS NEWSLETTER
    # ============================================================================
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/creer/', views.newsletter_create, name='newsletter_create'),
    path('newsletters/<int:pk>/', views.newsletter_detail, name='newsletter_detail'),
    path('newsletters/<int:pk>/modifier/', views.newsletter_edit, name='newsletter_edit'),
    path('newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter_edit'),
    path('newsletters/<int:pk>/supprimer/', views.newsletter_delete, name='newsletter_delete'),
    
    # Gestion des abonnés
    path('newsletter/abonnes/', views.newsletter_subscribers_management, name='newsletter_subscribers_management'),
    path('newsletter/statistiques/', views.newsletter_statistics, name='newsletter_statistics'),
    path('newsletter/parametres/', views.newsletter_settings, name='newsletter_settings'),
    path('newsletter/notifications/', views.newsletter_notifications, name='newsletter_notifications'),
]

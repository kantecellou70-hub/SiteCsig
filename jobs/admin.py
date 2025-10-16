from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from content_management.models import NewsletterCampaign
from .tasks import send_bulk_newsletter, test_email_connection

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'target_language', 'scheduled_at', 
        'sent_count', 'failed_count', 'created_by', 'created_at'
    ]
    list_filter = [
        'status', 'target_language', 'target_active_only', 
        'created_at', 'scheduled_at'
    ]
    search_fields = ['title', 'subject', 'content']
    readonly_fields = [
        'sent_count', 'failed_count', 'opened_count', 'clicked_count',
        'created_at', 'started_at', 'completed_at', 'created_by'
    ]
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'subject', 'content', 'template_name')
        }),
        ('Configuration', {
            'fields': ('status', 'target_language', 'target_active_only', 'scheduled_at')
        }),
        ('Statistiques', {
            'fields': ('sent_count', 'failed_count', 'opened_count', 'clicked_count'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'started_at', 'completed_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nouvelle campagne
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['sending', 'completed', 'failed']:
            return self.readonly_fields + ('status', 'scheduled_at')
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in ['sending', 'completed']:
            return False
        return super().has_delete_permission(request, obj)
    
    actions = ['send_campaign', 'test_email_connection']
    
    def send_campaign(self, request, queryset):
        """Action pour envoyer une campagne"""
        for campaign in queryset:
            if campaign.can_be_sent:
                send_bulk_newsletter.delay(campaign.id)
                self.message_user(
                    request, 
                    f"Campagne '{campaign.title}' mise en file d'attente pour envoi."
                )
            else:
                self.message_user(
                    request, 
                    f"Campagne '{campaign.title}' ne peut pas être envoyée (statut: {campaign.get_status_display()}).",
                    level='WARNING'
                )
    
    send_campaign.short_description = "Envoyer les campagnes sélectionnées"
    
    def test_email_connection(self, request, queryset):
        """Action pour tester la connexion email"""
        result = test_email_connection.delay()
        self.message_user(
            request, 
            f"Test de connexion email lancé. ID de tâche: {result.id}"
        )
    
    test_email_connection.short_description = "Tester la connexion email"

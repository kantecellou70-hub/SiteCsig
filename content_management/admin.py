from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Article, ArticleImage, Event, Project, Program, 
    Partner, Newsletter, ContactMessage, SiteSettings, TeamMember
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    
    def color_display(self, obj):
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = _("Couleur")


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'views_count', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'excerpt']
    list_editable = ['status', 'is_featured']
    date_hierarchy = 'created_at'
    inlines = [ArticleImageInline]
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('title', 'category', 'author', 'status')
        }),
        (_('Contenu'), {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        (_('Médias'), {
            'fields': ('video_url', 'audio_file'),
            'classes': ('collapse',)
        }),
        (_('Options'), {
            'fields': ('is_featured', 'published_at', 'meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'published' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'location', 'status', 'is_featured']
    list_filter = ['status', 'is_featured', 'start_date', 'end_date', 'registration_required']
    search_fields = ['title', 'description', 'location']
    list_editable = ['status', 'is_featured']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('title', 'status', 'is_featured')
        }),
        (_('Détails'), {
            'fields': ('description', 'featured_image')
        }),
        (_('Date et lieu'), {
            'fields': ('start_date', 'end_date', 'location')
        }),
        (_('Contact'), {
            'fields': ('contact_email', 'contact_phone')
        }),
        (_('Inscription'), {
            'fields': ('registration_required', 'max_participants'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_date', 'end_date', 'is_featured']
    list_filter = ['status', 'is_featured', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'objectives']
    list_editable = ['status', 'is_featured']
    date_hierarchy = 'start_date'
    filter_horizontal = ['team_members']
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('title', 'status', 'is_featured')
        }),
        (_('Description'), {
            'fields': ('short_description', 'description', 'featured_image')
        }),
        (_('Dates'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Détails'), {
            'fields': ('budget', 'team_members', 'partners')
        }),
        (_('Contenu'), {
            'fields': ('objectives', 'results'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'duration', 'status', 'is_featured', 'is_free']
    list_filter = ['status', 'level', 'is_featured', 'is_free', 'start_date']
    search_fields = ['title', 'description']
    list_editable = ['status', 'is_featured', 'is_free']
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('title', 'status', 'is_featured')
        }),
        (_('Description'), {
            'fields': ('short_description', 'description', 'featured_image')
        }),
        (_('Détails'), {
            'fields': ('duration', 'level', 'max_students')
        }),
        (_('Prix et dates'), {
            'fields': ('is_free', 'price', 'start_date', 'end_date')
        }),
    )


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partnership_type', 'is_active', 'order', 'logo_display']
    list_filter = ['partnership_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    
    def logo_display(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.logo.url)
        return _("Aucun logo")
    logo_display.short_description = _("Logo")


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'language', 'is_active', 'subscription_date']
    list_filter = ['is_active', 'language', 'subscription_date']
    search_fields = ['email', 'first_name', 'last_name']
    list_editable = ['is_active']
    readonly_fields = ['subscription_date']
    
    actions = ['export_emails']
    
    def export_emails(self, request, queryset):
        emails = queryset.filter(is_active=True).values_list('email', flat=True)
        response = HttpResponse('\n'.join(emails), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="newsletter_emails.txt"'
        return response
    export_emails.short_description = _("Exporter les emails")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        (_('Message'), {
            'fields': ('message',)
        }),
        (_('Statut'), {
            'fields': ('is_read', 'created_at', 'updated_at')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Permettre seulement un objet de paramètres
        return not SiteSettings.objects.exists()
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('site_name', 'tagline')
        }),
        (_('Contact'), {
            'fields': ('address', 'phone', 'email')
        }),
        (_('Réseaux sociaux'), {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        (_('Contenu de la page d\'accueil'), {
            'fields': ('about_text', 'hero_title', 'hero_subtitle'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job_title', 'email', 'category', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'job_title', 'biography', 'slug']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'last_name', 'first_name']
    prepopulated_fields = {'slug': ('last_name', 'first_name')}
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'job_title', 'category')
        }),
        ('Biographie', {
            'fields': ('biography',)
        }),
        ('Réseaux sociaux', {
            'fields': ('linkedin', 'twitter', 'youtube', 'facebook'),
            'classes': ('collapse',)
        }),
        ('Photo et paramètres', {
            'fields': ('photo', 'slug', 'is_active', 'order')
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nom complet'
    full_name.admin_order_field = 'last_name'

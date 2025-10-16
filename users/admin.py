from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Administration des rôles utilisateur"""
    list_display = ['name', 'description', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    filter_horizontal = ['permissions']
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Permissions'), {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'readonly_fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


class UserProfileInline(admin.StackedInline):
    """Profil utilisateur en ligne"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profil')
    fields = ['avatar', 'bio', 'website']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration des utilisateurs"""
    inlines = [UserProfileInline]
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'job_title', 
        'department', 'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 
        'language', 'date_joined', 'roles'
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'job_title', 'department']
    ordering = ['-date_joined']
    filter_horizontal = ['groups', 'user_permissions', 'roles']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Informations professionnelles'), {
            'fields': ('job_title', 'department')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'is_verified',
                'groups', 'user_permissions', 'roles'
            ),
        }),
        (_('Préférences'), {
            'fields': ('language',)
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related et prefetch_related"""
        return super().get_queryset(request).select_related('profile').prefetch_related('roles')
    
    def get_list_display(self, request):
        """Personnaliser l'affichage selon les permissions"""
        list_display = list(super().get_list_display(request))
        
        if not request.user.is_superuser:
            # Masquer certains champs pour les non-superusers
            if 'is_superuser' in list_display:
                list_display.remove('is_superuser')
            if 'user_permissions' in list_display:
                list_display.remove('user_permissions')
        
        return list_display
    
    def get_fieldsets(self, request, obj=None):
        """Personnaliser les champs selon les permissions"""
        fieldsets = list(super().get_fieldsets(request, obj))
        
        if not request.user.is_superuser:
            # Masquer certains champs pour les non-superusers
            for fieldset in fieldsets:
                if fieldset[0] == _('Permissions'):
                    fields = list(fieldset[1]['fields'])
                    if 'is_superuser' in fields:
                        fields.remove('is_superuser')
                    if 'user_permissions' in fields:
                        fields.remove('user_permissions')
                    fieldset[1]['fields'] = tuple(fields)
        
        return fieldsets


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administration des profils utilisateur"""
    list_display = ['user', 'bio_preview', 'website']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    ordering = ['user__username']
    
    fieldsets = (
        (_('Utilisateur'), {
            'fields': ('user',)
        }),
        (_('Informations personnelles'), {
            'fields': ('avatar', 'bio', 'website')
        }),
    )
    
    def bio_preview(self, obj):
        """Aperçu de la biographie"""
        if obj.bio:
            return obj.bio[:100] + '...' if len(obj.bio) > 100 else obj.bio
        return _('Aucune biographie')
    bio_preview.short_description = _('Aperçu de la biographie')
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related('user')


# Personnalisation de l'interface d'administration
admin.site.site_header = _('Administration CSIG')
admin.site.site_title = _('Site d\'administration CSIG')
admin.site.index_title = _('Gestion de la Cité des Sciences et de l\'Innovation de Guinée')

# Personnaliser l'ordre des applications
admin.site.index_template = 'admin/custom_index.html'

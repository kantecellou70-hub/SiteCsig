from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.urls import reverse
import uuid


class UserRole(models.Model):
    """Modèle pour définir les rôles des utilisateurs"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire de contenu'),
        ('editor', 'Éditeur'),
        ('author', 'Auteur'),
        ('viewer', 'Lecteur'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name=_('Nom du rôle'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name=_('Permissions'))
    is_active = models.BooleanField(default=True, verbose_name=_('Actif'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Créé le'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Modifié le'))
    
    class Meta:
        verbose_name = _('Rôle utilisateur')
        verbose_name_plural = _('Rôles utilisateur')
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Modèle utilisateur étendu pour CSIG"""
    email = models.EmailField(unique=True, verbose_name=_('Adresse email'))
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés.")
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name=_('Téléphone'))
    
    # Informations professionnelles
    job_title = models.CharField(max_length=100, blank=True, verbose_name=_('Poste'))
    department = models.CharField(max_length=100, blank=True, verbose_name=_('Département'))
    
    # Paramètres du compte
    is_verified = models.BooleanField(default=False, verbose_name=_('Compte vérifié'))
    language = models.CharField(
        max_length=10,
        choices=[('fr', 'Français'), ('en', 'English')],
        default='fr',
        verbose_name=_('Langue préférée')
    )
    
    # Rôles et permissions
    roles = models.ManyToManyField(UserRole, blank=True, verbose_name=_('Rôles'))
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def has_role(self, role_name):
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return self.roles.filter(name=role_name).exists()
    
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.is_superuser or self.has_role('admin')


class UserProfile(models.Model):
    """Profil étendu de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('Utilisateur'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    bio = models.TextField(blank=True, verbose_name=_('Biographie'))
    website = models.URLField(blank=True, verbose_name=_('Site web'))
    
    class Meta:
        verbose_name = _('Profil utilisateur')
        verbose_name_plural = _('Profils utilisateur')
    
    def __str__(self):
        return f"Profil de {self.user.get_display_name()}"

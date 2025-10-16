from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, UserRole

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil utilisateur lors de la création d'un utilisateur"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil utilisateur lors de la sauvegarde de l'utilisateur"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserRole)
def create_default_roles(sender, instance, created, **kwargs):
    """Créer des rôles par défaut si aucun n'existe"""
    if created and UserRole.objects.count() == 1:
        # Créer des rôles par défaut
        default_roles = [
            {
                'name': 'admin',
                'description': 'Administrateur avec tous les droits'
            },
            {
                'name': 'manager',
                'description': 'Gestionnaire de contenu avec droits étendus'
            },
            {
                'name': 'editor',
                'description': 'Éditeur de contenu'
            },
            {
                'name': 'author',
                'description': 'Auteur de contenu'
            },
            {
                'name': 'viewer',
                'description': 'Lecteur avec accès en lecture seule'
            }
        ]
        
        for role_data in default_roles:
            if not UserRole.objects.filter(name=role_data['name']).exists():
                UserRole.objects.create(**role_data)


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    """Supprimer le profil utilisateur lors de la suppression de l'utilisateur"""
    try:
        instance.profile.delete()
    except UserProfile.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """Attribuer un rôle par défaut aux nouveaux utilisateurs"""
    if created and not instance.is_superuser:
        # Attribuer le rôle 'viewer' par défaut
        try:
            viewer_role = UserRole.objects.get(name='viewer')
            instance.roles.add(viewer_role)
        except UserRole.DoesNotExist:
            pass

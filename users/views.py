from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from .models import User, UserProfile, UserRole
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, UserProfileForm,
    UserRoleForm, UserSearchForm, BulkUserActionForm, UserInvitationForm
)
import json

User = get_user_model()


@login_required
@permission_required('auth.view_user')
def user_list(request):
    """Liste des utilisateurs avec filtres et recherche"""
    # Formulaire de recherche
    search_form = UserSearchForm(request.GET)
    
    # Récupérer tous les utilisateurs
    users = User.objects.select_related('profile').prefetch_related('roles', 'groups')
    
    # Appliquer les filtres
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        role = search_form.cleaned_data.get('role')
        department = search_form.cleaned_data.get('department')
        is_active = search_form.cleaned_data.get('is_active')
        date_from = search_form.cleaned_data.get('date_joined_from')
        date_to = search_form.cleaned_data.get('date_joined_to')
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(job_title__icontains=search) |
                Q(department__icontains=search)
            )
        
        if role:
            users = users.filter(roles=role)
        
        if department:
            users = users.filter(department__icontains=department)
        
        if is_active != '':
            users = users.filter(is_active=bool(int(is_active)))
        
        if date_from:
            users = users.filter(date_joined__gte=date_from)
        
        if date_to:
            users = users.filter(date_joined__lte=date_to)
    
    # Tri par défaut
    users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    
    # Rôles disponibles
    roles = UserRole.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'roles': roles,
        'bulk_action_form': BulkUserActionForm(),
    }
    
    return render(request, 'users/user_list.html', context)


@login_required
@permission_required('auth.add_user')
def user_create(request):
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                _('L\'utilisateur "%(username)s" a été créé avec succès.') % {'username': user.username}
            )
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': _('Créer un nouvel utilisateur'),
        'submit_text': _('Créer l\'utilisateur'),
    }
    
    return render(request, 'users/user_form.html', context)


@login_required
@permission_required('auth.change_user')
def user_edit(request, pk):
    """Modifier un utilisateur existant"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                _('L\'utilisateur "%(username)s" a été modifié avec succès.') % {'username': user.username}
            )
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = CustomUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': _('Modifier l\'utilisateur %(username)s') % {'username': user.username},
        'submit_text': _('Enregistrer les modifications'),
    }
    
    return render(request, 'users/user_form.html', context)


@login_required
@permission_required('auth.view_user')
def user_detail(request, pk):
    """Détails d'un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    
    # Statistiques de l'utilisateur
    user_stats = {
        'last_login': user.last_login,
        'date_joined': user.date_joined,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'is_verified': user.is_verified,
    }
    
    # Rôles de l'utilisateur
    user_roles = user.roles.all()
    
    # Groupes de l'utilisateur
    user_groups = user.groups.all()
    
    # Permissions de l'utilisateur
    user_permissions = user.user_permissions.all()
    
    context = {
        'user': user,
        'user_stats': user_stats,
        'user_roles': user_roles,
        'user_groups': user_groups,
        'user_permissions': user_permissions,
    }
    
    return render(request, 'users/user_detail.html', context)


@login_required
@permission_required('auth.delete_user')
def user_delete(request, pk):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(
            request, 
            _('L\'utilisateur "%(username)s" a été supprimé avec succès.') % {'username': username}
        )
        return redirect('users:user_list')
    
    context = {
        'user': user,
        'title': _('Supprimer l\'utilisateur %(username)s') % {'username': user.username},
    }
    
    return render(request, 'users/user_confirm_delete.html', context)


@login_required
@permission_required('auth.change_user')
def user_profile_edit(request, pk):
    """Modifier le profil d'un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                _('Le profil de "%(username)s" a été modifié avec succès.') % {'username': user.username}
            )
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile,
        'title': _('Modifier le profil de %(username)s') % {'username': user.username},
        'submit_text': _('Enregistrer le profil'),
    }
    
    return render(request, 'users/user_profile_form.html', context)


@login_required
@permission_required('auth.view_user')
def role_list(request):
    """Liste des rôles utilisateur"""
    roles = UserRole.objects.all().prefetch_related('permissions')
    
    # Statistiques
    total_roles = roles.count()
    active_roles = roles.filter(is_active=True).count()
    
    context = {
        'roles': roles,
        'total_roles': total_roles,
        'active_roles': active_roles,
    }
    
    return render(request, 'users/role_list.html', context)


@login_required
@permission_required('auth.add_user')
def role_create(request):
    """Créer un nouveau rôle"""
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(
                request, 
                _('Le rôle "%(name)s" a été créé avec succès.') % {'name': role.get_name_display()}
            )
            return redirect('users:role_list')
    else:
        form = UserRoleForm()
    
    context = {
        'form': form,
        'title': _('Créer un nouveau rôle'),
        'submit_text': _('Créer le rôle'),
    }
    
    return render(request, 'users/role_form.html', context)


@login_required
@permission_required('auth.change_user')
def role_edit(request, pk):
    """Modifier un rôle existant"""
    role = get_object_or_404(UserRole, pk=pk)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                _('Le rôle "%(name)s" a été modifié avec succès.') % {'name': role.get_name_display()}
            )
            return redirect('users:role_list')
    else:
        form = UserRoleForm(instance=role)
    
    context = {
        'form': form,
        'role': role,
        'title': _('Modifier le rôle %(name)s') % {'name': role.get_name_display()},
        'submit_text': _('Enregistrer les modifications'),
    }
    
    return render(request, 'users/role_form.html', context)


@login_required
@permission_required('auth.delete_user')
def role_delete(request, pk):
    """Supprimer un rôle"""
    role = get_object_or_404(UserRole, pk=pk)
    
    if request.method == 'POST':
        name = role.get_name_display()
        role.delete()
        messages.success(
            request, 
            _('Le rôle "%(name)s" a été supprimé avec succès.') % {'name': name}
        )
        return redirect('users:role_list')
    
    context = {
        'role': role,
        'title': _('Supprimer le rôle %(name)s') % {'name': role.get_name_display()},
    }
    
    return render(request, 'users/role_confirm_delete.html', context)


@login_required
@permission_required('auth.change_user')
def user_toggle_status(request, pk):
    """Activer/désactiver un utilisateur"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        
        status = _('activé') if user.is_active else _('désactivé')
        messages.success(
            request, 
            _('L\'utilisateur "%(username)s" a été %(status)s.') % {
                'username': user.username, 'status': status
            }
        )
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': _('Statut mis à jour avec succès.')
        })
    
    return JsonResponse({'success': False, 'message': _('Méthode non autorisée.')})


@login_required
@permission_required('auth.change_user')
def bulk_user_action(request):
    """Actions en lot sur les utilisateurs"""
    if request.method == 'POST':
        form = BulkUserActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            role = form.cleaned_data.get('role')
            user_ids = form.cleaned_data.get('user_ids', '').split(',')
            
            users = User.objects.filter(pk__in=user_ids)
            count = 0
            
            if action == 'activate':
                users.update(is_active=True)
                count = users.count()
                messages.success(request, _('%(count)d utilisateur(s) activé(s) avec succès.') % {'count': count})
            
            elif action == 'deactivate':
                users.update(is_active=False)
                count = users.count()
                messages.success(request, _('%(count)d utilisateur(s) désactivé(s) avec succès.') % {'count': count})
            
            elif action == 'delete':
                count = users.count()
                users.delete()
                messages.success(request, _('%(count)d utilisateur(s) supprimé(s) avec succès.') % {'count': count})
            
            elif action == 'add_role' and role:
                for user in users:
                    user.roles.add(role)
                count = users.count()
                messages.success(
                    request, 
                    _('Le rôle "%(role)s" a été ajouté à %(count)d utilisateur(s).') % {
                        'role': role.get_name_display(), 'count': count
                    }
                )
            
            elif action == 'remove_role' and role:
                for user in users:
                    user.roles.remove(role)
                count = users.count()
                messages.success(
                    request, 
                    _('Le rôle "%(role)s" a été retiré de %(count)d utilisateur(s).') % {
                        'role': role.get_name_display(), 'count': count
                    }
                )
            
            return JsonResponse({
                'success': True,
                'count': count,
                'message': _('Action effectuée avec succès.')
            })
    
    return JsonResponse({'success': False, 'message': _('Formulaire invalide.')})


@login_required
@permission_required('auth.add_user')
def user_invitation(request):
    """Inviter un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserInvitationForm(request.POST)
        if form.is_valid():
            # Ici, vous pouvez implémenter la logique d'envoi d'invitation
            # Pour l'instant, on affiche juste un message de succès
            email = form.cleaned_data['email']
            messages.success(
                request, 
                _('Une invitation a été envoyée à %(email)s.') % {'email': email}
            )
            return redirect('users:user_list')
    else:
        form = UserInvitationForm()
    
    context = {
        'form': form,
        'title': _('Inviter un nouvel utilisateur'),
        'submit_text': _('Envoyer l\'invitation'),
    }
    
    return render(request, 'users/user_invitation.html', context)


@login_required
@permission_required('auth.view_user')
def user_dashboard(request):
    """Tableau de bord des utilisateurs"""
    # Statistiques générales
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    verified_users = User.objects.filter(is_verified=True).count()
    
    # Utilisateurs récents
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Utilisateurs par rôle
    users_by_role = UserRole.objects.annotate(
        user_count=Count('user')
    ).order_by('-user_count')
    
    # Utilisateurs par département
    users_by_department = User.objects.exclude(
        department__isnull=True
    ).exclude(
        department__exact=''
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Activité récente (connexions)
    recent_logins = User.objects.exclude(
        last_login__isnull=True
    ).order_by('-last_login')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'verified_users': verified_users,
        'recent_users': recent_users,
        'users_by_role': users_by_role,
        'users_by_department': users_by_department,
        'recent_logins': recent_logins,
    }
    
    return render(request, 'users/user_dashboard.html', context)


# API endpoints pour AJAX
@login_required
@permission_required('auth.view_user')
def user_search_api(request):
    """API de recherche d'utilisateurs pour AJAX"""
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 10))
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:limit]
    
    user_data = []
    for user in users:
        user_data.append({
            'id': user.pk,
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'is_active': user.is_active,
            'avatar_url': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else None,
        })
    
    return JsonResponse({'users': user_data})


@login_required
@permission_required('auth.change_user')
def user_quick_edit(request, pk):
    """Édition rapide d'un utilisateur via AJAX"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        data = json.loads(request.body)
        
        # Mettre à jour les champs autorisés
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'job_title' in data:
            user.job_title = data['job_title']
        if 'department' in data:
            user.department = data['department']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        try:
            user.save()
            return JsonResponse({
                'success': True,
                'message': _('Utilisateur mis à jour avec succès.'),
                'user': {
                    'id': user.pk,
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'email': user.email,
                    'is_active': user.is_active,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': _('Méthode non autorisée.')})


@login_required
def user_profile_api(request):
    """API pour récupérer les informations du profil utilisateur connecté"""
    user = request.user
    try:
        profile = getattr(user, 'profile', None)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.pk,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'phone': user.phone,
                'job_title': user.job_title,
                'department': user.department,
                'profile': {
                    'avatar': profile.avatar.url if profile and profile.avatar else None,
                    'bio': profile.bio if profile else None,
                    'website': profile.website if profile else None,
                } if profile else None,
                'roles': [role.name for role in user.roles.all()] if hasattr(user, 'roles') else [],
                'groups': [group.name for group in user.groups.all()],
                'permissions': list(user.get_all_permissions()),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
@permission_required('auth.change_user')
def user_toggle_status(request, pk):
    """Activer/désactiver un utilisateur via AJAX"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        
        try:
            user.save()
            return JsonResponse({
                'success': True,
                'message': _('Statut de l\'utilisateur mis à jour avec succès.'),
                'is_active': user.is_active
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': _('Méthode non autorisée.')})

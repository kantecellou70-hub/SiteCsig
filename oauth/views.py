from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
import json


def login_view(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('content_management:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name() or user.username}!')
                
                # Rediriger vers la page demandée ou le tableau de bord
                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('content_management:dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'oauth/login.html', {
        'form': form,
        'page_title': 'Connexion - CSIG'
    })


def register_view(request):
    """Page d'inscription"""
    if request.user.is_authenticated:
        return redirect('content_management:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connecter automatiquement l'utilisateur
            login(request, user)
            messages.success(request, 'Compte créé avec succès! Bienvenue!')
            return redirect('content_management:dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = UserCreationForm()
    
    return render(request, 'oauth/register.html', {
        'form': form,
        'page_title': 'Inscription - CSIG'
    })


@login_required
def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('oauth:login')


def password_reset_view(request):
    """Réinitialisation du mot de passe"""
    if request.user.is_authenticated:
        return redirect('content_management:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Ici, vous pouvez implémenter l'envoi d'email de réinitialisation
            messages.success(request, 'Un email de réinitialisation a été envoyé à votre adresse email.')
            return redirect('oauth:login')
        except User.DoesNotExist:
            messages.error(request, 'Aucun utilisateur trouvé avec cette adresse email.')
    
    return render(request, 'oauth/password_reset.html', {
        'page_title': 'Réinitialisation du mot de passe - CSIG'
    })


@login_required
def profile_view(request):
    """Profil de l'utilisateur"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Vérifier si le mot de passe actuel est correct
        current_password = request.POST.get('current_password')
        if current_password and not user.check_password(current_password):
            messages.error(request, 'Mot de passe actuel incorrect.')
            return render(request, 'oauth/profile.html', {
                'page_title': 'Profil - CSIG'
            })
        
        # Changer le mot de passe si fourni
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            messages.success(request, 'Mot de passe modifié avec succès.')
        
        user.save()
        messages.success(request, 'Profil mis à jour avec succès.')
        
        # Reconnecter l'utilisateur si le mot de passe a changé
        if new_password:
            user = authenticate(username=user.username, password=new_password)
            if user:
                login(request, user)
    
    return render(request, 'oauth/profile.html', {
        'page_title': 'Profil - CSIG'
    })


@csrf_exempt
def ajax_login(request):
    """Connexion via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Nom d\'utilisateur et mot de passe requis.'
                })
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Connexion réussie!',
                    'redirect_url': request.GET.get('next', '/content-management/')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Nom d\'utilisateur ou mot de passe incorrect.'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Données invalides.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée.'
    })


def check_auth_status(request):
    """Vérifier le statut d'authentification via AJAX"""
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
        'full_name': request.user.get_full_name() if request.user.is_authenticated else None
    })


def forgot_password_view(request):
    """Page mot de passe oublié"""
    if request.user.is_authenticated:
        return redirect('content_management:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Ici, implémenter l'envoi d'email de réinitialisation
                messages.success(request, 'Si un compte existe avec cette adresse email, vous recevrez un lien de réinitialisation.')
                return redirect('oauth:login')
            except User.DoesNotExist:
                # Ne pas révéler si l'email existe ou non pour la sécurité
                messages.success(request, 'Si un compte existe avec cette adresse email, vous recevrez un lien de réinitialisation.')
                return redirect('oauth:login')
        else:
            messages.error(request, 'Veuillez fournir votre adresse email.')
    
    return render(request, 'oauth/forgot_password.html', {
        'page_title': 'Mot de passe oublié - CSIG'
    })


def terms_of_service_view(request):
    """Conditions d'utilisation"""
    return render(request, 'oauth/terms.html', {
        'page_title': 'Conditions d\'utilisation - CSIG'
    })


def privacy_policy_view(request):
    """Politique de confidentialité"""
    return render(request, 'oauth/privacy.html', {
        'page_title': 'Politique de confidentialité - CSIG'
    })


def contact_support_view(request):
    """Contacter le support"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            # Ici, implémenter l'envoi d'email au support
            messages.success(request, 'Votre message a été envoyé au support. Nous vous répondrons dans les plus brefs délais.')
            return redirect('oauth:contact_support')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
    return render(request, 'oauth/contact_support.html', {
        'page_title': 'Contacter le support - CSIG'
    })

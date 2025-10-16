from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, UserRole


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Formulaire de création d'utilisateur personnalisé"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@csig.gn'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+224 123 456 789'
        })
    )
    job_title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Poste ou fonction'
        })
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Département ou service'
        })
    )
    language = forms.ChoiceField(
        choices=[('fr', 'Français'), ('en', 'English')],
        initial='fr',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text=_('Sélectionnez les rôles à attribuer à cet utilisateur')
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'job_title', 'department', 'language', 'roles'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les messages d'aide
        self.fields['username'].help_text = _(
            'Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.'
        )
        self.fields['password1'].help_text = _(
            'Votre mot de passe doit contenir au moins 8 caractères et ne peut pas être entièrement numérique.'
        )
        self.fields['password2'].help_text = _('Entrez le même mot de passe que précédemment, pour vérification.')
    
    def clean_email(self):
        """Vérifier l'unicité de l'email"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Un utilisateur avec cette adresse email existe déjà.'))
        return email
    
    def clean_phone(self):
        """Vérifier le format du téléphone"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Supprimer les espaces et caractères spéciaux
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 8:
                raise forms.ValidationError(_('Le numéro de téléphone doit contenir au moins 8 chiffres.'))
        return phone
    
    def save(self, commit=True):
        """Sauvegarder l'utilisateur et créer son profil"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.job_title = self.cleaned_data['job_title']
        user.department = self.cleaned_data['department']
        user.language = self.cleaned_data['language']
        
        if commit:
            user.save()
            # Créer le profil utilisateur
            UserProfile.objects.create(user=user)
            # Attribuer les rôles
            if self.cleaned_data.get('roles'):
                user.roles.set(self.cleaned_data['roles'])
        
        return user


class CustomUserChangeForm(UserChangeForm):
    """Formulaire de modification d'utilisateur personnalisé"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@csig.gn'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+224 123 456 789'
        })
    )
    job_title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Poste ou fonction'
        })
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Département ou service'
        })
    )
    language = forms.ChoiceField(
        choices=[('fr', 'Français'), ('en', 'English')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text=_('Sélectionnez les rôles à attribuer à cet utilisateur')
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'job_title', 'department', 'language', 'roles', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-remplir les rôles actuels
        if self.instance.pk:
            self.fields['roles'].initial = self.instance.roles.all()
    
    def clean_email(self):
        """Vérifier l'unicité de l'email (exclure l'utilisateur actuel)"""
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(_('Un utilisateur avec cette adresse email existe déjà.'))
        return email


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification du profil utilisateur"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Parlez-nous de vous...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://votre-site.com'
            }),
        }
    
    def clean_avatar(self):
        """Vérifier la taille et le type de l'avatar"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Vérifier la taille (max 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('L\'image ne doit pas dépasser 5MB.'))
            
            # Vérifier le type de fichier
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                raise forms.ValidationError(_('Seuls les formats JPEG, PNG et GIF sont autorisés.'))
        
        return avatar


class UserRoleForm(forms.ModelForm):
    """Formulaire de création/modification de rôle utilisateur"""
    class Meta:
        model = UserRole
        fields = ['name', 'description', 'is_active', 'permissions']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du rôle...'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permissions': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Grouper les permissions par application
        self.fields['permissions'].queryset = self.fields['permissions'].queryset.select_related('content_type')


class UserSearchForm(forms.Form):
    """Formulaire de recherche d'utilisateurs"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, email, poste...'
        })
    )
    role = forms.ModelChoiceField(
        queryset=UserRole.objects.filter(is_active=True),
        required=False,
        empty_label=_('Tous les rôles'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Département'
        })
    )
    is_active = forms.ChoiceField(
        choices=[
            ('', _('Tous les statuts')),
            ('1', _('Actif')),
            ('0', _('Inactif'))
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_joined_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_joined_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class BulkUserActionForm(forms.Form):
    """Formulaire pour les actions en lot sur les utilisateurs"""
    ACTION_CHOICES = [
        ('activate', _('Activer')),
        ('deactivate', _('Désactiver')),
        ('delete', _('Supprimer')),
        ('add_role', _('Ajouter un rôle')),
        ('remove_role', _('Retirer un rôle')),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    role = forms.ModelChoiceField(
        queryset=UserRole.objects.filter(is_active=True),
        required=False,
        empty_label=_('Sélectionner un rôle'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    user_ids = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    def clean(self):
        """Validation personnalisée"""
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        role = cleaned_data.get('role')
        
        if action in ['add_role', 'remove_role'] and not role:
            raise forms.ValidationError(_('Un rôle doit être sélectionné pour cette action.'))
        
        return cleaned_data


class UserInvitationForm(forms.Form):
    """Formulaire d'invitation d'utilisateur"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@csig.gn'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom (optionnel)'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom (optionnel)'
        })
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=UserRole.objects.filter(is_active=True),
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text=_('Sélectionnez au moins un rôle à attribuer')
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Message d\'invitation personnalisé (optionnel)...'
        })
    )
    
    def clean_email(self):
        """Vérifier que l'email n'est pas déjà utilisé"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Un utilisateur avec cette adresse email existe déjà.'))
        return email

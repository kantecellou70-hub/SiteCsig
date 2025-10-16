from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Article, Event, Project, ProjectPartner, Program, 
    Partner, Newsletter, NewsletterCampaign, ContactMessage, EventDay, EventAgenda, EventIntervenant, EventFAQ, EventOrganizer, EventTag,
    EventRegistrationForm, FormField, FormFieldOption, EventRegistration, TeamMember, ConferenceRoom, RoomImage, ExternalOrganization, RoomBooking, BookingPayment, RoomMaintenance, Personna, Blog, AboutPage, CityDistrict, CoreValue, HeroStatistic, Achievement
)
from django.utils import timezone


class MultipleFileInput(forms.FileInput):
    """Widget personnalisé pour l'upload de fichiers multiples"""
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = 'multiple'
        super().__init__(attrs)
    
    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon', 'is_active', 'order', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom de la catégorie')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Description')}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Classe CSS de l\'icône (ex: fas fa-science)')}),
            'is_active': forms.Select(choices=[(True, _('Actif')), (False, _('Inactif'))], attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


class ArticleForm(forms.ModelForm):
    images = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label=_("Images supplémentaires")
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'excerpt', 'content',
            'category', 'author', 'featured_image', 'video_url', 'audio_file', 
            'status', 'published_at', 'is_featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Titre de l\'article')}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Extrait de l\'article')}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'style': 'display: none;'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('URL de la vidéo YouTube ou Vimeo')}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 60, 'placeholder': _('Titre pour le SEO (max 60 caractères)')}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'maxlength': 160, 'placeholder': _('Description pour le SEO (max 160 caractères)')}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraire les catégories des kwargs si elles sont passées
        categories = kwargs.pop('categories', None)
        print(f"DEBUG FORM: categories parameter: {categories}")
        
        super().__init__(*args, **kwargs)
        
        # Utiliser les catégories passées en paramètre ou filtrer par défaut
        if categories is not None:
            print(f"DEBUG FORM: Setting queryset to {categories.count()} categories")
            self.fields['category'].queryset = categories
            print(f"DEBUG FORM: Queryset set, now has {self.fields['category'].queryset.count()} items")
        else:
            print("DEBUG FORM: No categories parameter, using default filter")
            # Filtrer les catégories actives (avec fallback si le champ n'existe pas)
            try:
                self.fields['category'].queryset = Category.objects.filter(is_active=True).order_by('order', 'name')
            except:
                # Fallback si le champ is_active n'existe pas
                self.fields['category'].queryset = Category.objects.all().order_by('order', 'name')
        
        # Cacher le champ auteur car il sera automatiquement défini
        self.fields['author'].widget = forms.HiddenInput()
        

        
        # Rendre la date de publication optionnelle
        self.fields['published_at'].required = False
        

        
        # Rendre la catégorie optionnelle
        self.fields['category'].required = False
        
        # Rendre les autres champs optionnels
        self.fields['featured_image'].required = False
        self.fields['video_url'].required = False
        self.fields['audio_file'].required = False
        self.fields['meta_title'].required = False
        self.fields['meta_description'].required = False


class EventForm(forms.ModelForm):
    """Formulaire pour créer/modifier un événement"""
    class Meta:
        model = Event
        fields = [
            'title', 'description',
            'start_date', 'end_date', 'start_time', 'end_time',
            'location', 'address', 'city', 'country',
            'direct_link', 'registration_link', 'website',
            'contact_email', 'contact_phone',
            'registration_required', 'max_participants', 'is_free', 'price',
            'status', 'is_featured', 'is_public',
            'featured_image', 'banner_image',
            'meta_title', 'meta_description',
            'tags', 'event_type',
            'scientific_field', 'target_audience', 'language'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'registration_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['tags']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Définir une valeur par défaut pour le statut si c'est un nouvel événement
        if not self.instance.pk:
            self.fields['status'].initial = 'draft'
            # S'assurer que le champ status a les bonnes options
            self.fields['status'].choices = [
                ('draft', 'Brouillon'),
                ('published', 'Publié'),
                ('trash', 'Corbeille')
            ]
        
        # Validation personnalisée pour les dates
        if self.instance.pk:
            self.fields['start_date'].widget.attrs['min'] = self.instance.start_date.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")

        if start_date == end_date and start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("L'heure de fin doit être postérieure à l'heure de début pour un événement d'une journée.")

        return cleaned_data
    
    def save(self, commit=True):
        event = super().save(commit=False)
        # Définir automatiquement la devise en GNF
        event.currency = 'GNF'
        
        if commit:
            event.save()
            # Sauvegarder les relations many-to-many
            self.save_m2m()
        
        return event


class EventDayForm(forms.ModelForm):
    """Formulaire pour créer/modifier un jour d'événement"""
    class Meta:
        model = EventDay
        fields = ['date', 'day_number', 'title', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'day_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        if self.event:
            self.fields['date'].widget.attrs['min'] = self.event.start_date.strftime('%Y-%m-%d')
            self.fields['date'].widget.attrs['max'] = self.event.end_date.strftime('%Y-%m-%d')


class EventAgendaForm(forms.ModelForm):
    """Formulaire pour créer/modifier un élément d'agenda"""
    class Meta:
        model = EventAgenda
        fields = ['start_time', 'end_time', 'activity', 'description', 'location', 'activity_type', 'order']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'activity': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("L'heure de fin doit être postérieure à l'heure de début.")

        return cleaned_data


class EventIntervenantForm(forms.ModelForm):
    """Formulaire pour les intervenants d'événement"""
    class Meta:
        model = EventIntervenant
        fields = ['nom', 'profession', 'photo', 'biographie', 'email', 'telephone', 'linkedin', 'twitter', 'website']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet de l\'intervenant'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profession, titre ou poste'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'biographie': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Biographie professionnelle...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+224 XXX XXX XXX'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/profil'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/username'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://exemple.com'}),
        }


class EventFAQForm(forms.ModelForm):
    """Formulaire pour créer/modifier une FAQ"""
    class Meta:
        model = EventFAQ
        fields = ['question', 'answer', 'category', 'order', 'is_public']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventOrganizerForm(forms.ModelForm):
    """Formulaire pour créer/modifier un organisateur"""
    class Meta:
        model = EventOrganizer
        fields = ['name', 'logo', 'description', 'website', 'role', 'organization_type', 'contact_email', 'contact_phone', 'address', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Université de Conakry'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de l\'organisation et de son rôle dans l\'événement'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'role': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('organizer', 'Organisateur principal'),
                ('co_organizer', 'Co-organisateur'),
                ('partner', 'Partenaire'),
                ('sponsor', 'Sponsor'),
                ('supporter', 'Soutien'),
                ('other', 'Autre'),
            ]),
            'organization_type': forms.Select(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@exemple.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+224 XXX XXX XXX'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse complète'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class EventTagForm(forms.ModelForm):
    """Formulaire pour créer/modifier un tag d'événement"""
    class Meta:
        model = EventTag
        fields = ['name', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'short_description',
            'featured_image', 'start_date', 'end_date', 'status', 'budget',
            'objectives', 'results', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Titre du projet')}),
            'description': forms.Textarea(attrs={'class': 'form-control django-ckeditor-5'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Description courte du projet')}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),

            'objectives': forms.Textarea(attrs={'class': 'form-control django-ckeditor-5'}),
            'results': forms.Textarea(attrs={'class': 'form-control django-ckeditor-5'}),
        }


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'title', 'description', 'short_description', 'featured_image',
            'duration', 'level', 'max_students', 'price', 'is_free',
            'start_date', 'end_date', 'status', 'is_featured',
            'slug', 'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Titre du programme')}),
            'description': forms.Textarea(attrs={'class': 'form-control django-ckeditor-5'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Description courte du programme')}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 6 mois, 1 an, etc.')}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('URL unique du programme')}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Titre pour le référencement (SEO)')}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Description pour le référencement (SEO)')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].required = False
        self.fields['meta_title'].required = False
        self.fields['meta_description'].required = False
        self.fields['slug'].required = False
        self.fields['short_description'].required = False
        self.fields['featured_image'].required = False
        self.fields['duration'].required = False
        self.fields['max_students'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'logo', 'website', 'contact_email', 'contact_phone', 'description', 'partnership_type', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom du partenaire')}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('Site web du partenaire')}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email de contact')}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Téléphone de contact')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Description du partenariat')}),
            'partnership_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'first_name', 'last_name', 'language']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Votre adresse email')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Votre prénom')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Votre nom')}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Votre nom complet')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Votre adresse email')}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Sujet de votre message')}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Votre message')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Votre numéro de téléphone (optionnel)')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False


class NewsletterCampaignForm(forms.ModelForm):
    """Formulaire pour créer/modifier une campagne de newsletter"""
    class Meta:
        model = NewsletterCampaign
        fields = [
            'title', 'subject', 'content', 'template_name', 'status', 
            'scheduled_at', 'target_language', 'target_active_only'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': _('Titre de la campagne')
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': _('Sujet de l\'email')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 10, 
                'placeholder': _('Contenu de la newsletter (HTML autorisé)')
            }),
            'template_name': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('newsletter_default.html', 'Template par défaut'),
                ('newsletter_news.html', 'Template actualités'),
                ('newsletter_event.html', 'Template événements'),
                ('newsletter_custom.html', 'Template personnalisé'),
            ]),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'target_language': forms.Select(attrs={
                'class': 'form-control'
            }),
            'target_active_only': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ scheduled_at optionnel
        self.fields['scheduled_at'].required = False
        # Ajouter des classes CSS pour le style
        self.fields['content'].widget.attrs.update({
            'class': 'form-control summernote'
        })


# Formulaires de recherche
class ArticleSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Rechercher un article...')
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("Toutes les catégories"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', _('Tous les statuts')), ('draft', _('Brouillon')), ('published', _('Publié')), ('trash', _('Corbeille'))],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Rechercher un événement...')
        })
    )
    status = forms.ChoiceField(
        choices=[('', _('Tous les statuts')), ('draft', _('Brouillon')), ('published', _('Publié')), ('trash', _('Corbeille'))],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    upcoming = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# Formulaires pour la gestion en ligne
class EventDayInlineFormSet(forms.BaseInlineFormSet):
    """Formset pour gérer les jours d'événement"""
    def clean(self):
        super().clean()
        dates = []
        day_numbers = []
        
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                date = form.cleaned_data.get('date')
                day_number = form.cleaned_data.get('day_number')
                
                if date in dates:
                    raise forms.ValidationError("Chaque jour doit avoir une date unique.")
                if day_number in day_numbers:
                    raise forms.ValidationError("Chaque jour doit avoir un numéro unique.")
                
                dates.append(date)
                day_numbers.append(day_number)


class EventAgendaInlineFormSet(forms.BaseInlineFormSet):
    """Formset pour gérer l'agenda d'un jour"""
    def clean(self):
        super().clean()
        times = []
        
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                start_time = form.cleaned_data.get('start_time')
                end_time = form.cleaned_data.get('end_time')
                
                if start_time and end_time:
                    time_range = (start_time, end_time)
                    if time_range in times:
                        raise forms.ValidationError("Les créneaux horaires ne doivent pas se chevaucher.")
                    times.append(time_range)


class EventRegistrationFormForm(forms.ModelForm):
    """Formulaire pour créer/modifier un formulaire d'inscription"""
    class Meta:
        model = EventRegistrationForm
        fields = [
            'title', 'description', 'is_active', 'allow_multiple_registrations',
            'max_registrations', 'registration_deadline', 'send_confirmation_email',
            'confirmation_message', 'terms_and_conditions', 'require_terms_acceptance',
            'primary_color', 'secondary_color', 'logo'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du formulaire d\'inscription'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du formulaire...'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'confirmation_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Message affiché après inscription...'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Conditions générales d\'inscription...'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FormFieldForm(forms.ModelForm):
    """Formulaire pour créer/modifier un champ de formulaire"""
    class Meta:
        model = FormField
        fields = [
            'label', 'field_type', 'placeholder', 'help_text', 'required',
            'min_length', 'max_length', 'min_value', 'max_value',
            'has_options', 'allowed_file_types', 'max_file_size',
            'order', 'is_visible', 'depends_on', 'show_when_value'
        ]
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Libellé du champ'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'placeholder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texte d\'aide'}),
            'help_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Aide détaillée...'}),
            'min_length': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'max_length': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'min_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowed_file_types': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: .pdf,.doc,.jpg (séparés par des virgules)'}),
            'max_file_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Taille en MB'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'show_when_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valeur qui déclenche l\'affichage'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les champs de dépendance pour éviter les références circulaires
        if self.instance.pk:
            self.fields['depends_on'].queryset = FormField.objects.filter(
                form=self.instance.form
            ).exclude(pk=self.instance.pk)
        
        # Masquer certains champs selon le type
        self.fields['min_length'].widget.attrs['style'] = 'display: none;'
        self.fields['max_length'].widget.attrs['style'] = 'display: none;'
        self.fields['min_value'].widget.attrs['style'] = 'display: none;'
        self.fields['max_value'].widget.attrs['style'] = 'display: none;'
        self.fields['has_options'].widget.attrs['style'] = 'display: none;'
        self.fields['allowed_file_types'].widget.attrs['style'] = 'display: none;'
        self.fields['max_file_size'].widget.attrs['style'] = 'display: none;'
        self.fields['depends_on'].widget.attrs['style'] = 'display: none;'
        self.fields['show_when_value'].widget.attrs['style'] = 'display: none;'


class FormFieldOptionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une option de champ"""
    class Meta:
        model = FormFieldOption
        fields = ['label', 'value', 'order', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Libellé affiché'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valeur stockée'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class EventRegistrationPublicForm(forms.ModelForm):
    """Formulaire d'inscription à un événement"""
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre.email@exemple.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre numéro de téléphone'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.form_fields = kwargs.pop('form_fields', [])
        super().__init__(*args, **kwargs)
        
        # Ajouter dynamiquement les champs personnalisés
        for field in self.form_fields:
            if field.is_visible:
                self.fields[f'field_{field.pk}'] = self.create_dynamic_field(field)
    
    def create_dynamic_field(self, form_field):
        """Crée un champ de formulaire dynamique selon le type"""
        field_kwargs = {
            'label': form_field.label,
            'required': form_field.required,
            'help_text': form_field.help_text,
        }
        
        if form_field.placeholder:
            field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'placeholder': form_field.placeholder})
        
        if form_field.field_type == 'text':
            field = forms.CharField(max_length=form_field.max_length or 200, **field_kwargs)
        elif form_field.field_type == 'textarea':
            field = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), **field_kwargs)
        elif form_field.field_type == 'email':
            field = forms.EmailField(**field_kwargs)
        elif form_field.field_type == 'phone':
            field = forms.CharField(max_length=20, **field_kwargs)
        elif form_field.field_type == 'date':
            field = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), **field_kwargs)
        elif form_field.field_type == 'datetime':
            field = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), **field_kwargs)
        elif form_field.field_type == 'number':
            field = forms.DecimalField(
                max_digits=10, 
                decimal_places=2,
                min_value=form_field.min_value,
                max_value=form_field.max_value,
                **field_kwargs
            )
        elif form_field.field_type in ['select', 'radio']:
            choices = [(opt.value, opt.label) for opt in form_field.options.all()]
            field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), **field_kwargs)
        elif form_field.field_type == 'multiselect':
            choices = [(opt.value, opt.label) for opt in form_field.options.all()]
            field = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}), **field_kwargs)
        elif form_field.field_type == 'checkbox':
            field = forms.BooleanField(**field_kwargs)
        elif form_field.field_type == 'file':
            field = forms.FileField(**field_kwargs)
        elif form_field.field_type == 'url':
            field = forms.URLField(**field_kwargs)
        elif form_field.field_type == 'note':
            field = forms.CharField(widget=forms.HiddenInput(), required=False)
            field.widget.attrs['style'] = 'display: none;'
        elif form_field.field_type == 'divider':
            field = forms.CharField(widget=forms.HiddenInput(), required=False)
            field.widget.attrs['style'] = 'display: none;'
        else:
            field = forms.CharField(**field_kwargs)
        
        return field


# Formsets pour la gestion des champs et options
def get_form_field_formset():
    """Retourne le formset pour les champs de formulaire"""
    return forms.inlineformset_factory(
        EventRegistrationForm, 
        FormField, 
        form=FormFieldForm,
        extra=1,
        can_delete=True,
        fields=['label', 'field_type', 'placeholder', 'help_text', 'required', 'order']
    )

def get_form_field_option_formset():
    """Retourne le formset pour les options de champ"""
    return forms.inlineformset_factory(
        FormField, 
        FormFieldOption, 
        form=FormFieldOptionForm,
        extra=1,
        can_delete=True,
        fields=['label', 'value', 'order', 'is_default']
    )


class ProjectPartnerForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier un partenaire de projet"""
    class Meta:
        model = ProjectPartner
        fields = ['name', 'logo', 'role', 'description', 'website', 'contact_email', 'contact_phone', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du partenaire'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rôle dans le projet'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du partenaire'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemple.com'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@partenaire.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+224 XXX XXX XXX'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Rendre certains champs optionnels
        self.fields['logo'].required = False
        self.fields['website'].required = False
        self.fields['contact_email'].required = False
        self.fields['contact_phone'].required = False
        self.fields['description'].required = False
        self.fields['order'].required = False
        
        # Définir l'ordre par défaut
        if not self.instance.pk:
            self.fields['order'].initial = 0


class TeamMemberForm(forms.ModelForm):
    """Formulaire pour les membres de l'équipe"""
    
    class Meta:
        model = TeamMember
        fields = [
            'first_name', 'last_name', 'email', 'job_title', 'category', 'biography',
            'linkedin', 'twitter', 'youtube', 'facebook', 'photo', 'slug',
            'is_active', 'order'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du membre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du membre'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Poste occupé (ex: Directeur, Chercheur, etc.)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Slug automatique (nom-prenom)'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Biographie du membre...'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/...'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/...'
            }),
            'youtube': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/...'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier si l'email existe déjà pour un autre membre
            instance = getattr(self, 'instance', None)
            if instance and instance.pk:
                # Mode édition - exclure l'instance actuelle
                if TeamMember.objects.exclude(pk=instance.pk).filter(email=email).exists():
                    raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre membre.")
            else:
                # Mode création
                if TeamMember.objects.filter(email=email).exists():
                    raise forms.ValidationError("Cette adresse email est déjà utilisée par un autre membre.")
        return email


class ConferenceRoomForm(forms.ModelForm):
    """Formulaire pour les salles de conférence"""
    
    class Meta:
        model = ConferenceRoom
        fields = [
            'name', 'description', 'capacity', 'area', 'price_per_hour', 
            'price_per_day', 'features', 'is_active', 'maintenance_until'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la salle'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de la salle'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Capacité'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Surface en m²'
            }),
            'price_per_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': 'Prix par heure'
            }),
            'price_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': 'Prix par jour'
            }),
            'features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Équipements disponibles (un par ligne)'
            }),
            'maintenance_until': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_features(self):
        """Nettoie et formate le texte des équipements"""
        features_text = self.cleaned_data.get('features', '')
        if features_text:
            # Supprimer les espaces en début et fin, et normaliser les séparateurs
            return features_text.strip()
        return ''


class RoomImageForm(forms.ModelForm):
    """Formulaire pour les images de salle"""
    
    class Meta:
        model = RoomImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Légende de l\'image'
            }),
        }


class ExternalOrganizationForm(forms.ModelForm):
    """Formulaire pour les organisations externes"""
    
    class Meta:
        model = ExternalOrganization
        fields = [
            'name', 'organization_type', 'contact_person', 'email', 'phone',
            'address', 'website', 'tax_id', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de l\'organisation'
            }),
            'organization_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Personne de contact'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Site web'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de TVA'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes'
            }),
        }


class RoomBookingForm(forms.ModelForm):
    """Formulaire pour les réservations de salle"""
    
    class Meta:
        model = RoomBooking
        fields = [
            'room', 'organization', 'event_title', 'event_description',
            'start_time', 'end_time', 'attendees_count', 'special_requirements'
        ]
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control'
            }),
            'organization': forms.Select(attrs={
                'class': 'form-control'
            }),
            'event_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l\'événement'
            }),
            'event_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de l\'événement'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'attendees_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Nombre de participants'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Exigences spéciales'
            }),
        }
    
    def clean(self):
        """Validation personnalisée pour éviter les conflits"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("L'heure de fin doit être postérieure à l'heure de début.")
            
            if start_time < timezone.now():
                raise forms.ValidationError("La date de début ne peut pas être dans le passé.")
            
            # Vérifier la disponibilité de la salle
            if room:
                if not room.is_available:
                    raise forms.ValidationError("Cette salle n'est pas disponible.")
                
                # Vérifier les conflits avec d'autres réservations
                conflicting_bookings = RoomBooking.objects.filter(
                    room=room,
                    status__in=['confirmed', 'pending'],
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                
                if conflicting_bookings.exists():
                    # Générer un rapport détaillé des conflits
                    conflicts_count = conflicting_bookings.count()
                    raise forms.ValidationError(
                        f"Conflit détecté avec {conflicts_count} réservation(s) existante(s). "
                        "Veuillez vérifier le calendrier de disponibilité."
                    )
        
        return cleaned_data


class BookingPaymentForm(forms.ModelForm):
    """Formulaire pour les paiements de réservation"""
    
    class Meta:
        model = BookingPayment
        fields = [
            'amount', 'payment_type', 'payment_method', 'reference', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': 'Montant'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence du paiement'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur le paiement'
            }),
        }


class RoomMaintenanceForm(forms.ModelForm):
    """Formulaire pour la maintenance des salles"""
    
    class Meta:
        model = RoomMaintenance
        fields = [
            'room', 'title', 'description', 'start_date', 'end_date',
            'maintenance_type', 'status', 'priority', 'estimated_cost', 'technician', 'notes'
        ]
        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la maintenance'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de la maintenance'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'maintenance_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01,
                'placeholder': 'Coût estimé'
            }),
            'technician': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Technicien'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes'
            }),
        }
    
    def clean(self):
        """Validation personnalisée"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
            
            if start_date < timezone.now():
                raise forms.ValidationError("La date de début ne peut pas être dans le passé.")
        
        return cleaned_data


class BookingSearchForm(forms.Form):
    """Formulaire de recherche pour les réservations"""
    room = forms.ModelChoiceField(
        queryset=ConferenceRoom.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les salles",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    organization = forms.ModelChoiceField(
        queryset=ExternalOrganization.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les organisations",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + RoomBooking._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par titre d\'événement...'
        })
    )


class PersonnaForm(forms.ModelForm):
    class Meta:
        model = Personna
        fields = ['name', 'description', 'is_active', 'featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du personna'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du personna'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError("Le nom doit contenir au moins 3 caractères.")
        if len(name) > 100:
            raise forms.ValidationError("Le nom ne peut pas dépasser 100 caractères.")
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError("La description doit contenir au moins 10 caractères.")
        return description


class BlogForm(forms.ModelForm):
    """Formulaire pour les blogs"""
    
    class Meta:
        model = Blog
        fields = [
            'title', 'content', 'image', 'video_url',
            'personna', 'status', 'is_active', 'featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du blog'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control ckeditor5',
                'rows': 12,
                'placeholder': 'Contenu du blog avec mise en forme (gras, italique, souligné, etc.)'
            }),

            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'personna': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        
        if title:
            if len(title.strip()) < 5:
                raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
        
        if content:
            if len(content.strip()) < 50:
                raise forms.ValidationError("Le contenu doit contenir au moins 50 caractères.")
        
        return cleaned_data


class CityDistrictForm(forms.ModelForm):
    """Formulaire pour les quartiers de la cité"""
    
    class Meta:
        model = CityDistrict
        fields = ['name', 'description', 'icon', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du quartier'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du quartier'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-building'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CoreValueForm(forms.ModelForm):
    """Formulaire pour les valeurs fondamentales"""
    
    class Meta:
        model = CoreValue
        fields = ['icon', 'name', 'description', 'order', 'is_active']
        widgets = {
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-lightbulb'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la valeur'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de la valeur'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class HeroStatisticForm(forms.ModelForm):
    """Formulaire pour les statistiques hero"""
    
    class Meta:
        model = HeroStatistic
        fields = ['number', 'label', 'order', 'is_active']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '50+'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Projets innovants'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AchievementForm(forms.ModelForm):
    """Formulaire pour les réalisations"""
    
    class Meta:
        model = Achievement
        fields = ['icon', 'text', 'order', 'is_active']
        widgets = {
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-trophy'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de la réalisation'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AboutPageForm(forms.ModelForm):
    """Formulaire pour la page À propos"""
    
    class Meta:
        model = AboutPage
        fields = [
            'hero_title', 'hero_subtitle', 'hero_background',
            'history_title', 'history_content',
            'districts_title', 'districts_subtitle',
            'cta_title', 'cta_content',
            'show_districts'
        ]
        widgets = {
            'hero_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre principal de la page'}),
            'hero_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sous-titre principal'}),
            'hero_background': forms.FileInput(attrs={'class': 'form-control'}),
            'history_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la section histoire'}),
            'history_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu de l\'histoire'}),
            'districts_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la section quartiers'}),
            'districts_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Sous-titre des quartiers'}),
            'cta_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la section CTA'}),
            'cta_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contenu de la section CTA'}),
        }
    
    def clean_hero_stats(self):
        """Valide le format JSON des statistiques"""
        data = self.cleaned_data['hero_stats']
        try:
            if isinstance(data, str):
                import json
                json.loads(data)
        except (ValueError, TypeError):
            raise forms.ValidationError("Format JSON invalide pour les statistiques")
        return data
    
    def clean_achievements(self):
        """Valide le format JSON des réalisations"""
        data = self.cleaned_data['achievements']
        try:
            if isinstance(data, str):
                import json
                json.loads(data)
        except (ValueError, TypeError):
            raise forms.ValidationError("Format JSON invalide pour les réalisations")
        return data

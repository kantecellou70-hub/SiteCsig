from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Modèle de base avec timestamps"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date de modification"))
    
    class Meta:
        abstract = True


class StatusChoices(models.TextChoices):
    """Choix de statuts pour les contenus"""
    DRAFT = 'draft', _('Brouillon')
    PUBLISHED = 'published', _('Publié')
    TRASH = 'trash', _('Corbeille')


class Category(TimeStampedModel):
    """Catégorie d'articles"""
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    color = models.CharField(max_length=7, default="#0d4786", verbose_name=_("Couleur"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icône"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Catégorie parente"))
    
    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def articles(self):
        """Retourne tous les articles de cette catégorie"""
        return Article.objects.filter(category=self)
    
    @property
    def subcategories(self):
        """Retourne toutes les sous-catégories"""
        return Category.objects.filter(parent=self)


class Article(TimeStampedModel):
    """Article de blog"""
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    excerpt = models.TextField(max_length=500, blank=True, verbose_name=_("Extrait"))
    content = CKEditor5Field(verbose_name=_("Contenu"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Catégorie"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Auteur"))
    featured_image = models.ImageField(upload_to='articles/featured/', verbose_name=_("Image principale"))
    video_url = models.URLField(blank=True, verbose_name=_("URL vidéo"))
    audio_file = models.FileField(
        upload_to='articles/audio/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg'])],
        verbose_name=_("Fichier audio")
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name=_("Statut")
    )
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de publication"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de vues"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    meta_title = models.CharField(max_length=60, blank=True, verbose_name=_("Titre meta"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Description meta"))
    
    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('sfront:article_detail', kwargs={'slug': self.slug})


class ArticleImage(TimeStampedModel):
    """Images multiples pour les articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='articles/gallery/', verbose_name=_("Image"))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_("Légende"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    
    class Meta:
        verbose_name = _("Image d'article")
        verbose_name_plural = _("Images d'articles")
        ordering = ['order']


class Event(TimeStampedModel):
    """Événements scientifiques"""
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    description = CKEditor5Field(verbose_name=_("Description"))
    
    # Informations principales
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))
    start_time = models.TimeField(default='09:00', verbose_name=_("Heure de début"))
    end_time = models.TimeField(default='17:00', verbose_name=_("Heure de fin"))
    location = models.CharField(max_length=200, verbose_name=_("Lieu"))
    address = models.TextField(blank=True, verbose_name=_("Adresse complète"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("Ville"))
    country = models.CharField(max_length=100, blank=True, verbose_name=_("Pays"))
    
    # Liens et informations supplémentaires
    direct_link = models.URLField(blank=True, verbose_name=_("Lien direct"))
    registration_link = models.URLField(blank=True, verbose_name=_("Lien d'inscription"))
    website = models.URLField(blank=True, verbose_name=_("Site web de l'événement"))
    
    # Contact principal
    contact_email = models.EmailField(blank=True, verbose_name=_("Email de contact"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone de contact"))
    
    # Configuration
    registration_required = models.BooleanField(default=False, verbose_name=_("Inscription requise"))
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Nombre max de participants"))
    is_free = models.BooleanField(default=True, verbose_name=_("Gratuit"))
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Prix"))
    currency = models.CharField(max_length=3, default="GNF", verbose_name=_("Devise"))
    
    # Statut et visibilité
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name=_("Statut")
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    is_public = models.BooleanField(default=True, verbose_name=_("Public"))
    
    # Médias
    featured_image = models.ImageField(upload_to='events/', blank=True, verbose_name=_("Image principale"))
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, verbose_name=_("Bannière"))
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name=_("Titre meta"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Description meta"))
    
    # Tags et catégories
    tags = models.ManyToManyField('EventTag', blank=True, verbose_name=_("Tags"))
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('conference', _('Conférence')),
            ('seminar', _('Séminaire')),
            ('workshop', _('Atelier')),
            ('symposium', _('Symposium')),
            ('congress', _('Congrès')),
            ('exhibition', _('Exposition')),
            ('competition', _('Concours')),
            ('hackathon', _('Hackathon')),
            ('other', _('Autre')),
        ],
        default='conference',
        verbose_name=_("Type d'événement")
    )
    
    # Informations scientifiques
    scientific_field = models.CharField(max_length=100, blank=True, verbose_name=_("Domaine scientifique"))
    target_audience = models.CharField(max_length=200, blank=True, verbose_name=_("Public cible"))
    language = models.CharField(
        max_length=20,
        choices=[
            ('fr', _('Français')),
            ('en', _('Anglais')),
            ('fr-en', _('Français/Anglais')),
            ('other', _('Autre')),
        ],
        default='fr',
        verbose_name=_("Langue principale")
    )
    
    class Meta:
        verbose_name = _("Événement")
        verbose_name_plural = _("Événements")
        ordering = ['-start_date', '-start_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Nombre de jours de l'événement"""
        return (self.end_date - self.start_date).days + 1

    @property
    def is_multi_day(self):
        """Vérifie si l'événement dure plusieurs jours"""
        return self.start_date != self.end_date

    @property
    def full_location(self):
        """Adresse complète formatée"""
        parts = [self.location]
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    @property
    def time_range(self):
        """Plage horaire formatée"""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class EventDay(models.Model):
    """Journée spécifique d'un événement avec son agenda"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='days', verbose_name=_("Événement"))
    date = models.DateField(verbose_name=_("Date"))
    day_number = models.PositiveIntegerField(verbose_name=_("Numéro du jour"))
    title = models.CharField(max_length=200, blank=True, verbose_name=_("Titre du jour"))
    description = models.TextField(blank=True, verbose_name=_("Description du jour"))
    
    class Meta:
        verbose_name = _("Jour d'événement")
        verbose_name_plural = _("Jours d'événement")
        ordering = ['date', 'day_number']
        unique_together = ['event', 'date', 'day_number']

    def __str__(self):
        return f"Jour {self.day_number} - {self.date} - {self.event.title}"


class EventIntervenant(models.Model):
    """Intervenant d'une activité d'événement"""
    nom = models.CharField(max_length=200, default="Nom à compléter", verbose_name=_("Nom complet"))
    profession = models.CharField(max_length=200, default="Profession à compléter", verbose_name=_("Profession/Titre"))
    photo = models.ImageField(upload_to='intervenants/', blank=True, null=True, verbose_name=_("Photo"))
    biographie = models.TextField(default="Biographie à compléter", verbose_name=_("Biographie"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    telephone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    linkedin = models.URLField(blank=True, verbose_name=_("Profil LinkedIn"))
    twitter = models.URLField(blank=True, verbose_name=_("Profil Twitter"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    
    class Meta:
        verbose_name = _("Intervenant")
        verbose_name_plural = _("Intervenants")
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.profession}"

class EventAgenda(models.Model):
    """Agenda d'une journée d'événement"""
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE, related_name='activities', verbose_name=_("Jour d'événement"))
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))
    activity = models.CharField(max_length=200, verbose_name=_("Activité"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Lieu"))
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('keynote', _('Conférence plénière')),
            ('session', _('Session')),
            ('workshop', _('Atelier')),
            ('break', _('Pause')),
            ('lunch', _('Déjeuner')),
            ('networking', _('Networking')),
            ('poster', _('Session poster')),
            ('other', _('Autre')),
        ],
        default='session',
        verbose_name=_("Type d'activité")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    intervenants = models.ManyToManyField(EventIntervenant, blank=True, verbose_name=_("Intervenants"))
    
    class Meta:
        verbose_name = _("Élément d'agenda")
        verbose_name_plural = _("Éléments d'agenda")
        ordering = ['start_time', 'order']

    def __str__(self):
        return f"{self.start_time} - {self.activity}"





class EventFAQ(models.Model):
    """FAQ d'un événement"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='faqs', verbose_name=_("Événement"))
    question = models.CharField(max_length=500, verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Réponse"))
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', _('Général')),
            ('registration', _('Inscription')),
            ('logistics', _('Logistique')),
            ('scientific', _('Scientifique')),
            ('technical', _('Technique')),
            ('other', _('Autre')),
        ],
        default='general',
        verbose_name=_("Catégorie")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    is_public = models.BooleanField(default=True, verbose_name=_("Visible publiquement"))
    
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.question[:50]}..."


class EventOrganizer(models.Model):
    """Organisateur d'un événement"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='organizers', verbose_name=_("Événement"))
    name = models.CharField(max_length=200, verbose_name=_("Nom de l'organisation"))
    logo = models.ImageField(upload_to='events/organizers/', blank=True, null=True, verbose_name=_("Logo"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    role = models.CharField(max_length=100, blank=True, verbose_name=_("Rôle dans l'événement"))
    organization_type = models.CharField(
        max_length=50,
        choices=[
            ('university', _('Université')),
            ('research_center', _('Centre de recherche')),
            ('company', _('Entreprise')),
            ('ngo', _('ONG')),
            ('government', _('Institution gouvernementale')),
            ('other', _('Autre')),
        ],
        default='other',
        verbose_name=_("Type d'organisation")
    )
    contact_email = models.EmailField(blank=True, verbose_name=_("Email de contact"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    address = models.TextField(blank=True, verbose_name=_("Adresse"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    
    class Meta:
        verbose_name = _("Organisateur")
        verbose_name_plural = _("Organisateurs")
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class EventTag(models.Model):
    """Tags pour catégoriser les événements"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nom"))
    color = models.CharField(max_length=7, default="#0d4786", verbose_name=_("Couleur"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    class Meta:
        verbose_name = _("Tag d'événement")
        verbose_name_plural = _("Tags d'événement")
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    """Projets de recherche et développement"""
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    description = CKEditor5Field(verbose_name=_("Description"))
    short_description = models.TextField(max_length=300, verbose_name=_("Description courte"))
    featured_image = models.ImageField(upload_to='projects/', verbose_name=_("Image principale"))
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Date de fin"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', _('Planification')),
            ('active', _('Actif')),
            ('completed', _('Terminé')),
            ('on_hold', _('En attente')),
        ],
        default='planning',
        verbose_name=_("Statut")
    )
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Budget"))
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name=_("Membres de l'équipe"))
    partners_text = models.TextField(blank=True, verbose_name=_("Partenaires (texte libre)"))
    objectives = CKEditor5Field(verbose_name=_("Objectifs"))
    results = CKEditor5Field(blank=True, verbose_name=_("Résultats"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    
    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('sfront:project_detail', kwargs={'slug': self.slug})


class ProjectPartner(TimeStampedModel):
    """Partenaire d'un projet"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_partners', verbose_name=_("Projet"))
    name = models.CharField(max_length=200, verbose_name=_("Nom du partenaire"))
    logo = models.ImageField(upload_to='project_partners/logos/', blank=True, null=True, verbose_name=_("Logo"))
    role = models.CharField(max_length=200, verbose_name=_("Rôle dans le projet"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Email de contact"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    
    class Meta:
        verbose_name = _("Partenaire de projet")
        verbose_name_plural = _("Partenaires de projet")
        ordering = ['order', 'name']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.project.title}"
    
    def get_absolute_url(self):
        return reverse('content_management:project_detail', kwargs={'pk': self.project.pk})


class Program(TimeStampedModel):
    """Programmes éducatifs et de formation"""
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    description = CKEditor5Field(verbose_name=_("Description"))
    short_description = models.TextField(max_length=300, verbose_name=_("Description courte"))
    featured_image = models.ImageField(upload_to='programs/', verbose_name=_("Image principale"))
    duration = models.CharField(max_length=100, verbose_name=_("Durée"))
    level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', _('Débutant')),
            ('intermediate', _('Intermédiaire')),
            ('advanced', _('Avancé')),
        ],
        default='beginner',
        verbose_name=_("Niveau")
    )
    max_students = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Nombre max d'étudiants"))
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Prix"))
    is_free = models.BooleanField(default=True, verbose_name=_("Gratuit"))
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Date de début"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Date de fin"))
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name=_("Statut")
    )
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    meta_title = models.CharField(max_length=60, blank=True, verbose_name=_("Titre meta"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Description meta"))
    
    class Meta:
        verbose_name = _("Programme")
        verbose_name_plural = _("Programmes")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('sfront:program_detail', kwargs={'slug': self.slug})


class Partner(TimeStampedModel):
    """Partenaires institutionnels et privés"""
    name = models.CharField(max_length=200, verbose_name=_("Nom"))
    logo = models.ImageField(upload_to='partners/', verbose_name=_("Logo"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Email de contact"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone de contact"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    partnership_type = models.CharField(
        max_length=50,
        choices=[
            ('academic', _('Académique')),
            ('research', _('Recherche')),
            ('industrial', _('Industriel')),
            ('governmental', _('Gouvernemental')),
            ('ngo', _('ONG')),
        ],
        default='academic',
        verbose_name=_("Type de partenariat")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))
    
    class Meta:
        verbose_name = _("Partenaire")
        verbose_name_plural = _("Partenaires")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Newsletter(TimeStampedModel):
    """Newsletter pour les abonnés"""
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("Prénom"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("Nom"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    language = models.CharField(
        max_length=2,
        choices=[('fr', 'Français'), ('en', 'English')],
        default='fr',
        verbose_name=_("Langue préférée")
    )
    subscription_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date d'inscription"))
    
    class Meta:
        verbose_name = _("Abonné newsletter")
        verbose_name_plural = _("Abonnés newsletter")
        ordering = ['-subscription_date']
    
    def __str__(self):
        return self.email


class NewsletterCampaign(TimeStampedModel):
    """Campagne de newsletter"""
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('scheduled', _('Programmée')),
        ('sending', _('En cours d\'envoi')),
        ('completed', _('Terminée')),
        ('failed', _('Échouée')),
        ('cancelled', _('Annulée')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Titre de la campagne"))
    subject = models.CharField(max_length=200, verbose_name=_("Sujet de l'email"))
    content = models.TextField(verbose_name=_("Contenu de la newsletter"))
    template_name = models.CharField(
        max_length=100, 
        default='newsletter_default.html',
        verbose_name=_("Nom du template")
    )
    
    # Statut et programmation
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name=_("Statut")
    )
    scheduled_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Date et heure programmées")
    )
    
    # Statistiques d'envoi
    sent_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre d'emails envoyés"))
    failed_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre d'échecs"))
    opened_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre d'ouvertures"))
    clicked_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de clics"))
    
    # Métadonnées
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Créé par")
    )
    started_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Début d'envoi")
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Fin d'envoi")
    )
    
    # Filtres d'audience
    target_language = models.CharField(
        max_length=3,
        choices=[('fr', 'Français'), ('en', 'English'), ('all', 'Toutes')],
        default='all',
        verbose_name=_("Langue cible")
    )
    target_active_only = models.BooleanField(
        default=True, 
        verbose_name=_("Abonnés actifs uniquement")
    )
    
    class Meta:
        verbose_name = _("Campagne newsletter")
        verbose_name_plural = _("Campagnes newsletter")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_subscribers(self):
        """Nombre total d'abonnés cibles"""
        queryset = Newsletter.objects.all()
        
        if self.target_active_only:
            queryset = queryset.filter(is_active=True)
        
        if self.target_language != 'all':
            queryset = queryset.filter(language=self.target_language)
        
        return queryset.count()
    
    @property
    def success_rate(self):
        """Taux de succès de l'envoi"""
        if self.sent_count == 0:
            return 0
        return (self.sent_count / (self.sent_count + self.failed_count)) * 100
    
    def can_be_sent(self):
        """Vérifie si la campagne peut être envoyée"""
        if self.status not in ['draft', 'scheduled']:
            return False
        if self.scheduled_at and self.scheduled_at > timezone.now():
            return False
        return True


class ContactMessage(TimeStampedModel):
    """Messages de contact"""
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    email = models.EmailField(verbose_name=_("Email"))
    subject = models.CharField(max_length=200, verbose_name=_("Sujet"))
    message = models.TextField(verbose_name=_("Message"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    is_read = models.BooleanField(default=False, verbose_name=_("Lu"))
    
    class Meta:
        verbose_name = _("Message de contact")
        verbose_name_plural = _("Messages de contact")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteSettings(TimeStampedModel):
    """Paramètres du site"""
    site_name = models.CharField(max_length=100, default="Cité des Sciences et de l'Innovation de Guinée", verbose_name=_("Nom du site"))
    tagline = models.CharField(max_length=200, default="Explorer-Découvrir-Innover", verbose_name=_("Devise"))
    address = models.TextField(default="Rogbané, corniche nord Taouyah, Conakry, République de Guinée", verbose_name=_("Adresse"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    facebook_url = models.URLField(blank=True, verbose_name=_("URL Facebook"))
    twitter_url = models.URLField(blank=True, verbose_name=_("URL Twitter"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("URL LinkedIn"))
    youtube_url = models.URLField(blank=True, verbose_name=_("URL YouTube"))
    about_text = models.TextField(blank=True, verbose_name=_("Texte de présentation"))
    hero_title = models.CharField(max_length=200, blank=True, verbose_name=_("Titre de la page d'accueil"))
    hero_subtitle = models.TextField(blank=True, verbose_name=_("Sous-titre de la page d'accueil"))
    
    class Meta:
        verbose_name = _("Paramètre du site")
        verbose_name_plural = _("Paramètres du site")
    
    def __str__(self):
        return "Paramètres du site"
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class EventRegistrationForm(models.Model):
    """Formulaire d'inscription personnalisé pour un événement"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='registration_form', verbose_name=_("Événement"))
    title = models.CharField(max_length=200, verbose_name=_("Titre du formulaire"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Formulaire actif"))
    allow_multiple_registrations = models.BooleanField(default=False, verbose_name=_("Autoriser plusieurs inscriptions"))
    max_registrations = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Nombre maximum d'inscriptions"))
    registration_deadline = models.DateTimeField(null=True, blank=True, verbose_name=_("Date limite d'inscription"))
    send_confirmation_email = models.BooleanField(default=True, verbose_name=_("Envoyer un email de confirmation"))
    confirmation_message = models.TextField(blank=True, verbose_name=_("Message de confirmation"))
    terms_and_conditions = models.TextField(blank=True, verbose_name=_("Conditions générales"))
    require_terms_acceptance = models.BooleanField(default=False, verbose_name=_("Exiger l'acceptation des conditions"))
    
    # Styles et personnalisation
    primary_color = models.CharField(max_length=7, default="#667eea", verbose_name=_("Couleur principale"))
    secondary_color = models.CharField(max_length=7, default="#764ba2", verbose_name=_("Couleur secondaire"))
    logo = models.ImageField(upload_to='events/forms/logos/', blank=True, null=True, verbose_name=_("Logo du formulaire"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Dernière modification"))
    
    class Meta:
        verbose_name = _("Formulaire d'inscription")
        verbose_name_plural = _("Formulaires d'inscription")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Formulaire d'inscription - {self.event.title}"
    
    @property
    def total_registrations(self):
        """Nombre total d'inscriptions"""
        return self.registrations.count()
    
    @property
    def is_registration_open(self):
        """Vérifie si les inscriptions sont ouvertes"""
        if not self.is_active:
            return False
        if self.max_registrations and self.total_registrations >= self.max_registrations:
            return False
        if self.registration_deadline and timezone.now() > self.registration_deadline:
            return False
        return True


class FormField(models.Model):
    """Champ d'un formulaire d'inscription"""
    FIELD_TYPES = [
        ('text', _('Texte court')),
        ('textarea', _('Texte long')),
        ('email', _('Email')),
        ('phone', _('Téléphone')),
        ('date', _('Date')),
        ('datetime', _('Date et heure')),
        ('number', _('Nombre')),
        ('select', _('Sélection unique')),
        ('multiselect', _('Sélection multiple')),
        ('radio', _('Boutons radio')),
        ('checkbox', _('Cases à cocher')),
        ('file', _('Fichier')),
        ('url', _('URL')),
        ('note', _('Note/Description')),
        ('divider', _('Séparateur')),
    ]
    
    form = models.ForeignKey(EventRegistrationForm, on_delete=models.CASCADE, related_name='fields', verbose_name=_("Formulaire"))
    label = models.CharField(max_length=200, verbose_name=_("Libellé du champ"))
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, verbose_name=_("Type de champ"))
    placeholder = models.CharField(max_length=200, blank=True, verbose_name=_("Texte d'aide"))
    help_text = models.TextField(blank=True, verbose_name=_("Texte d'aide détaillé"))
    
    # Validation
    required = models.BooleanField(default=False, verbose_name=_("Champ obligatoire"))
    min_length = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Longueur minimale"))
    max_length = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Longueur maximale"))
    min_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Valeur minimale"))
    max_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Valeur maximale"))
    
    # Options pour les champs de sélection
    has_options = models.BooleanField(default=False, verbose_name=_("A des options de choix"))
    
    # Fichiers
    allowed_file_types = models.CharField(max_length=200, blank=True, verbose_name=_("Types de fichiers autorisés"))
    max_file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Taille maximale (MB)"))
    
    # Affichage
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_visible = models.BooleanField(default=True, verbose_name=_("Champ visible"))
    
    # Conditions
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_fields', verbose_name=_("Dépend de"))
    show_when_value = models.CharField(max_length=200, blank=True, verbose_name=_("Afficher quand la valeur est"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Dernière modification"))
    
    class Meta:
        verbose_name = _("Champ de formulaire")
        verbose_name_plural = _("Champs de formulaire")
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"
    
    @property
    def options(self):
        """Retourne les options du champ si c'est un champ de sélection"""
        if self.has_options:
            return self.options.all().order_by('order')
        return []


class FormFieldOption(models.Model):
    """Option pour un champ de formulaire de type sélection"""
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, related_name='options', verbose_name=_("Champ"))
    label = models.CharField(max_length=200, verbose_name=_("Libellé de l'option"))
    value = models.CharField(max_length=200, verbose_name=_("Valeur de l'option"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_default = models.BooleanField(default=False, verbose_name=_("Option par défaut"))
    
    class Meta:
        verbose_name = _("Option de champ")
        verbose_name_plural = _("Options de champ")
        ordering = ['order', 'label']
    
    def __str__(self):
        return f"{self.label} ({self.field.label})"


class EventRegistration(models.Model):
    """Inscription à un événement via le formulaire personnalisé"""
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('confirmed', _('Confirmée')),
        ('cancelled', _('Annulée')),
        ('waitlist', _('Liste d\'attente')),
    ]
    
    form = models.ForeignKey(EventRegistrationForm, on_delete=models.CASCADE, related_name='registrations', verbose_name=_("Formulaire"))
    registration_id = models.CharField(max_length=50, unique=True, verbose_name=_("ID d'inscription"))
    
    # Informations de base
    first_name = models.CharField(max_length=100, verbose_name=_("Prénom"))
    last_name = models.CharField(max_length=100, verbose_name=_("Nom"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Téléphone"))
    
    # Statut et gestion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Statut"))
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date d'inscription"))
    confirmation_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de confirmation"))
    cancelled_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Date d'annulation"))
    
    # Notes internes
    internal_notes = models.TextField(blank=True, verbose_name=_("Notes internes"))
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("Adresse IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    
    class Meta:
        verbose_name = _("Inscription à l'événement")
        verbose_name_plural = _("Inscriptions à l'événement")
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"Inscription de {self.first_name} {self.last_name} - {self.form.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.registration_id:
            # Générer un ID unique
            import uuid
            self.registration_id = f"REG-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def responses(self):
        """Retourne toutes les réponses de cette inscription"""
        return self.responses.all().order_by('field__order')


class FormResponse(models.Model):
    """Réponse à un champ spécifique du formulaire"""
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, related_name='responses', verbose_name=_("Inscription"))
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, verbose_name=_("Champ"))
    
    # Réponse selon le type de champ
    text_value = models.TextField(blank=True, verbose_name=_("Valeur texte"))
    number_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Valeur numérique"))
    date_value = models.DateField(null=True, blank=True, verbose_name=_("Valeur date"))
    datetime_value = models.DateTimeField(null=True, blank=True, verbose_name=_("Valeur date/heure"))
    boolean_value = models.BooleanField(null=True, blank=True, verbose_name=_("Valeur booléenne"))
    file_value = models.FileField(upload_to='events/registrations/files/', blank=True, null=True, verbose_name=_("Fichier"))
    
    # Options sélectionnées (pour les champs de type sélection)
    selected_options = models.ManyToManyField(FormFieldOption, blank=True, verbose_name=_("Options sélectionnées"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    
    class Meta:
        verbose_name = _("Réponse au formulaire")
        verbose_name_plural = _("Réponses au formulaire")
        unique_together = ['registration', 'field']
    
    def __str__(self):
        return f"Réponse de {self.registration.full_name} à {self.field.label}"
    
    @property
    def display_value(self):
        """Retourne la valeur affichable selon le type de champ"""
        if self.field.field_type in ['select', 'multiselect', 'radio', 'checkbox']:
            if self.selected_options.exists():
                return ", ".join([opt.label for opt in self.selected_options.all()])
            return ""
        elif self.field.field_type == 'file':
            return self.file_value.name if self.file_value else ""
        elif self.field.field_type == 'date':
            return self.date_value.strftime('%d/%m/%Y') if self.date_value else ""
        elif self.field.field_type == 'datetime':
            return self.datetime_value.strftime('%d/%m/%Y %H:%M') if self.datetime_value else ""
        elif self.field.field_type == 'number':
            return str(self.number_value) if self.number_value is not None else ""
        elif self.field.field_type == 'boolean':
            return "Oui" if self.boolean_value else "Non" if self.boolean_value is False else ""
        else:
            return self.text_value or ""
        




class TeamMember(TimeStampedModel):
    """Membre de l'équipe de la Cité des Sciences et de l'Innovation de Guinée"""
    
    CATEGORY_CHOICES = [
        ('management', _('Direction')),
        ('research', _('Recherche')),
        ('teaching', _('Enseignement')),
        ('technical', _('Technique')),
        ('administrative', _('Administratif')),
        ('communication', _('Communication')),
        ('other', _('Autre')),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name=_("Prénom"))
    last_name = models.CharField(max_length=100, verbose_name=_("Nom"))
    email = models.EmailField(verbose_name=_("Email"))
    job_title = models.CharField(max_length=200, verbose_name=_("Poste"), blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=_("Catégorie")
    )
    biography = models.TextField(verbose_name=_("Biographie"))
    linkedin = models.URLField(blank=True, verbose_name=_("Profil LinkedIn"))
    twitter = models.URLField(blank=True, verbose_name=_("Profil Twitter"))
    youtube = models.URLField(blank=True, verbose_name=_("Chaîne YouTube"))
    facebook = models.URLField(blank=True, verbose_name=_("Profil Facebook"))
    photo = models.ImageField(upload_to='team/', verbose_name=_("Photo"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"), blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    
    class Meta:
        verbose_name = _("Membre de l'équipe")
        verbose_name_plural = _("Membres de l'équipe")
        ordering = ['order', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        """Génère un slug unique au format 'nom-prenom' avec suffixe numérique si nécessaire"""
        base_slug = slugify(f"{self.last_name}-{self.first_name}")
        slug = base_slug
        counter = 1
        
        # Vérifier si le slug existe déjà
        while TeamMember.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    @property
    def full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Retourne le nom d'affichage (prénom + nom)"""
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('content_management:team_member_detail', kwargs={'slug': self.slug})
        




class ConferenceRoom(TimeStampedModel):
    """Salle de conférence"""
    name = models.CharField(max_length=100, verbose_name=_("Nom de la salle"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    capacity = models.PositiveIntegerField(verbose_name=_("Capacité"))
    area = models.PositiveIntegerField(help_text=_("Surface en m²"), verbose_name=_("Surface"))
    price_per_hour = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Prix par heure")
    )
    price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Prix par jour")
    )
    features = models.TextField(
        blank=True, 
        verbose_name=_("Équipements disponibles"),
        help_text=_("Liste des équipements: projecteur, son, wifi, etc. (séparés par des virgules ou des retours à la ligne)")
    )
    images = models.ManyToManyField(
        'RoomImage', 
        blank=True, 
        verbose_name=_("Images")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Disponible"))
    maintenance_until = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Maintenance jusqu'au")
    )
    
    class Meta:
        verbose_name = _("Salle de conférence")
        verbose_name_plural = _("Salles de conférence")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        """Vérifie si la salle est disponible"""
        if not self.is_active:
            return False
        if self.maintenance_until and timezone.now() < self.maintenance_until:
            return False
        return True
    
    def get_availability(self, start_date, end_date):
        """Vérifie la disponibilité pour une période donnée"""
        conflicting_bookings = self.bookings.filter(
            models.Q(start_time__lt=end_date) & 
            models.Q(end_time__gt=start_date) &
            models.Q(status__in=['confirmed', 'pending'])
        )
        return conflicting_bookings.count() == 0


class RoomImage(TimeStampedModel):
    """Image d'une salle de conférence"""
    image = models.ImageField(upload_to='rooms/', verbose_name=_("Image"))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_("Légende"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Image principale"))
    
    class Meta:
        verbose_name = _("Image de salle")
        verbose_name_plural = _("Images de salle")
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return self.caption or f"Image {self.id}"


class ExternalOrganization(TimeStampedModel):
    """Organisation externe qui loue des salles"""
    name = models.CharField(max_length=200, verbose_name=_("Nom de l'organisation"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    organization_type = models.CharField(
        max_length=50,
        choices=[
            ('company', _('Entreprise')),
            ('ngo', _('ONG')),
            ('government', _('Institution gouvernementale')),
            ('educational', _('Établissement éducatif')),
            ('other', _('Autre'))
        ],
        verbose_name=_("Type d'organisation")
    )
    contact_person = models.CharField(max_length=100, verbose_name=_("Personne de contact"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Téléphone"))
    address = models.TextField(blank=True, verbose_name=_("Adresse"))
    website = models.URLField(blank=True, verbose_name=_("Site web"))
    tax_id = models.CharField(max_length=50, blank=True, verbose_name=_("Numéro de TVA"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    
    class Meta:
        verbose_name = _("Organisation externe")
        verbose_name_plural = _("Organisations externes")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class RoomBooking(TimeStampedModel):
    """Réservation d'une salle de conférence"""
    room = models.ForeignKey(
        ConferenceRoom, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_("Salle")
    )
    organization = models.ForeignKey(
        ExternalOrganization, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name=_("Organisation")
    )
    event_title = models.CharField(max_length=200, verbose_name=_("Titre de l'événement"))
    event_description = models.TextField(blank=True, verbose_name=_("Description de l'événement"))
    start_time = models.DateTimeField(verbose_name=_("Heure de début"))
    end_time = models.DateTimeField(verbose_name=_("Heure de fin"))
    attendees_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Nombre de participants"),
        help_text=_("Nombre estimé de participants")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('En attente')),
            ('confirmed', _('Confirmée')),
            ('cancelled', _('Annulée')),
            ('completed', _('Terminée')),
            ('rejected', _('Refusée'))
        ],
        default='pending',
        verbose_name=_("Statut")
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True,
        blank=True,
        verbose_name=_("Prix total")
    )
    deposit_paid = models.BooleanField(default=False, verbose_name=_("Acompte payé"))
    full_payment_paid = models.BooleanField(default=False, verbose_name=_("Paiement complet"))
    special_requirements = models.TextField(blank=True, verbose_name=_("Exigences spéciales"))
    admin_notes = models.TextField(blank=True, verbose_name=_("Notes administrateur"))
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_bookings',
        verbose_name=_("Confirmé par")
    )
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de confirmation"))
    
    class Meta:
        verbose_name = _("Réservation de salle")
        verbose_name_plural = _("Réservations de salle")
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['room', 'start_time', 'end_time']),
            models.Index(fields=['status', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.event_title} - {self.room.name} ({self.start_time.date()})"
    
    def save(self, *args, **kwargs):
        # Calculer le prix total si pas déjà défini
        if not self.total_price:
            from decimal import Decimal
            duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
            if duration_hours <= 8:  # Moins d'une journée
                self.total_price = self.room.price_per_hour * Decimal(str(duration_hours))
            else:  # Plus d'une journée
                days = (self.end_time - self.start_time).days + 1
                self.total_price = self.room.price_per_day * Decimal(str(days))
        
        # Marquer comme confirmé si le statut change
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def duration_hours(self):
        """Durée en heures"""
        return (self.end_time - self.start_time).total_seconds() / 3600
    
    @property
    def duration_days(self):
        """Durée en jours"""
        return (self.end_time - self.start_time).days + 1
    
    @property
    def is_confirmed(self):
        """Vérifie si la réservation est confirmée"""
        return self.status == 'confirmed'
    
    @property
    def is_pending(self):
        """Vérifie si la réservation est en attente"""
        return self.status == 'pending'
    
    @property
    def is_cancelled(self):
        """Vérifie si la réservation est annulée"""
        return self.status == 'cancelled'
    
    @property
    def is_completed(self):
        """Vérifie si la réservation est terminée"""
        return self.status == 'completed'
    
    def check_conflicts(self):
        """Vérifie s'il y a des conflits avec d'autres réservations"""
        conflicting_bookings = RoomBooking.objects.filter(
            room=self.room,
            status__in=['confirmed', 'pending'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        return conflicting_bookings.exists()
    
    def get_conflicts_report(self):
        """Génère un rapport détaillé des conflits"""
        from django.utils import timezone
        from datetime import timezone as dt_timezone
        
        # S'assurer que les dates ont le bon fuseau horaire
        start_time = self.start_time
        end_time = self.end_time
        
        # Si les dates n'ont pas de fuseau horaire, les traiter comme UTC
        if start_time and timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, dt_timezone.utc)
        if end_time and timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time, dt_timezone.utc)
        
        if not self.pk:  # Nouvelle réservation
            conflicting_bookings = RoomBooking.objects.filter(
                room=self.room,
                status__in=['confirmed', 'pending'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
        else:
            conflicting_bookings = RoomBooking.objects.filter(
                room=self.room,
                status__in=['confirmed', 'pending'],
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(pk=self.pk)
        
        conflicts = []
        for booking in conflicting_bookings:
            try:
                # Calculer la période de chevauchement
                overlap_start = max(start_time, booking.start_time)
                overlap_end = min(end_time, booking.end_time)
                overlap_duration = (overlap_end - overlap_start).total_seconds() / 3600
                
                conflicts.append({
                    'booking': booking,
                    'overlap_start': overlap_start,
                    'overlap_end': overlap_end,
                    'overlap_hours': round(overlap_duration, 2),
                    'overlap_days': round(overlap_duration / 24, 2),
                    'conflict_type': 'overlap',
                    'conflicting_event': booking.event_title,
                    'conflicting_organization': booking.organization.name if booking.organization else 'N/A'
                })
            except Exception as e:
                # En cas d'erreur de calcul, ajouter un conflit générique
                conflicts.append({
                    'booking': booking,
                    'overlap_start': None,
                    'overlap_end': None,
                    'overlap_hours': 0,
                    'overlap_days': 0,
                    'conflict_type': 'error',
                    'error_message': str(e),
                    'conflicting_event': booking.event_title,
                    'conflicting_organization': booking.organization.name if booking.organization else 'N/A'
                })
        
        return conflicts
    
    def get_duration_info(self):
        """Retourne les informations de durée formatées"""
        duration = self.end_time - self.start_time
        total_hours = duration.total_seconds() / 3600
        total_days = duration.days + (duration.seconds / 86400)
        
        if total_hours < 24:
            return f"{total_hours:.1f} heures"
        else:
            return f"{total_days:.1f} jours ({total_hours:.1f} heures)"
    
    def get_detailed_conflicts_summary(self):
        """Résumé détaillé des conflits pour l'affichage"""
        conflicts = self.get_conflicts_report()
        
        if not conflicts:
            return {
                'has_conflicts': False,
                'message': '✅ Aucun conflit détecté. La réservation peut être confirmée.',
                'conflicts_count': 0,
                'total_overlap_hours': 0,
                'total_overlap_days': 0,
                'details': []
            }
        
        # Calculer les totaux en ignorant les erreurs
        valid_conflicts = [c for c in conflicts if c['conflict_type'] != 'error']
        total_overlap_hours = sum(c['overlap_hours'] for c in valid_conflicts)
        total_overlap_days = sum(c['overlap_days'] for c in valid_conflicts)
        
        # Créer des détails lisibles pour chaque conflit
        conflict_details = []
        for conflict in conflicts:
            if conflict['conflict_type'] == 'overlap':
                detail = f"• {conflict['conflicting_event']} ({conflict['conflicting_organization']}) - "
                detail += f"Conflit de {conflict['overlap_hours']} heures ({conflict['overlap_days']:.1f} jours)"
                conflict_details.append(detail)
            elif conflict['conflict_type'] == 'error':
                detail = f"• {conflict['conflicting_event']} ({conflict['conflicting_organization']}) - "
                detail += f"Erreur de calcul: {conflict.get('error_message', 'Erreur inconnue')}"
                conflict_details.append(detail)
        
        # Message principal
        if len(conflicts) == 1:
            message = f"⚠️ Conflit détecté avec 1 réservation existante"
        else:
            message = f"⚠️ Conflits détectés avec {len(conflicts)} réservations existantes"
        
        if total_overlap_hours > 0:
            message += f" - Chevauchement total: {total_overlap_hours:.1f} heures"
        
        return {
            'has_conflicts': True,
            'message': message,
            'conflicts_count': len(conflicts),
            'total_overlap_hours': total_overlap_hours,
            'total_overlap_days': total_overlap_days,
            'conflicts': conflicts,
            'details': conflict_details
        }


class BookingPayment(TimeStampedModel):
    """Paiement pour une réservation"""
    booking = models.ForeignKey(
        RoomBooking, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name=_("Réservation")
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Montant")
    )
    payment_type = models.CharField(
        max_length=20,
        choices=[
            ('deposit', _('Acompte')),
            ('full_payment', _('Paiement complet')),
            ('partial', _('Paiement partiel')),
            ('refund', _('Remboursement'))
        ],
        verbose_name=_("Type de paiement")
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('bank_transfer', _('Virement bancaire')),
            ('check', _('Chèque')),
            ('cash', _('Espèces')),
            ('credit_card', _('Carte de crédit')),
            ('other', _('Autre'))
        ],
        verbose_name=_("Méthode de paiement")
    )
    reference = models.CharField(max_length=100, blank=True, verbose_name=_("Référence"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Vérifié"))
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Vérifié par")
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de vérification"))
    
    class Meta:
        verbose_name = _("Paiement de réservation")
        verbose_name_plural = _("Paiements de réservation")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.booking.event_title}"


class RoomMaintenance(TimeStampedModel):
    """Maintenance d'une salle"""
    room = models.ForeignKey(
        ConferenceRoom, 
        on_delete=models.CASCADE, 
        related_name='maintenance_records',
        verbose_name=_("Salle")
    )
    title = models.CharField(max_length=200, verbose_name=_("Titre de la maintenance"))
    description = models.TextField(verbose_name=_("Description"))
    start_date = models.DateTimeField(verbose_name=_("Date de début"))
    end_date = models.DateTimeField(verbose_name=_("Date de fin"))
    maintenance_type = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', _('Planifiée')),
            ('emergency', _('Urgente')),
            ('preventive', _('Préventive')),
            ('corrective', _('Corrective'))
        ],
        verbose_name=_("Type de maintenance")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', _('Planifiée')),
            ('in_progress', _('En cours')),
            ('completed', _('Terminée')),
            ('cancelled', _('Annulée'))
        ],
        default='planned',
        verbose_name=_("Statut")
    )
    estimated_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("Coût estimé")
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', _('Faible')),
            ('medium', _('Moyenne')),
            ('high', _('Élevée'))
        ],
        default='medium',
        verbose_name=_("Priorité")
    )
    technician = models.CharField(max_length=100, blank=True, verbose_name=_("Technicien"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    
    class Meta:
        verbose_name = _("Maintenance de salle")
        verbose_name_plural = _("Maintenances de salle")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} - {self.room.name}"
    
    @property
    def is_active(self):
        """Vérifie si la maintenance est active"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.status == 'in_progress'
    
    @property
    def duration_hours(self):
        """Calcule la durée en heures"""
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return duration.total_seconds() / 3600
        return 0
    
    @property
    def duration_days(self):
        """Calcule la durée en jours"""
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return duration.days
        return 0
        




class Personna(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name=_("Nom"))
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name=_("Slug"))
    description = models.TextField(verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))

    class Meta:
        verbose_name = _("Personna")
        verbose_name_plural = _("Personnas")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Vérifier si le slug existe déjà
            counter = 1
            original_slug = self.slug
            while Personna.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def blogs_count(self):
        return self.blogs.count()


class Blog(TimeStampedModel):
    """Blog associé à un personna"""
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('published', _('Publié')),
        ('archived', _('Archivé'))
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("Titre"))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_("Slug"))
    content = CKEditor5Field(verbose_name=_("Contenu"), config_name='blog_content')
    excerpt = models.TextField(max_length=300, blank=True, verbose_name=_("Extrait court"), 
                              help_text=_("Résumé court du blog (max 300 caractères). Si vide, sera généré automatiquement depuis le contenu."))
    image = models.ImageField(
        upload_to='blogs/images/',
        null=True,
        blank=True,
        verbose_name=_("Image principale")
    )
    video_url = models.URLField(blank=True, verbose_name=_("URL de la vidéo"))
    personna = models.ForeignKey(
        Personna,
        on_delete=models.CASCADE,
        related_name='blogs',
        verbose_name=_("Personna")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Statut")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"))
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de publication")
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de vues"))
    
    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Génération automatique du slug
        if not self.slug:
            self.slug = slugify(self.title)
            # Vérifier si le slug existe déjà
            counter = 1
            original_slug = self.slug
            while Blog.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Génération automatique de l'extrait si vide
        if not self.excerpt and self.content:
            # Nettoyer le HTML et prendre les premiers caractères
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = clean_content[:300].strip()
            if len(clean_content) > 300:
                self.excerpt += "..."
        
        # Si le statut passe à publié et qu'il n'y a pas de date de publication
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def reading_time(self):
        """Calcule le temps de lecture estimé"""
        import re
        clean_content = re.sub(r'<[^>]+>', '', self.content)
        words = len(clean_content.split())
        minutes = words // 200  # 200 mots par minute
        return max(1, minutes)
        




class CityDistrict(TimeStampedModel):
    """Quartier de la cité des sciences"""
    
    name = models.CharField(max_length=200, verbose_name=_("Nom du quartier"))
    description = models.TextField(verbose_name=_("Description du quartier"))
    icon = models.CharField(max_length=100, verbose_name=_("Icône FontAwesome"), 
                          help_text=_("Ex: fas fa-building, fas fa-flask, fas fa-microscope"))
    image = models.ImageField(upload_to='city_districts/', verbose_name=_("Image du quartier"), blank=True, null=True)
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_active = models.BooleanField(default=True, verbose_name=_("Quartier actif"))
    
    class Meta:
        verbose_name = _("Quartier de la cité")
        verbose_name_plural = _("Quartiers de la cité")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CoreValue(TimeStampedModel):
    """Valeur fondamentale de la CSIG"""
    
    icon = models.CharField(max_length=100, verbose_name=_("Icône FontAwesome"), 
                          help_text=_("Ex: fas fa-lightbulb, fas fa-heart, fas fa-star"))
    name = models.CharField(max_length=200, verbose_name=_("Nom de la valeur"))
    description = models.TextField(verbose_name=_("Description de la valeur"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_active = models.BooleanField(default=True, verbose_name=_("Valeur active"))
    
    class Meta:
        verbose_name = _("Valeur fondamentale")
        verbose_name_plural = _("Valeurs fondamentales")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class AboutPage(TimeStampedModel):
    """Page À propos - Contenu dynamique"""
    
    # Informations principales
    hero_title = models.CharField(max_length=200, verbose_name=_("Titre principal"))
    hero_subtitle = models.TextField(verbose_name=_("Sous-titre principal"))
    hero_background = models.ImageField(upload_to='about/hero/', verbose_name=_("Image de fond hero"))
    
    # Notre Histoire
    history_title = models.CharField(max_length=200, default="Notre Histoire", verbose_name=_("Titre de l'histoire"))
    history_content = CKEditor5Field(verbose_name=_("Contenu de l'histoire"))
    
    # Quartiers de la cité (remplace timeline)
    districts_title = models.CharField(max_length=200, default="Les Quartiers de la Cité", verbose_name=_("Titre des quartiers"))
    districts_subtitle = models.TextField(default="Découvrez les différents espaces de notre cité des sciences", verbose_name=_("Sous-titre des quartiers"))
    
    # CTA Section
    cta_title = models.CharField(max_length=200, default="Rejoignez la Révolution Scientifique", verbose_name=_("Titre CTA"))
    cta_content = models.TextField(verbose_name=_("Contenu de la section CTA"))
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name=_("Page active"))
    show_districts = models.BooleanField(default=True, verbose_name=_("Afficher les quartiers"))
    
    class Meta:
        verbose_name = _("Page À propos")
        verbose_name_plural = _("Pages À propos")
    
    def __str__(self):
        return "Page À propos"
    
    @classmethod
    def get_active_page(cls):
        """Retourne la page active ou crée une page par défaut"""
        page = cls.objects.filter(is_active=True).first()
        if not page:
            page = cls.objects.create(
                hero_title="À propos de la CSIG",
                hero_subtitle="La Cité des Sciences et de l'Innovation de Guinée est un centre d'excellence dédié au développement scientifique, technologique et innovant de notre nation.",
                history_content="Fondée en 2020, la CSIG est née de la vision ambitieuse de créer un écosystème d'innovation au cœur de l'Afrique de l'Ouest. Notre mission est de transformer la Guinée en un hub technologique reconnu internationalement.",
                cta_content="Découvrez nos programmes, participez à nos événements ou devenez partenaire de la CSIG pour contribuer au développement scientifique de la Guinée."
            )
        return page


class HeroStatistic(TimeStampedModel):
    """Statistique de la section hero"""
    
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='hero_statistics')
    number = models.CharField(max_length=50, verbose_name=_("Nombre/Chiffre"))
    label = models.CharField(max_length=200, verbose_name=_("Libellé"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_active = models.BooleanField(default=True, verbose_name=_("Statistique active"))
    
    class Meta:
        verbose_name = _("Statistique hero")
        verbose_name_plural = _("Statistiques hero")
        ordering = ['order', 'number']
    
    def __str__(self):
        return f"{self.number} - {self.label}"


class Achievement(TimeStampedModel):
    """Réalisation de la CSIG"""
    
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='achievements')
    icon = models.CharField(max_length=100, verbose_name=_("Icône FontAwesome"), 
                          help_text=_("Ex: fas fa-trophy, fas fa-medal, fas fa-star"))
    text = models.TextField(verbose_name=_("Description de la réalisation"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre d'affichage"))
    is_active = models.BooleanField(default=True, verbose_name=_("Réalisation active"))
    
    class Meta:
        verbose_name = _("Réalisation")
        verbose_name_plural = _("Réalisations")
        ordering = ['order', 'text']
    
    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text





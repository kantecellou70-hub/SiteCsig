from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NewsletterLog(models.Model):
    """
    Modèle pour tracer les envois de newsletters
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sending', 'En cours d\'envoi'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
        ('bounced', 'Retourné'),
        ('opened', 'Ouvert'),
        ('clicked', 'Cliqué'),
    ]
    
    campaign = models.ForeignKey(
        'content_management.NewsletterCampaign',
        on_delete=models.CASCADE,
        related_name='logs'
    )
    subscriber = models.ForeignKey(
        'content_management.Newsletter',
        on_delete=models.CASCADE,
        related_name='logs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Log de newsletter"
        verbose_name_plural = "Logs de newsletters"
        unique_together = ['campaign', 'subscriber']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['subscriber', 'status']),
        ]
    
    def __str__(self):
        return f"{self.campaign.title} - {self.subscriber.email} ({self.get_status_display()})"
    
    def mark_as_sent(self):
        """Marque le log comme envoyé"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message=""):
        """Marque le log comme échoué"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()
    
    def mark_as_opened(self):
        """Marque le log comme ouvert"""
        if not self.opened_at:
            self.status = 'opened'
            self.opened_at = timezone.now()
            self.save()
    
    def mark_as_clicked(self):
        """Marque le log comme cliqué"""
        if not self.clicked_at:
            self.status = 'clicked'
            self.clicked_at = timezone.now()
            self.save()

class EmailTemplate(models.Model):
    """
    Modèle pour gérer les templates d'emails
    """
    name = models.CharField(max_length=100, unique=True)
    subject_template = models.CharField(max_length=200)
    html_template = models.TextField()
    text_template = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template d'email"
        verbose_name_plural = "Templates d'emails"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_subject(self, context):
        """Rend le template de sujet avec le contexte"""
        from django.template import Template, Context
        template = Template(self.subject_template)
        return template.render(Context(context))
    
    def get_html_content(self, context):
        """Rend le template HTML avec le contexte"""
        from django.template import Template, Context
        template = Template(self.html_template)
        return template.render(Context(context))
    
    def get_text_content(self, context):
        """Rend le template texte avec le contexte"""
        if not self.text_template:
            return ""
        from django.template import Template, Context
        template = Template(self.text_template)
        return template.render(Context(context))

class EmailQueue(models.Model):
    """
    Modèle pour gérer la file d'attente des emails
    """
    PRIORITY_CHOICES = [
        (1, 'Basse'),
        (2, 'Normale'),
        (3, 'Haute'),
        (4, 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    to_email = models.EmailField()
    from_email = models.EmailField()
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email en file d'attente"
        verbose_name_plural = "Emails en file d'attente"
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'scheduled_at']),
            models.Index(fields=['to_email', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.get_status_display()})"
    
    def can_be_sent(self):
        """Vérifie si l'email peut être envoyé"""
        if self.status != 'pending':
            return False
        
        if self.scheduled_at and self.scheduled_at > timezone.now():
            return False
        
        if self.retry_count >= self.max_retries:
            return False
        
        return True
    
    def mark_as_processing(self):
        """Marque l'email comme en cours de traitement"""
        self.status = 'processing'
        self.save()
    
    def mark_as_sent(self):
        """Marque l'email comme envoyé"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message=""):
        """Marque l'email comme échoué"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()
    
    def retry(self):
        """Remet l'email en file d'attente pour un nouvel essai"""
        if self.retry_count < self.max_retries:
            self.status = 'pending'
            self.error_message = ""
            self.save()
            return True
        return False

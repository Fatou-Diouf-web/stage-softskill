from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Coach(models.Model):
    """Modèle pour les coachs"""
    
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='coach_profile',
        verbose_name=_('utilisateur')
    )
    specialization = models.CharField(_('spécialisation'), max_length=200)
    experience_years = models.PositiveIntegerField(_('années d\'expérience'))
    bio = models.TextField(_('biographie'))
    hourly_rate = models.DecimalField(
        _('tarif horaire'),
        max_digits=10,
        decimal_places=2
    )
    is_available = models.BooleanField(_('disponible'), default=True)
    rating = models.DecimalField(
        _('note moyenne'),
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('coach')
        verbose_name_plural = _('coachs')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"


class CoachingSession(models.Model):
    """Session de coaching"""
    
    SESSION_TYPES = [
        ('individual', 'Individuel'),
        ('group', 'Groupe'),
        ('assessment', 'Évaluation'),
        ('follow_up', 'Suivi'),
    ]
    
    SESSION_STATUS = [
        ('scheduled', 'Programmée'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    client = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='coaching_sessions',
        verbose_name=_('client')
    )
    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('coach')
    )
    
    # Session details
    session_type = models.CharField(
        _('type de session'),
        max_length=20,
        choices=SESSION_TYPES,
        default='individual'
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField(_('programmée le'))
    duration_minutes = models.PositiveIntegerField(
        _('durée en minutes'),
        default=60
    )
    
    # Status and tracking
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=SESSION_STATUS,
        default='scheduled'
    )
    meeting_link = models.URLField(_('lien de réunion'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Payment
    price = models.DecimalField(
        _('prix'),
        max_digits=10,
        decimal_places=2
    )
    is_paid = models.BooleanField(_('payé'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('session de coaching')
        verbose_name_plural = _('sessions de coaching')
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.coach.user.get_full_name()} - {self.title}"


class SessionFeedback(models.Model):
    """Retour d'expérience sur une session"""
    
    session = models.OneToOneField(
        CoachingSession,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name=_('session')
    )
    client_rating = models.PositiveIntegerField(
        _('note du client'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    client_comment = models.TextField(_('commentaire du client'), blank=True)
    coach_rating = models.PositiveIntegerField(
        _('note du coach'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    coach_comment = models.TextField(_('commentaire du coach'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('retour d\'expérience')
        verbose_name_plural = _('retours d\'expérience')
    
    def __str__(self):
        return f"Feedback - {self.session.title}"

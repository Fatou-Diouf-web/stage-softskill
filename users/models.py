from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé"""
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    is_subscribed = models.BooleanField(_('abonné'), default=False)
    subscription_end_date = models.DateTimeField(
        _('date de fin d\'abonnement'),
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.email or self.username

    class Meta:
        db_table = 'users_customuser'
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    @property
    def is_active_subscriber(self):
        """Vérifie si l'utilisateur a un abonnement actif"""
        if not self.is_subscribed:
            return False
        if not self.subscription_end_date:
            return False
        from django.utils import timezone
        return timezone.now() <= self.subscription_end_date


class Profile(models.Model):
    """Profil utilisateur étendu"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.jpg',
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f'Profil de {self.user.username}'


class UserProgress(models.Model):
    """Suivi des progrès de l'utilisateur"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    completed_lessons = models.ManyToManyField(
        'courses.Lesson',
        blank=True,
        related_name='completed_by'
    )
    progress_percentage = models.DecimalField(
        _('pourcentage de progression'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    started_at = models.DateTimeField(_('commencé le'), auto_now_add=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('progression utilisateur')
        verbose_name_plural = _('progressions utilisateur')
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"
    
    def update_progress(self):
        """Met à jour le pourcentage de progression"""
        total_lessons = self.course.lessons.count()
        if total_lessons > 0:
            completed_count = self.completed_lessons.count()
            self.progress_percentage = (completed_count / total_lessons) * 100
            self.save()
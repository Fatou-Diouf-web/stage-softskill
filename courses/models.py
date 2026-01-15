from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Category(models.Model):
    """Catégorie de formation (soft skills)"""
    
    name = models.CharField(_('nom'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    color = models.CharField(_('couleur'), max_length=7, default='#007bff')
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('catégorie')
        verbose_name_plural = _('catégories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Formation en soft skills"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    ]
    
    title = models.CharField(_('titre'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('description'))
    short_description = models.CharField(_('description courte'), max_length=300)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name=_('catégorie')
    )
    instructor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='courses_taught',
        verbose_name=_('formateur'),
        limit_choices_to={'user_type': 'coach'}
    )
    
    # Course details
    difficulty_level = models.CharField(
        _('niveau de difficulté'),
        max_length=20,
        choices=DIFFICULTY_LEVELS,
        default='beginner'
    )
    duration_hours = models.PositiveIntegerField(_('durée en heures'))
    price = models.DecimalField(
        _('prix'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    is_free = models.BooleanField(_('gratuit'), default=False)
    
    # Course content
    thumbnail = models.ImageField(
        _('miniature'),
        upload_to='course_thumbnails/',
        blank=True,
        null=True
    )
    video_intro = models.URLField(_('vidéo d\'introduction'), blank=True)
    objectives = models.TextField(_('objectifs d\'apprentissage'))
    prerequisites = models.TextField(_('prérequis'), blank=True)
    target_audience = models.TextField(_('public cible'))
    
    # Course status
    is_published = models.BooleanField(_('publié'), default=False)
    is_featured = models.BooleanField(_('mis en avant'), default=False)
    enrollment_count = models.PositiveIntegerField(_('nombre d\'inscriptions'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    published_at = models.DateTimeField(_('publié le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('formation')
        verbose_name_plural = _('formations')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def total_lessons(self):
        return self.lessons.count()
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0


class Lesson(models.Model):
    """Leçon d'une formation"""
    
    LESSON_TYPES = [
        ('video', 'Vidéo'),
        ('text', 'Texte'),
        ('quiz', 'Quiz'),
        ('exercise', 'Exercice'),
        ('webinar', 'Webinaire'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('formation')
    )
    title = models.CharField(_('titre'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    lesson_type = models.CharField(
        _('type de leçon'),
        max_length=20,
        choices=LESSON_TYPES,
        default='video'
    )
    
    # Content
    content = models.TextField(_('contenu'), blank=True)
    video_url = models.URLField(_('URL vidéo'), blank=True)
    duration_minutes = models.PositiveIntegerField(_('durée en minutes'), default=0)
    
    # Files
    attachment = models.FileField(
        _('fichier joint'),
        upload_to='lesson_attachments/',
        blank=True,
        null=True
    )
    
    # Ordering
    order = models.PositiveIntegerField(_('ordre'), default=0)
    
    # Status
    is_active = models.BooleanField(_('actif'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('leçon')
        verbose_name_plural = _('leçons')
        ordering = ['course', 'order']
        unique_together = ['course', 'slug']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseEnrollment(models.Model):
    """Inscription à une formation"""
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('utilisateur')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('formation')
    )
    enrolled_at = models.DateTimeField(_('inscrit le'), auto_now_add=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    payment_status = models.CharField(
        _('statut du paiement'),
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('completed', 'Terminé'),
            ('failed', 'Échoué'),
            ('refunded', 'Remboursé'),
        ],
        default='pending'
    )
    progress_percentage = models.DecimalField(
        _('pourcentage de progression'),
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    class Meta:
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"


class CourseRating(models.Model):
    """Évaluation d'une formation"""
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='course_ratings',
        verbose_name=_('utilisateur')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('formation')
    )
    rating = models.PositiveIntegerField(
        _('note'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(_('avis'), blank=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('évaluation')
        verbose_name_plural = _('évaluations')
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title} - {self.rating}/5"

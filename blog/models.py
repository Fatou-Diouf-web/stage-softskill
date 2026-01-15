from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse


class BlogCategory(models.Model):
    """Catégorie d'articles du blog"""
    
    name = models.CharField(_('nom'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(_('couleur'), max_length=7, default='#007bff')
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('catégorie blog')
        verbose_name_plural = _('catégories blog')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """Article du blog"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    title = models.CharField(_('titre'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    excerpt = models.TextField(_('extrait'), max_length=300, blank=True)
    content = models.TextField(_('contenu'))
    
    # Author and category
    author = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name=_('auteur')
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('catégorie')
    )
    
    # SEO and content
    meta_description = models.CharField(_('description meta'), max_length=160, blank=True)
    meta_keywords = models.CharField(_('mots-clés meta'), max_length=200, blank=True)
    featured_image = models.ImageField(
        _('image à la une'),
        upload_to='blog_images/',
        blank=True,
        null=True
    )
    
    # Status and visibility
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(_('mis en avant'), default=False)
    allow_comments = models.BooleanField(_('autoriser les commentaires'), default=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(_('nombre de vues'), default=0)
    read_time_minutes = models.PositiveIntegerField(_('temps de lecture en minutes'), default=5)
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    published_at = models.DateTimeField(_('publié le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()


class BlogComment(models.Model):
    """Commentaire sur un article"""
    
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('article')
    )
    author = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name=_('auteur')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('commentaire parent')
    )
    
    content = models.TextField(_('contenu'))
    is_approved = models.BooleanField(_('approuvé'), default=False)
    is_spam = models.BooleanField(_('spam'), default=False)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('commentaire')
        verbose_name_plural = _('commentaires')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Commentaire de {self.author.get_full_name()} sur {self.post.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class BlogTag(models.Model):
    """Tags pour les articles"""
    
    name = models.CharField(_('nom'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    posts = models.ManyToManyField(
        BlogPost,
        related_name='tags',
        verbose_name=_('articles')
    )
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class Newsletter(models.Model):
    """Newsletter pour les abonnés"""
    
    title = models.CharField(_('titre'), max_length=200)
    subject = models.CharField(_('sujet'), max_length=200)
    content = models.TextField(_('contenu'))
    
    # Status
    is_sent = models.BooleanField(_('envoyé'), default=False)
    sent_at = models.DateTimeField(_('envoyé le'), null=True, blank=True)
    
    # Statistics
    sent_count = models.PositiveIntegerField(_('nombre d\'envois'), default=0)
    opened_count = models.PositiveIntegerField(_('nombre d\'ouvertures'), default=0)
    clicked_count = models.PositiveIntegerField(_('nombre de clics'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NewsletterSubscriber(models.Model):
    """Abonné à la newsletter"""
    
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('prénom'), max_length=100, blank=True)
    last_name = models.CharField(_('nom'), max_length=100, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    subscribed_at = models.DateTimeField(_('abonné le'), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_('désabonné le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('abonné newsletter')
        verbose_name_plural = _('abonnés newsletter')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email

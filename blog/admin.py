from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import BlogCategory, BlogPost, BlogComment, BlogTag, Newsletter, NewsletterSubscriber


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Interface d'administration pour les catégories du blog"""
    
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class BlogCommentInline(admin.TabularInline):
    """Inline pour les commentaires dans les articles"""
    model = BlogComment
    extra = 0
    readonly_fields = ['author', 'content', 'created_at']
    fields = ['author', 'content', 'is_approved', 'is_spam', 'created_at']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Interface d'administration pour les articles du blog"""
    
    list_display = [
        'title', 'author', 'category', 'status', 
        'is_featured', 'view_count', 'published_at'
    ]
    list_filter = [
        'status', 'category', 'is_featured', 
        'allow_comments', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'view_count', 'comment_count', 'created_at', 
        'updated_at', 'published_at'
    ]
    list_editable = ['status', 'is_featured']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        (_('Auteur et catégorie'), {
            'fields': ('author', 'category')
        }),
        (_('SEO et contenu'), {
            'fields': (
                'meta_description', 'meta_keywords', 'featured_image',
                'read_time_minutes'
            )
        }),
        (_('Statut et visibilité'), {
            'fields': ('status', 'is_featured', 'allow_comments')
        }),
        (_('Statistiques'), {
            'fields': ('view_count', 'comment_count'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BlogCommentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    """Interface d'administration pour les commentaires"""
    
    list_display = [
        'author', 'post', 'is_approved', 'is_spam', 
        'is_reply', 'created_at'
    ]
    list_filter = ['is_approved', 'is_spam', 'created_at']
    search_fields = [
        'author__email', 'author__first_name', 'author__last_name',
        'post__title', 'content'
    ]
    list_editable = ['is_approved', 'is_spam']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('post', 'author', 'parent', 'content')
        }),
        (_('Modération'), {
            'fields': ('is_approved', 'is_spam')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post')


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    """Interface d'administration pour les tags"""
    
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['posts']
    ordering = ['name']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Interface d'administration pour les newsletters"""
    
    list_display = [
        'title', 'subject', 'is_sent', 'sent_count',
        'opened_count', 'clicked_count', 'created_at'
    ]
    list_filter = ['is_sent', 'created_at']
    search_fields = ['title', 'subject', 'content']
    readonly_fields = [
        'sent_count', 'opened_count', 'clicked_count',
        'sent_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'subject', 'content')
        }),
        (_('Statut'), {
            'fields': ('is_sent', 'sent_at')
        }),
        (_('Statistiques'), {
            'fields': ('sent_count', 'opened_count', 'clicked_count'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """Interface d'administration pour les abonnés à la newsletter"""
    
    list_display = [
        'email', 'first_name', 'last_name', 'is_active',
        'subscribed_at', 'unsubscribed_at'
    ]
    list_filter = ['is_active', 'subscribed_at', 'unsubscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    list_editable = ['is_active']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name')
        }),
        (_('Statut'), {
            'fields': ('is_active', 'subscribed_at', 'unsubscribed_at')
        }),
    )

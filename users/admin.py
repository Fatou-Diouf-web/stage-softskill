from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProgress


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Interface d'administration pour les utilisateurs personnalisés"""
    
    list_display = [
        'email', 
        'first_name', 
        'last_name', 
        'is_subscribed', 
        'is_active', 
        'date_joined'
    ]
    
    list_filter = [
        'is_subscribed', 
        'is_active', 
        'is_staff', 
        'date_joined'
    ]
    
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {
            'fields': (
                'first_name', 
                'last_name', 
                'phone',
                'profile_picture',
                'bio'
            )
        }),
        ('Abonnement', {
            'fields': (
                'is_subscribed',
                'subscription_end_date'
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """Interface d'administration pour les progrès utilisateur"""
    
    list_display = [
        'user', 'course', 'progress_percentage', 
        'started_at', 'completed_at'
    ]
    list_filter = ['course', 'started_at', 'completed_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'course__title']
    readonly_fields = ['started_at', 'progress_percentage']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'course')
        }),
        (_('Progression'), {
            'fields': (
                'completed_lessons', 'progress_percentage',
                'started_at', 'completed_at'
            )
        }),
    )
    
    filter_horizontal = ['completed_lessons']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')

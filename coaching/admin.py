from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Coach, CoachingSession, SessionFeedback


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    """Interface d'administration pour les coachs"""
    
    list_display = [
        'user', 'specialization', 'experience_years', 
        'hourly_rate', 'rating', 'is_available'
    ]
    list_filter = ['is_available', 'experience_years', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'specialization'
    ]
    readonly_fields = ['rating', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'specialization', 'experience_years')
        }),
        (_('Informations professionnelles'), {
            'fields': ('bio', 'hourly_rate', 'rating')
        }),
        (_('Statut'), {
            'fields': ('is_available',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CoachingSession)
class CoachingSessionAdmin(admin.ModelAdmin):
    """Interface d'administration pour les sessions de coaching"""
    
    list_display = [
        'client', 'coach', 'session_type', 'title',
        'scheduled_at', 'status', 'is_paid'
    ]
    list_filter = [
        'session_type', 'status', 'is_paid', 
        'scheduled_at', 'created_at'
    ]
    search_fields = [
        'client__email', 'client__first_name', 'client__last_name',
        'coach__user__email', 'coach__user__first_name', 'title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'is_paid']
    
    fieldsets = (
        (None, {
            'fields': ('client', 'coach', 'session_type', 'title', 'description')
        }),
        (_('Planification'), {
            'fields': ('scheduled_at', 'duration_minutes')
        }),
        (_('Statut et suivi'), {
            'fields': ('status', 'meeting_link', 'notes')
        }),
        (_('Paiement'), {
            'fields': ('price', 'is_paid')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client', 'coach__user'
        )


@admin.register(SessionFeedback)
class SessionFeedbackAdmin(admin.ModelAdmin):
    """Interface d'administration pour les retours d'expérience"""
    
    list_display = [
        'session', 'client_rating', 'coach_rating',
        'created_at'
    ]
    list_filter = ['client_rating', 'coach_rating', 'created_at']
    search_fields = [
        'session__client__email', 'session__coach__user__email',
        'session__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('session',)
        }),
        (_('Évaluation client'), {
            'fields': ('client_rating', 'client_comment')
        }),
        (_('Évaluation coach'), {
            'fields': ('coach_rating', 'coach_comment')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'session__client', 'session__coach__user'
        )

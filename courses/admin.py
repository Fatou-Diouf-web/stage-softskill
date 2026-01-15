from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Course, Lesson, CourseEnrollment, CourseRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Interface d'administration pour les catégories"""
    
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class LessonInline(admin.TabularInline):
    """Inline pour les leçons dans les cours"""
    model = Lesson
    extra = 1
    fields = ['title', 'lesson_type', 'duration_minutes', 'order', 'is_active']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Interface d'administration pour les cours"""
    
    list_display = [
        'title', 'category', 'instructor', 'difficulty_level',
        'price', 'is_published', 'is_featured', 'enrollment_count'
    ]
    list_filter = [
        'category', 'difficulty_level', 'is_published', 
        'is_featured', 'is_free', 'created_at'
    ]
    search_fields = ['title', 'description', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['enrollment_count', 'created_at', 'updated_at', 'published_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        (_('Catégorisation'), {
            'fields': ('category', 'instructor', 'difficulty_level')
        }),
        (_('Contenu'), {
            'fields': (
                'thumbnail', 'video_intro', 'objectives',
                'prerequisites', 'target_audience'
            )
        }),
        (_('Prix et accès'), {
            'fields': ('price', 'is_free')
        }),
        (_('Statut'), {
            'fields': (
                'is_published', 'is_featured', 'enrollment_count'
            )
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [LessonInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'instructor')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Interface d'administration pour les leçons"""
    
    list_display = [
        'title', 'course', 'lesson_type', 'duration_minutes',
        'order', 'is_active'
    ]
    list_filter = ['course', 'lesson_type', 'is_active', 'created_at']
    search_fields = ['title', 'course__title']
    list_editable = ['order', 'is_active']
    ordering = ['course', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        (_('Type et contenu'), {
            'fields': ('lesson_type', 'content', 'video_url', 'duration_minutes')
        }),
        (_('Fichiers'), {
            'fields': ('attachment',)
        }),
        (_('Organisation'), {
            'fields': ('order', 'is_active')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Interface d'administration pour les inscriptions"""
    
    list_display = [
        'user', 'course', 'progress_percentage', 
        'enrolled_at', 'completed_at'
    ]
    list_filter = ['course', 'enrolled_at', 'completed_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'course__title'
    ]
    readonly_fields = ['enrolled_at', 'progress_percentage']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'course')
        }),
        (_('Progression'), {
            'fields': ('progress_percentage', 'enrolled_at', 'completed_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    """Interface d'administration pour les évaluations"""
    
    list_display = [
        'user', 'course', 'rating', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'course__title', 'review'
    ]
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'course', 'rating', 'review')
        }),
        (_('Dates'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')

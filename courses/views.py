from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Course, Category, Lesson, CourseEnrollment, CourseRating
from users.models import CustomUser


def home(request):
    """Page d'accueil"""
    featured_courses = Course.objects.filter(
        is_published=True, 
        is_featured=True
    )[:6]
    
    latest_courses = Course.objects.filter(
        is_published=True
    ).order_by('-created_at')[:6]
    
    popular_categories = Category.objects.filter(
        is_active=True,
        courses__is_published=True
    ).distinct()[:6]
    
    # Statistiques
    total_students = CourseEnrollment.objects.count()
    total_courses = Course.objects.filter(is_published=True).count()
    total_certificates = CourseEnrollment.objects.filter(completed_at__isnull=False).count()
    
    context = {
        'featured_courses': featured_courses,
        'latest_courses': latest_courses,
        'popular_categories': popular_categories,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_certificates': total_certificates,
    }
    return render(request, 'courses/home.html', context)


def course_list(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')
    
    if selected_category:
        courses = courses.filter(category__slug=selected_category)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'courses/course_list.html', context)
def course_detail(request, slug):
    """Détail d'une formation"""
    course = get_object_or_404(Course, slug=slug, is_published=True)

    # Vérifier si l'utilisateur est inscrit
    is_enrolled = False
    user_progress = None
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(
            user=request.user, 
            course=course
        ).exists()
        if is_enrolled:
            user_progress = CourseEnrollment.objects.get(
                user=request.user, 
                course=course
            )
    
    # Évaluations
    ratings = CourseRating.objects.filter(course=course, rating__gte=4)[:3]
    
    # Formations similaires
    similar_courses = Course.objects.filter(
        category=course.category,
        is_published=True
    ).exclude(id=course.id)[:3]
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'user_progress': user_progress,
        'ratings': ratings,
        'similar_courses': similar_courses,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_enroll(request, slug):
    """Inscription à une formation"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Vérifier si déjà inscrit
    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'Vous êtes déjà inscrit à cette formation.')
        return redirect('courses:course_detail', slug=slug)
    
    # Créer l'inscription
    enrollment = CourseEnrollment.objects.create(
        user=request.user,
        course=course
    )
    
    # Mettre à jour le compteur d'inscriptions
    course.enrollment_count += 1
    course.save()
    
    messages.success(request, f'Inscription réussie à "{course.title}"!')
    return redirect('courses:course_detail', slug=slug)


@login_required
def lesson_detail(request, slug, lesson_id):
    """Détail d'une leçon"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Vérifier l'inscription
    enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        messages.error(request, 'Vous devez être inscrit pour accéder aux leçons.')
        return redirect('courses:course_detail', slug=slug)
    
    # Calculer la progression
    total_lessons = course.lessons.filter(is_active=True).count()
    completed_lessons = enrollment.completed_lessons.count() if hasattr(enrollment, 'completed_lessons') else 0
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Récupérer les notes de l'utilisateur
    user_notes = ""
    if hasattr(lesson, 'user_notes'):
        user_note = lesson.user_notes.filter(user=request.user).first()
        if user_note:
            user_notes = user_note.notes
    
    context = {
        'course': course,
        'lesson': lesson,
        'progress_percentage': progress_percentage,
        'user_notes': user_notes,
    }
    return render(request, 'courses/lesson_detail.html', context)


def category_detail(request, slug):
    """Détail d'une catégorie"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    courses = Course.objects.filter(
        category=category, 
        is_published=True
    )
    
    # Recherche
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filtres
    level = request.GET.get('level')
    if level:
        courses = courses.filter(difficulty_level=level)
    
    # Tri
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'title':
        courses = courses.order_by('title')
    elif sort_by == 'price':
        courses = courses.order_by('price')
    elif sort_by == 'duration':
        courses = courses.order_by('duration')
    else:
        courses = courses.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'courses/category_detail.html', context)


@login_required
def dashboard(request):
    """Dashboard utilisateur"""
    enrollments = CourseEnrollment.objects.filter(user=request.user)
    completed_courses = enrollments.filter(completed_at__isnull=False)
    in_progress_courses = enrollments.filter(completed_at__isnull=True)
    
    # Calculer la progression pour chaque formation
    for enrollment in in_progress_courses:
        total_lessons = enrollment.course.lessons.filter(is_active=True).count()
        completed_lessons = enrollment.completed_lessons.count() if hasattr(enrollment, 'completed_lessons') else 0
        enrollment.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Statistiques
    total_courses = enrollments.count()
    completed_count = completed_courses.count()
    progress_percentage = (completed_count / total_courses * 100) if total_courses > 0 else 0
    
    # Formations recommandées
    user_categories = enrollments.values_list('course__category__id', flat=True).distinct()
    recommended_courses = Course.objects.filter(
        category__id__in=user_categories,
        is_published=True
    ).exclude(
        id__in=enrollments.values_list('course__id', flat=True)
    )[:3]
    
    context = {
        'total_courses': total_courses,
        'completed_count': completed_count,
        'progress_percentage': progress_percentage,
        'in_progress_courses': in_progress_courses[:5],
        'completed_courses': completed_courses[:5],
        'recommended_courses': recommended_courses,
    }
    return render(request, 'courses/dashboard.html', context)


def search_courses(request):
    """Recherche globale de formations"""
    query = request.GET.get('q', '')
    courses = Course.objects.filter(is_published=True)
    
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query)
        ).distinct()
    
    # Filtres
    category = request.GET.get('category')
    level = request.GET.get('level')
    price = request.GET.get('price')
    
    if category:
        courses = courses.filter(category__slug=category)
    if level:
        courses = courses.filter(difficulty_level=level)
    if price == 'free':
        courses = courses.filter(is_free=True)
    elif price == 'paid':
        courses = courses.filter(is_free=False)
    
    # Tri
    sort_by = request.GET.get('sort', 'relevance')
    if sort_by == 'title':
        courses = courses.order_by('title')
    elif sort_by == 'price':
        courses = courses.order_by('price')
    elif sort_by == 'duration':
        courses = courses.order_by('duration')
    elif sort_by == 'newest':
        courses = courses.order_by('-created_at')
    else:
        # Tri par pertinence (nombre d'inscriptions)
        courses = courses.order_by('-enrollment_count')
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'courses': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_level': level,
        'selected_price': price,
        'sort_by': sort_by,
    }
    return render(request, 'courses/search_results.html', context)

@login_required
@login_required
def my_courses(request):
    """Affiche les formations de l'utilisateur connecté"""
    enrolled_courses = CourseEnrollment.objects.filter(
        user=request.user
    ).select_related('course')
    
    context = {
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
def my_progress(request):
    """Mon progrès"""
    enrollments = CourseEnrollment.objects.filter(user=request.user)
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'courses/my_progress.html', context)


def search_courses(request):
    """Recherche de formations"""
    query = request.GET.get('q', '')
    courses = Course.objects.filter(is_published=True)
    
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'courses/search_results.html', context)


def php_course_detail(request):
    context = {
        'course': {
            'id': 1,  # Ajoutez un ID valide pour le cours PHP
            'title': 'Maîtrise de PHP 8',
            'slug': 'maitrise-php-8',
            'description': 'Apprenez à développer des applications web dynamiques avec PHP 8...',
            'duration_hours': 40,
            'price': 199,
            'enrolled_students': 250,
            'level': 'Débutant',
            'category': {
                'name': 'Développement Web',
                'slug': 'developpement-web'
            },
            'objectives': [
                'Maîtriser les bases de PHP 8',
                'Développer des applications web dynamiques',
                'Créer des APIs RESTful',
                'Gérer les bases de données avec PHP'
            ],
            'prerequisites': [
                'Aucune connaissance en programmation requise',
                'Ordinateur avec connexion internet'
            ],
            'modules': [
                {
                    'title': 'Introduction à PHP 8',
                    'lessons': [
                        'Présentation de PHP 8 et ses nouveautés',
                        "Installation de l'environnement",
                        'Les bases de la syntaxe PHP',
                        'Variables et types de données',
                        'Opérateurs et structures de contrôle'
                    ]
                },
                {
                    'title': 'Programmation orientée objet',
                    'lessons': [
                        'Les classes et les objets',
                        'Héritage et polymorphisme',
                        'Interfaces et classes abstraites',
                        'Traits et espaces de noms'
                    ]
                }
            ]
        }
    }
    return render(request, 'courses/php_course_detail.html', context)

# courses/views.py
def flutter_course_detail(request):
    context = {
        'course': {
            'title': 'Développement Mobile avec Flutter',
            'description': 'Créez des applications mobiles multiplateformes avec Flutter et Dart...',
            'slug': 'flutter'  # Add this line to include the slug
        },
        'title': 'Flutter - Soft Skills Academy'
    }
    return render(request, 'courses/flutter_course_detail.html', context)

# courses/views.py
def payment_options(request, course_slug=None):
    context = {
        'title': 'Options de Paiement - Soft Skills Academy',
        'course': {'slug': course_slug} if course_slug else None
    }
    return render(request, 'payments/options.html', context)
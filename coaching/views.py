from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Coach, CoachingSession
from django.contrib import messages
from django.utils import timezone


def coach_list(request):
    """Liste des coachs"""
    coaches = Coach.objects.filter(is_available=True)
    return render(request, 'coaching/coach_list.html', {'coaches': coaches})


def coach_detail(request, coach_id):
    """Détail d'un coach"""
    coach = get_object_or_404(Coach, id=coach_id)
    return render(request, 'coaching/coach_detail.html', {'coach': coach})


def fatou_sylla(request):
    """Page de profil détaillée pour Fatou Sylla"""
    try:
        coach = Coach.objects.get(user__first_name='Fatou', user__last_name='Sylla')
    except Coach.DoesNotExist:
        # Créer un utilisateur et un coach par défaut si nécessaire
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user, created = User.objects.get_or_create(
            username='fatou.sylla',
            defaults={
                'first_name': 'Fatou',
                'last_name': 'Sylla',
                'email': 'fatou.sylla@example.com'
            }
        )
        
        if created:
            user.set_password('motdepasse')  # Changez ce mot de passe
            user.save()
        
        coach, _ = Coach.objects.get_or_create(
            user=user,
            defaults={
                'specialization': 'Développement Personnel',
                'experience_years': 5,
                'bio': 'Coach en développement personnel avec plus de 5 ans d\'expérience',
                'hourly_rate': 50.00,
                'is_available': True
            }
        )
    
    return render(request, 'coaching/fatou_sylla.html', {'coach': coach})


def jean_dupont(request):
    """Page de profil pour Jean Dupont - Gestion du stress"""
    # Solution 1: Récupérer par ID si vous connaissez l'ID
    # coach = get_object_or_404(Coach, id=1)  # Remplacez 1 par l'ID de Jean Dupont
    
    # Solution 2: Créer le coach s'il n'existe pas
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import User
    from .models import Coach
    
    User = get_user_model()
    
    # Vérifier si l'utilisateur existe, sinon le créer
    user, created = User.objects.get_or_create(
        username='jean.dupont',
        defaults={
            'email': 'jean.dupont@example.com',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'is_active': True
        }
    )
    
    # Vérifier si le coach existe, sinon le créer
    coach, created = Coach.objects.get_or_create(
        user=user,
        defaults={
            'specialization': 'Gestion du stress et développement personnel',
            'experience_years': 8,
            'bio': 'Expert en gestion du stress avec plus de 8 ans d\'expérience...',
            'hourly_rate': 80.00,
            'is_available': True,
            'rating': 4.8
        }
    )
    
    return render(request, 'coaching/jean_dupont.html', {'coach': coach})


def aminata_diop(request):
    """Page de profil pour Aminata Diop - Leadership"""
    try:
        coach = Coach.objects.get(user__first_name='Aminata', user__last_name='Diop')
    except Coach.DoesNotExist:
        # Gérer le cas où le coach n'existe pas
        return render(request, '404.html', status=404)
        
    return render(request, 'coaching/aminata_diop.html', {'coach': coach})


@login_required
def book_session(request, coach_id):
    """Réserver une session"""
    coach = get_object_or_404(Coach, id=coach_id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        session_date = request.POST.get('session_date')
        duration = int(request.POST.get('duration', 60))  # 60 minutes par défaut
        notes = request.POST.get('notes', '')
        
        try:
            # Calculer le prix en fonction de la durée et du tarif horaire
            price = (coach.hourly_rate * duration) / 60  # Convertir en heures
            
            # Créer une nouvelle session de coaching
            session = CoachingSession.objects.create(
                client=request.user,
                coach=coach,
                title=f"Session avec {coach.user.get_full_name()}",
                description=notes or f"Session de coaching avec {coach.user.get_full_name()}",
                session_type='individual',
                scheduled_at=session_date,
                duration_minutes=duration,
                price=price,  # Ajout du prix calculé
                status='scheduled'
            )
            
            # Rediriger vers la page de détail de la session
            return redirect('coaching:session_detail', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
    
    # Si méthode GET ou en cas d'erreur POST, afficher le formulaire
    return render(request, 'coaching/book_session.html', {
        'coach': coach,
        'now': timezone.now().strftime('%Y-%m-%dT%H:%M')
    })

@login_required
def my_sessions(request):
    """Affiche les sessions de l'utilisateur connecté"""
    sessions = CoachingSession.objects.filter(client=request.user).order_by('scheduled_at')
    return render(request, 'coaching/my_sessions.html', {'sessions': sessions})


def session_detail(request, session_id):
    """Détail d'une session"""
    session = get_object_or_404(CoachingSession, id=session_id)
    return render(request, 'coaching/session_detail.html', {'session': session})

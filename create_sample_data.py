#!/usr/bin/env python
"""
Script pour créer des données de test pour la plateforme Soft Skills
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softskills_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Category, Course, Lesson
from coaching.models import Coach
from blog.models import BlogCategory, BlogPost
from payments.models import SubscriptionPlan

User = get_user_model()

def create_sample_data():
    print("Création des données de test...")
    
    # Créer un utilisateur coach
    coach_user, created = User.objects.get_or_create(
        email='coach@softskills.com',
        defaults={
            'username': 'coach',
            'first_name': 'Marie',
            'last_name': 'Dubois',
            'user_type': 'coach',
            'is_staff': True,
        }
    )
    if created:
        coach_user.set_password('coach123')
        coach_user.save()
        print(f"Coach créé: {coach_user.get_full_name()}")
    
    # Créer des catégories de formations
    categories_data = [
        {
            'name': 'Communication',
            'slug': 'communication',
            'description': 'Améliorez vos compétences en communication interpersonnelle',
            'color': '#2563eb'
        },
        {
            'name': 'Leadership',
            'slug': 'leadership',
            'description': 'Développez votre leadership et votre capacité à motiver les équipes',
            'color': '#10b981'
        },
        {
            'name': 'Gestion du Stress',
            'slug': 'gestion-du-stress',
            'description': 'Apprenez à gérer le stress et à maintenir votre équilibre',
            'color': '#f59e0b'
        },
        {
            'name': 'Créativité',
            'slug': 'creativite',
            'description': 'Libérez votre créativité et votre capacité d\'innovation',
            'color': '#8b5cf6'
        },
        {
            'name': 'Intelligence Émotionnelle',
            'slug': 'intelligence-emotionnelle',
            'description': 'Développez votre quotient émotionnel et votre empathie',
            'color': '#ec4899'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"Catégorie créée: {category.name}")
    
    # Créer des formations
    courses_data = [
        {
            'title': 'Communication Efficace',
            'slug': 'communication-efficace',
            'description': 'Maîtrisez les techniques de communication pour mieux vous exprimer et être entendu.',
            'short_description': 'Apprenez à communiquer avec impact et clarté',
            'difficulty_level': 'beginner',
            'duration_hours': 8,
            'price': 49.00,
            'is_free': False,
            'objectives': 'À la fin de cette formation, vous saurez communiquer avec clarté, écouter activement et adapter votre message à votre auditoire.',
            'target_audience': 'Professionnels souhaitant améliorer leurs compétences en communication',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Leadership Inspirant',
            'slug': 'leadership-inspirant',
            'description': 'Développez votre leadership pour inspirer et guider votre équipe vers le succès.',
            'short_description': 'Devenez un leader inspirant et efficace',
            'difficulty_level': 'intermediate',
            'duration_hours': 12,
            'price': 79.00,
            'is_free': False,
            'objectives': 'Développez votre vision, inspirez votre équipe et créez un environnement de travail motivant.',
            'target_audience': 'Managers et futurs leaders',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Gestion du Stress au Travail',
            'slug': 'gestion-stress-travail',
            'description': 'Apprenez des techniques pratiques pour gérer le stress professionnel.',
            'short_description': 'Maîtrisez le stress et préservez votre bien-être',
            'difficulty_level': 'beginner',
            'duration_hours': 6,
            'price': 0.00,
            'is_free': True,
            'objectives': 'Identifiez les sources de stress et appliquez des techniques de relaxation efficaces.',
            'target_audience': 'Tous les professionnels',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Créativité et Innovation',
            'slug': 'creativite-innovation',
            'description': 'Libérez votre créativité et développez votre capacité d\'innovation.',
            'short_description': 'Débloquez votre potentiel créatif',
            'difficulty_level': 'intermediate',
            'duration_hours': 10,
            'price': 69.00,
            'is_free': False,
            'objectives': 'Développez votre pensée créative et appliquez des méthodes d\'innovation.',
            'target_audience': 'Professionnels créatifs et entrepreneurs',
            'is_published': True,
            'is_featured': False
        }
    ]
    
    for i, course_data in enumerate(courses_data):
        course, created = Course.objects.get_or_create(
            slug=course_data['slug'],
            defaults={
                **course_data,
                'category': categories[i % len(categories)],
                'instructor': coach_user
            }
        )
        if created:
            print(f"Formation créée: {course.title}")
            
            # Créer quelques leçons pour chaque formation
            lessons_data = [
                {
                    'title': 'Introduction',
                    'slug': 'introduction',
                    'description': 'Présentation de la formation et des objectifs',
                    'lesson_type': 'video',
                    'content': 'Bienvenue dans cette formation...',
                    'duration_minutes': 15,
                    'order': 1
                },
                {
                    'title': 'Théorie et Concepts',
                    'slug': 'theorie-concepts',
                    'description': 'Les concepts fondamentaux à maîtriser',
                    'lesson_type': 'text',
                    'content': 'Dans cette leçon, nous allons explorer...',
                    'duration_minutes': 30,
                    'order': 2
                },
                {
                    'title': 'Exercices Pratiques',
                    'slug': 'exercices-pratiques',
                    'description': 'Mise en pratique des concepts appris',
                    'lesson_type': 'exercise',
                    'content': 'Maintenant, passons à la pratique...',
                    'duration_minutes': 45,
                    'order': 3
                }
            ]
            
            for lesson_data in lessons_data:
                lesson, created = Lesson.objects.get_or_create(
                    course=course,
                    slug=lesson_data['slug'],
                    defaults=lesson_data
                )
                if created:
                    print(f"  - Leçon créée: {lesson.title}")
    
    # Créer un profil coach
    coach, created = Coach.objects.get_or_create(
        user=coach_user,
        defaults={
            'specialization': 'Développement personnel et soft skills',
            'experience_years': 8,
            'bio': 'Experte en développement personnel avec plus de 8 ans d\'expérience dans l\'accompagnement de professionnels.',
            'hourly_rate': 80.00,
            'is_available': True
        }
    )
    if created:
        print(f"Profil coach créé pour: {coach.user.get_full_name()}")
    
    # Créer des catégories de blog
    blog_categories_data = [
        {
            'name': 'Développement Personnel',
            'slug': 'developpement-personnel',
            'description': 'Articles sur le développement personnel et la croissance'
        },
        {
            'name': 'Soft Skills',
            'slug': 'soft-skills',
            'description': 'Conseils et techniques pour améliorer vos soft skills'
        },
        {
            'name': 'Leadership',
            'slug': 'leadership-blog',
            'description': 'Conseils de leadership et management'
        }
    ]
    
    blog_categories = []
    for cat_data in blog_categories_data:
        category, created = BlogCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        blog_categories.append(category)
        if created:
            print(f"Catégorie blog créée: {category.name}")
    
    # Créer des articles de blog
    blog_posts_data = [
        {
            'title': '5 Techniques pour Améliorer votre Communication',
            'slug': '5-techniques-communication',
            'excerpt': 'Découvrez des techniques simples et efficaces pour améliorer votre communication au quotidien.',
            'content': 'La communication est l\'une des compétences les plus importantes dans le monde professionnel...',
            'status': 'published',
            'read_time_minutes': 5
        },
        {
            'title': 'Comment Développer votre Leadership',
            'slug': 'developper-leadership',
            'excerpt': 'Le leadership n\'est pas inné, il se développe. Voici comment devenir un leader inspirant.',
            'content': 'Le leadership est une compétence qui peut être développée avec de la pratique...',
            'status': 'published',
            'read_time_minutes': 7
        },
        {
            'title': 'Gérer le Stress au Travail : Guide Complet',
            'slug': 'gerer-stress-travail',
            'excerpt': 'Un guide complet pour identifier et gérer les sources de stress professionnel.',
            'content': 'Le stress au travail est un problème majeur qui affecte de nombreux professionnels...',
            'status': 'published',
            'read_time_minutes': 8
        }
    ]
    
    for i, post_data in enumerate(blog_posts_data):
        post, created = BlogPost.objects.get_or_create(
            slug=post_data['slug'],
            defaults={
                **post_data,
                'author': coach_user,
                'category': blog_categories[i % len(blog_categories)]
            }
        )
        if created:
            print(f"Article blog créé: {post.title}")
    
    # Créer des plans d'abonnement
    subscription_plans_data = [
        {
            'name': 'Plan Mensuel',
            'description': 'Accès à toutes les formations pendant 1 mois',
            'plan_type': 'monthly',
            'price': 29.00,
            'duration_days': 30,
            'max_courses': 0,  # illimité
            'is_active': True,
            'is_popular': True
        },
        {
            'name': 'Plan Annuel',
            'description': 'Accès à toutes les formations pendant 1 an',
            'plan_type': 'yearly',
            'price': 299.00,
            'original_price': 348.00,
            'discount_percentage': 14,
            'duration_days': 365,
            'max_courses': 0,  # illimité
            'is_active': True,
            'is_featured': True
        }
    ]
    
    for plan_data in subscription_plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"Plan d'abonnement créé: {plan.name}")
    
    print("\n✅ Données de test créées avec succès!")
    print("\n📧 Comptes de test créés:")
    print(f"   - Admin: admin@softskills.com / admin123456")
    print(f"   - Coach: coach@softskills.com / coach123")
    print("\n🌐 Accédez à votre plateforme:")
    print("   - Site web: http://127.0.0.1:8000/")
    print("   - Admin: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    create_sample_data() 
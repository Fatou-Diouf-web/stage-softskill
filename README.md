# 🧠 Soft Skills Platform

Plateforme complète de formation et coaching en soft skills développée avec Django.

## 🚀 Fonctionnalités

- ✅ Formations en ligne avec suivi de progression
- ✅ Coaching individuel et en groupe
- ✅ Blog avec articles sur les soft skills
- ✅ Système de paiement et abonnements
- ✅ Dashboard utilisateur personnalisé
- ✅ Interface d'administration complète

## 🛠️ Installation

1. **Installer les dépendances**
```bash
pip install django djangorestframework django-cors-headers pillow python-decouple django-allauth django-crispy-forms crispy-bootstrap5
```

2. **Migrer la base de données**
```bash
python manage.py migrate
```

3. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

4. **Créer des données de test**
```bash
python create_sample_data.py
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

## 🌐 Accès

- **Site web**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## 👥 Comptes de Test

- **Admin**: admin@softskills.com / admin123456
- **Coach**: coach@softskills.com / coach123

## 📁 Applications

- `courses/` - Formations et leçons
- `coaching/` - Sessions de coaching
- `blog/` - Articles et contenu
- `payments/` - Système de paiement
- `users/` - Gestion des utilisateurs

## 🎯 Technologies

- Django 5.1.5
- Bootstrap 5
- SQLite (développement)
- Django Allauth
- Crispy Forms 
"""
URL configuration for softskills_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Mettez coaching/ en premier
    path('coaching/', include('coaching.urls', namespace='coaching')),  
    # Ensuite les autres URLs
    path('', include('courses.urls', namespace='courses')),
    path('blog/', include('blog.urls', namespace='blog')),  # Ajoutez cette ligne
    path('payments/', include('payments.urls')),
    path('accounts/', include('allauth.urls')),
    path('contact/', include('contact.urls', namespace='contact')),
    path('users/', include('users.urls', namespace='users')),
]

# Configuration pour les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration du site admin
admin.site.site_header = "Soft Skills Platform - Administration"
admin.site.site_title = "Soft Skills Platform"
admin.site.index_title = "Bienvenue dans l'administration"

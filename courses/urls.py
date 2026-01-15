# courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/<slug:slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-progress/', views.my_progress, name='my_progress'),
    path('search/', views.search_courses, name='search_courses'),
    path('maitrise-php-8/', views.php_course_detail, name='php_course_detail'),
    path('flutter/', views.flutter_course_detail, name='flutter_course_detail'),
    path('payment/options/<slug:course_slug>/', views.payment_options, name='payment_options'),
    path('payment/options/', views.payment_options, name='payment_options'),
    
    # Modifiez cette ligne pour qu'elle ne capture que les URLs qui commencent par courses/
    path('courses/<slug:slug>/', views.course_detail, name='course_detail_fallback'),
    path('', views.home, name='home'),  # Assurez-vous que cette ligne existe
]
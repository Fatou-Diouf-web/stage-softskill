from django.urls import path
from . import views

app_name = 'coaching'

urlpatterns = [
    path('', views.coach_list, name='coach_list'),
    path('coach/<int:coach_id>/', views.coach_detail, name='coach_detail'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('book-session/<int:coach_id>/', views.book_session, name='book_session'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('fatou-sylla/', views.fatou_sylla, name='fatou_sylla'),
    path('jean-dupont/', views.jean_dupont, name='jean_dupont'),
    path('aminata-diop/', views.aminata_diop, name='aminata_diop'),
] 
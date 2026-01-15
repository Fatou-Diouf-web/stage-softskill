from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from courses.models import Course, CourseEnrollment
from .models import SubscriptionPlan, Payment
import json
import hashlib
import hmac
import requests
from urllib.parse import urljoin




@login_required

def course_payment(request, course_id):
    """Page de paiement pour une formation spécifique"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Vérifier si l'utilisateur est déjà inscrit au cours
    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'Vous êtes déjà inscrit à cette formation.')
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        # Traitement du paiement avec PayTech
        payment_result = process_paytech_payment(request, course)
        
        if payment_result['success']:
            return redirect(payment_result['redirect_url'])
        else:
            messages.error(request, payment_result['message'])
    
    context = {
        'course': course,
        'paytech_public_key': getattr(settings, 'PAYTECH_PUBLIC_KEY', ''),
    }
    return render(request, 'payments/course_payment.html', context)

@login_required
@login_required
def process_payment(request, course_id, payment_method):
    """Page de traitement du paiement"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Vérifier si l'utilisateur est déjà inscrit
    if CourseEnrollment.objects.filter(user_id=request.user.id, course=course).exists():
        messages.warning(request, "Vous êtes déjà inscrit à ce cours.")
        return redirect('courses:course_detail', slug=course.slug)
    
    context = {
        'course': course,
        'payment_method': payment_method,
    }
    return render(request, 'payments/process_payment.html', context) 

@login_required
def course_payment(request, course_id):
    """Page de paiement pour une formation spécifique"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Vérifier si l'utilisateur est déjà inscrit
    if CourseEnrollment.objects.filter(user_id=request.user.id, course=course).exists():
        messages.info(request, 'Vous êtes déjà inscrit à cette formation.')
        return redirect('courses:course_detail', slug=course.slug)
    
    # Si une méthode de paiement est spécifiée, rediriger vers process_payment
    payment_method = request.GET.get('method')
    if payment_method and payment_method in ['wave', 'orange', 'visa']:
        return redirect('payments:process_payment', 
                      course_id=course.id, 
                      payment_method=payment_method)
    
    # Sinon, afficher la page de sélection de la méthode de paiement
    context = {
        'course': course,
    }
    return render(request, 'payments/select_payment_method.html', context) 

@csrf_exempt
@require_POST
def paytech_ipn(request):
    """Endpoint IPN (Instant Payment Notification) pour PayTech"""
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        # Vérifier le paiement
        payment = Payment.objects.get(transaction_id=token)
        
        # Mettre à jour le statut du paiement
        if data.get('success') == '1':
            payment.status = 'completed'
            
            # Créer l'inscription au cours
            CourseEnrollment.objects.get_or_create(
                user=payment.user,
                course=payment.course,
                payment=payment
            )
        else:
            payment.status = 'failed'
        
        payment.gateway_response = data
        payment.save()
        
        return HttpResponse('OK')
    except Exception as e:
        # Log l'erreur pour le débogage
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erreur IPN PayTech: {str(e)}')
        return HttpResponse('ERROR', status=400)


def subscription_list(request):
    """Liste des plans d'abonnement"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'payments/subscription_list.html', {'plans': plans})


@login_required
def checkout(request, plan_id):
    """Page de paiement"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    return render(request, 'payments/checkout.html', {'plan': plan})


class PaymentView(TemplateView):
    """Page principale de paiement"""
    template_name = 'payments/payment_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['pending_payments'] = CourseEnrollment.objects.filter(
                user=self.request.user,
                payment_status='pending'
            )
        return context


def payment_success(request):
    """Page de succès de paiement"""
    return render(request, 'payments/success.html')


def payment_cancel(request):
    """Page d'annulation de paiement"""
    return render(request, 'payments/cancel.html')

@login_required
@require_http_methods(["POST"])
def init_paytech_payment(request, course_id):
    """Vue pour initialiser un paiement PayTech"""
    try:
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Vérifier si l'utilisateur est déjà inscrit
        if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
            return JsonResponse({
                'success': False,
                'message': 'Vous êtes déjà inscrit à cette formation.'
            }, status=400)
        
        # Récupérer les données de la requête
        data = json.loads(request.body)
        payment_method = data.get('payment_method', 'visa')
        
        # Paramètres de la requête vers l'API PayTech
        params = {
            'item_name': course.title,
            'item_price': str(int(float(course.price) * 100)),  # Convertir en centimes
            'currency': 'XOF',
            'ref_command': f'COURSE-{course.id}-{request.user.id}',
            'command_name': f'Paiement formation {course.title}',
            'env': 'test' if settings.DEBUG else 'prod',
            'ipn_url': request.build_absolute_uri(reverse('payments:paytech_ipn')),
            'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
            'cancel_url': request.build_absolute_uri(reverse('payments:payment_cancel')),
            'custom_field': json.dumps({
                'user_id': request.user.id,
                'course_id': course.id,
                'payment_method': payment_method
            })
        }
        
        # Signature de la requête
        signature_data = f"{params['item_name']}{params['item_price']}{params['command_name']}{params['ref_command']}{settings.PAYTECH_API_KEY}"
        signature = hmac.new(
            settings.PAYTECH_API_SECRET.encode('utf-8'),
            signature_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        params['public_key'] = settings.PAYTECH_API_KEY
        
        # URL de l'API PayTech
        api_url = urljoin(settings.PAYTECH_BASE_URL, '/payment/init')
        
        # Envoyer la requête à l'API PayTech
        response = requests.post(api_url, json=params)
        response_data = response.json()
        
        if response_data.get('success') == 1:
            return JsonResponse({
                'success': True,
                'payment_url': response_data.get('redirect_url')
            })
        else:
            return JsonResponse({
                'success': False,
                'message': response_data.get('message', 'Erreur lors de l\'initialisation du paiement')
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Une erreur est survenue: {str(e)}'
        }, status=500)

@csrf_exempt
@require_POST
def paytech_ipn(request):
    """Endpoint IPN (Instant Payment Notification) pour PayTech"""
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        # Vérifier le paiement
        payment = Payment.objects.get(transaction_id=token)
        
        # Mettre à jour le statut du paiement
        if data.get('success') == '1':
            payment.status = 'completed'
            
            # Créer l'inscription au cours
            CourseEnrollment.objects.get_or_create(
                user=payment.user,
                course=payment.course,
                payment=payment
            )
        else:
            payment.status = 'failed'
        
        payment.gateway_response = data
        payment.save()
        
        return HttpResponse('OK')
    except Exception as e:
        # Log l'erreur pour le débogage
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erreur IPN PayTech: {str(e)}')
        return HttpResponse('ERROR', status=400)
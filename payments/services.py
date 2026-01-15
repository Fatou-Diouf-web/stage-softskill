import hashlib
import json
import requests
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Payment

class PayTechService:
    """Service pour gérer les paiements avec PayTech"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'PAYTECH_API_KEY', '')
        self.api_secret = getattr(settings, 'PAYTECH_API_SECRET', '')
        self.base_url = getattr(settings, 'PAYTECH_BASE_URL', 'https://paytech.sn')
    
    def _generate_signature(self, params):
        """Génère la signature pour l'API PayTech"""
        params_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hashlib.sha256(f"{params_str}{self.api_secret}".encode()).hexdigest()
    
    def init_payment(self, amount, currency, item_name, item_ref, user_email, user_first_name, user_last_name, ipn_url, success_url, cancel_url):
        """Initialise un paiement avec PayTech"""
        endpoint = f"{self.base_url}/api/payment/request-payment"
        
        params = {
            'item_name': item_name,
            'item_price': str(amount),
            'currency': currency,
            'ref_command': item_ref,
            'command_name': item_name,
            'env': 'test' if settings.DEBUG else 'prod',
            'ipn_url': ipn_url,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'email': user_email,
            'first_name': user_first_name,
            'last_name': user_last_name,
            'api_key': self.api_key,
            'lang': 'fr'
        }
        
        params['signature'] = self._generate_signature(params)
        
        try:
            response = requests.post(endpoint, json=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': 0,
                'message': str(e)
            }
    
    def verify_payment(self, token):
        """Vérifie le statut d'un paiement"""
        endpoint = f"{self.base_url}/api/payment/check"
        
        params = {
            'token': token,
            'api_key': self.api_key
        }
        
        params['signature'] = self._generate_signature(params)
        
        try:
            response = requests.post(endpoint, json=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': 0,
                'message': str(e)
            }

def process_paytech_payment(request, course):
    """Traite un paiement avec PayTech"""
    paytech = PayTechService()
    
    # Créer une commande en attente
    payment = Payment.objects.create(
        user=request.user,
        payment_type='course',
        amount=course.price,
        currency='XOF',
        status='pending',
        course=course
    )
    
    # Préparer les URLs de retour
    base_url = f"{request.scheme}://{request.get_host()}"
    
    # Initialiser le paiement PayTech
    response = paytech.init_payment(
        amount=float(course.price) * 655.957,  # Conversion en FCFA
        currency='XOF',
        item_name=f"Formation: {course.title}",
        item_ref=f"COURSE-{course.id}-{payment.id}",
        user_email=request.user.email,
        user_first_name=request.user.first_name,
        user_last_name=request.user.last_name,
        ipn_url=f"{base_url}{reverse('payments:paytech_ipn')}",
        success_url=f"{base_url}{reverse('payments:payment_success')}",
        cancel_url=f"{base_url}{reverse('payments:payment_cancel')}"
    )
    
    if response.get('success') == 1:
        # Sauvegarder le token de la transaction
        payment.transaction_id = response.get('token')
        payment.gateway_response = response
        payment.save()
        
        return {
            'success': True,
            'redirect_url': response.get('redirect_url')
        }
    else:
        # Mettre à jour le statut du paiement en échec
        payment.status = 'failed'
        payment.gateway_response = response
        payment.save()
        
        return {
            'success': False,
            'message': response.get('message', 'Erreur lors de l\'initialisation du paiement')
        }
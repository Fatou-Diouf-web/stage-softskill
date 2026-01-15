from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SubscriptionPlan, UserSubscription, Payment, Coupon, Invoice


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Interface d'administration pour les plans d'abonnement"""
    
    list_display = [
        'name', 'plan_type', 'price', 'discounted_price',
        'is_active', 'is_popular', 'is_featured', 'duration_days'
    ]
    list_filter = [
        'plan_type', 'is_active', 'is_popular', 'is_featured',
        'created_at'
    ]
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'is_popular', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'plan_type')
        }),
        (_('Prix'), {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        (_('Fonctionnalités'), {
            'fields': ('features', 'max_courses', 'max_coaching_sessions')
        }),
        (_('Statut'), {
            'fields': ('is_active', 'is_popular', 'is_featured')
        }),
        (_('Durée'), {
            'fields': ('duration_days',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Interface d'administration pour les abonnements utilisateur"""
    
    list_display = [
        'user', 'plan', 'status', 'start_date', 'end_date',
        'amount_paid', 'auto_renew', 'is_active'
    ]
    list_filter = [
        'status', 'plan', 'auto_renew', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'plan__name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'is_active'
    ]
    list_editable = ['status', 'auto_renew']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'plan')
        }),
        (_('Statut et dates'), {
            'fields': ('status', 'start_date', 'end_date', 'cancelled_at')
        }),
        (_('Renouvellement'), {
            'fields': ('auto_renew', 'next_billing_date')
        }),
        (_('Paiement'), {
            'fields': ('amount_paid', 'payment_method')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Interface d'administration pour les paiements"""
    
    list_display = [
        'user', 'payment_type', 'amount', 'currency',
        'status', 'payment_method', 'created_at'
    ]
    list_filter = [
        'payment_type', 'status', 'payment_method', 'currency',
        'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'transaction_id'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'completed_at'
    ]
    list_editable = ['status']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'payment_type')
        }),
        (_('Montant et devise'), {
            'fields': ('amount', 'currency')
        }),
        (_('Statut et méthode'), {
            'fields': ('status', 'payment_method')
        }),
        (_('Références externes'), {
            'fields': ('transaction_id', 'gateway_response')
        }),
        (_('Objets liés'), {
            'fields': ('subscription', 'course', 'coaching_session'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Interface d'administration pour les coupons"""
    
    list_display = [
        'code', 'coupon_type', 'discount_value', 'min_amount',
        'max_uses', 'used_count', 'is_active', 'is_valid'
    ]
    list_filter = [
        'coupon_type', 'is_active', 'valid_from', 'valid_until'
    ]
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'coupon_type')
        }),
        (_('Réduction'), {
            'fields': ('discount_value', 'min_amount')
        }),
        (_('Limites d\'utilisation'), {
            'fields': ('max_uses', 'used_count')
        }),
        (_('Validité'), {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        (_('Applicabilité'), {
            'fields': ('applicable_plans', 'applicable_courses'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['applicable_plans', 'applicable_courses']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Interface d'administration pour les factures"""
    
    list_display = [
        'invoice_number', 'user', 'total_amount', 'is_paid',
        'created_at'
    ]
    list_filter = ['is_paid', 'created_at']
    search_fields = [
        'invoice_number', 'user__email', 'user__first_name',
        'user__last_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'paid_at'
    ]
    list_editable = ['is_paid']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'payment', 'invoice_number')
        }),
        (_('Montants'), {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        (_('Adresse de facturation'), {
            'fields': (
                'billing_address', 'billing_city', 'billing_country',
                'billing_postal_code'
            ),
            'classes': ('collapse',)
        }),
        (_('Statut'), {
            'fields': ('is_paid', 'paid_at')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'payment')

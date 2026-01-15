from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal


class SubscriptionPlan(models.Model):
    """Plan d'abonnement"""
    
    PLAN_TYPES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
        ('lifetime', 'À vie'),
    ]
    
    name = models.CharField(_('nom'), max_length=100)
    description = models.TextField(_('description'))
    plan_type = models.CharField(
        _('type de plan'),
        max_length=20,
        choices=PLAN_TYPES,
        default='monthly'
    )
    
    # Pricing
    price = models.DecimalField(
        _('prix'),
        max_digits=10,
        decimal_places=2
    )
    original_price = models.DecimalField(
        _('prix original'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Prix avant réduction')
    )
    discount_percentage = models.PositiveIntegerField(
        _('pourcentage de réduction'),
        default=0
    )
    
    # Features
    features = models.JSONField(
        _('fonctionnalités'),
        default=list,
        help_text=_('Liste des fonctionnalités incluses')
    )
    max_courses = models.PositiveIntegerField(
        _('nombre maximum de cours'),
        default=0,
        help_text=_('0 = illimité')
    )
    max_coaching_sessions = models.PositiveIntegerField(
        _('nombre maximum de sessions de coaching'),
        default=0,
        help_text=_('0 = illimité')
    )
    
    # Status
    is_active = models.BooleanField(_('actif'), default=True)
    is_popular = models.BooleanField(_('populaire'), default=False)
    is_featured = models.BooleanField(_('mis en avant'), default=False)
    
    # Duration
    duration_days = models.PositiveIntegerField(
        _('durée en jours'),
        default=30,
        help_text=_('Durée du plan en jours')
    )
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('plan d\'abonnement')
        verbose_name_plural = _('plans d\'abonnement')
        ordering = ['price']
    
    def __str__(self):
        return self.name
    
    @property
    def discounted_price(self):
        """Calcule le prix avec réduction"""
        if self.discount_percentage > 0:
            discount = self.price * (self.discount_percentage / 100)
            return self.price - discount
        return self.price
    
    @property
    def savings_amount(self):
        """Calcule le montant économisé"""
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return Decimal('0.00')


class UserSubscription(models.Model):
    """Abonnement d'un utilisateur"""
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
        ('pending', 'En attente'),
        ('failed', 'Échoué'),
    ]
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('utilisateur')
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        verbose_name=_('plan')
    )
    
    # Status and dates
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_date = models.DateTimeField(_('date de début'))
    end_date = models.DateTimeField(_('date de fin'))
    cancelled_at = models.DateTimeField(_('annulé le'), null=True, blank=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(_('renouvellement automatique'), default=True)
    next_billing_date = models.DateTimeField(_('prochaine facturation'), null=True, blank=True)
    
    # Payment
    amount_paid = models.DecimalField(
        _('montant payé'),
        max_digits=10,
        decimal_places=2
    )
    payment_method = models.CharField(_('méthode de paiement'), max_length=50, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('abonnement utilisateur')
        verbose_name_plural = _('abonnements utilisateur')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name}"
    
    @property
    def is_active(self):
        """Vérifie si l'abonnement est actif"""
        return (self.status == 'active' and 
                self.end_date > timezone.now())
    
    @property
    def days_remaining(self):
        """Calcule le nombre de jours restants"""
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0


class Payment(models.Model):
    """Paiement"""
    
    PAYMENT_TYPES = [
        ('subscription', 'Abonnement'),
        ('course', 'Formation'),
        ('coaching', 'Coaching'),
        ('donation', 'Don'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
        ('cancelled', 'Annulé'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
    ]
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('utilisateur')
    )
    
    # Payment details
    payment_type = models.CharField(
        _('type de paiement'),
        max_length=20,
        choices=PAYMENT_TYPES,
        default='subscription'
    )
    amount = models.DecimalField(
        _('montant'),
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(_('devise'), max_length=3, default='EUR')
    
    # Status and method
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )
    payment_method = models.CharField(
        _('méthode de paiement'),
        max_length=20,
        choices=PAYMENT_METHODS,
        default='card'
    )
    
    # External references
    transaction_id = models.CharField(
        _('ID de transaction'),
        max_length=100,
        unique=True,
        blank=True
    )
    gateway_response = models.JSONField(
        _('réponse de la passerelle'),
        default=dict,
        blank=True
    )
    
    # Related objects
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('abonnement')
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('formation')
    )
    coaching_session = models.ForeignKey(
        'coaching.CoachingSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('session de coaching')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('paiement')
        verbose_name_plural = _('paiements')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount} {self.currency} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Coupon de réduction"""
    
    COUPON_TYPES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]
    
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.CharField(_('description'), max_length=200)
    coupon_type = models.CharField(
        _('type de coupon'),
        max_length=20,
        choices=COUPON_TYPES,
        default='percentage'
    )
    
    # Discount
    discount_value = models.DecimalField(
        _('valeur de réduction'),
        max_digits=10,
        decimal_places=2
    )
    min_amount = models.DecimalField(
        _('montant minimum'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Montant minimum pour utiliser le coupon')
    )
    
    # Usage limits
    max_uses = models.PositiveIntegerField(
        _('utilisation maximum'),
        default=0,
        help_text=_('0 = illimité')
    )
    used_count = models.PositiveIntegerField(_('nombre d\'utilisations'), default=0)
    
    # Validity
    valid_from = models.DateTimeField(_('valide à partir du'))
    valid_until = models.DateTimeField(_('valide jusqu\'au'))
    is_active = models.BooleanField(_('actif'), default=True)
    
    # Applicability
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name='coupons',
        verbose_name=_('plans applicables')
    )
    applicable_courses = models.ManyToManyField(
        'courses.Course',
        blank=True,
        related_name='coupons',
        verbose_name=_('formations applicables')
    )
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('coupon')
        verbose_name_plural = _('coupons')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        """Vérifie si le coupon est valide"""
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                (self.max_uses == 0 or self.used_count < self.max_uses))
    
    def calculate_discount(self, amount):
        """Calcule la réduction pour un montant donné"""
        if amount < self.min_amount:
            return Decimal('0.00')
        
        if self.coupon_type == 'percentage':
            return amount * (self.discount_value / 100)
        else:
            return min(self.discount_value, amount)


class Invoice(models.Model):
    """Facture"""
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('utilisateur')
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name=_('paiement')
    )
    
    # Invoice details
    invoice_number = models.CharField(_('numéro de facture'), max_length=50, unique=True)
    subtotal = models.DecimalField(_('sous-total'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('montant TVA'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('montant réduction'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('montant total'), max_digits=10, decimal_places=2)
    
    # Billing information
    billing_address = models.TextField(_('adresse de facturation'), blank=True)
    billing_city = models.CharField(_('ville de facturation'), max_length=100, blank=True)
    billing_country = models.CharField(_('pays de facturation'), max_length=100, blank=True)
    billing_postal_code = models.CharField(_('code postal'), max_length=20, blank=True)
    
    # Status
    is_paid = models.BooleanField(_('payée'), default=False)
    paid_at = models.DateTimeField(_('payée le'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('facture')
        verbose_name_plural = _('factures')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if self.is_paid and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

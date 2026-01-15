from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, CustomUser

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Crée ou met à jour le profil utilisateur.
    S'assure qu'un profil existe pour chaque utilisateur.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
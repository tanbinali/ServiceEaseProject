from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import Profile
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def add_user_to_client_group(sender, instance, created, **kwargs):
    """
    Assigns new users to the 'Client' group when they are activated.
    """
    if not created and instance.is_active:
        client_group, _ = Group.objects.get_or_create(name="Client")
        if not instance.groups.filter(name="Client").exists():
            instance.groups.add(client_group)
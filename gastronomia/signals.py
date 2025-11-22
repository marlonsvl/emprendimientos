# gastronomia/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name or "",
            last_name=instance.last_name or ""
        )

@receiver(post_save, sender=User)
def sync_user_profile(sender, instance, **kwargs):
    try:
        profile = instance.userprofile
        changed = False
        if profile.first_name != instance.first_name:
            profile.first_name = instance.first_name
            changed = True
        if profile.last_name != instance.last_name:
            profile.last_name = instance.last_name
            changed = True
        if changed:
            profile.save()
    except UserProfile.DoesNotExist:
        # created by create_user_profile ideally; ignore otherwise
        pass

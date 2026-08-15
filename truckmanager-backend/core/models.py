from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_user_role(user):
    """Retourne le rôle de l'utilisateur depuis son profil."""
    if not user:
        return 'OWNER'

    if not getattr(user, 'is_authenticated', False):
        return 'OWNER'

    try:
        profile = user.profile
    except User.profile.RelatedObjectDoesNotExist:
        profile = None

    if profile and getattr(profile, 'role', None):
        return profile.role

    return 'OWNER'


class UserProfile(models.Model):
    """Profil utilisateur étendu."""

    ROLE_ADMIN = 'ADMIN'
    ROLE_OWNER = 'OWNER'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_OWNER, 'Propriétaire'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OWNER)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': UserProfile.ROLE_OWNER},
        )

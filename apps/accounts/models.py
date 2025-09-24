from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur personnalisé - Principe KISS"""
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin_association', 'Admin Association'),
        ('resident', 'Résident'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    telephone = models.CharField(max_length=15, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
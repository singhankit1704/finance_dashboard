from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles:
      - viewer   : read-only access to dashboard data
      - analyst  : read access + insights/summaries
      - admin    : full access (create, update, delete records & users)
    """
    ROLE_VIEWER = 'viewer'
    ROLE_ANALYST = 'analyst'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_ANALYST, 'Analyst'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Avoid clashes with default auth.User
    groups = models.ManyToManyField('auth.Group', blank=True, related_name='custom_user_set')
    user_permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='custom_user_permissions_set')

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_analyst(self):
        return self.role in [self.ROLE_ANALYST, self.ROLE_ADMIN]

    @property
    def is_viewer(self):
        return True  # all roles can view

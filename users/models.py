
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='student',
        help_text='Type of user account'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )

    # Override related names for auth relationships to avoid reverse-accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='app_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='app_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        help_text='Short biography'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Date of birth'
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='User location/address'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        """Returns the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def is_student(self):
        """Check if user is a student"""
        return self.user_type == 'student'
    
    def is_mentor(self):
        """Check if user is a mentor"""
        return self.user_type == 'mentor'
    
    def is_admin_user(self):
        """Check if user is an administrator"""
        return self.user_type == 'admin'

# Additional user models can be added here if needed
# WorkSubmission and MentorFeedback are now in the materials app

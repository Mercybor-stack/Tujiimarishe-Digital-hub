

# Admin registration for user-related models
# WorkSubmission and MentorFeedback are registered in materials.admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin
    """
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'user_type', 
        'is_active', 
        'is_staff',
        'date_joined',
        'profile_image_preview'
    ]
    
    list_filter = [
        'user_type', 
        'is_active', 
        'is_staff', 
        'is_superuser', 
        'date_joined'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'phone_number'
    ]
    
    ordering = ['-date_joined']
    
    # Add user_type to the fieldsets
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 
                'last_name', 
                'email', 
                'phone_number', 
                'date_of_birth',
                'location',
                'bio',
                'profile_picture'
            )
        }),
        ('User Type', {
            'fields': ('user_type',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email',
                'user_type',
                'password1', 
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def profile_image_preview(self, obj):
        """Display profile picture thumbnail in admin"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    
    profile_image_preview.short_description = 'Profile Picture'
    
    # Add actions
    actions = ['make_student', 'make_mentor', 'make_admin', 'activate_users', 'deactivate_users']
    
    def make_student(self, request, queryset):
        """Change selected users to students"""
        updated = queryset.update(user_type='student')
        self.message_user(request, f'{updated} user(s) changed to Student.')
    make_student.short_description = 'Change to Student'
    
    def make_mentor(self, request, queryset):
        """Change selected users to mentors"""
        updated = queryset.update(user_type='mentor')
        self.message_user(request, f'{updated} user(s) changed to Mentor.')
    make_mentor.short_description = 'Change to Mentor'
    
    def make_admin(self, request, queryset):
        """Change selected users to admins"""
        updated = queryset.update(user_type='admin')
        self.message_user(request, f'{updated} user(s) changed to Administrator.')
    make_admin.short_description = 'Change to Administrator'
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'


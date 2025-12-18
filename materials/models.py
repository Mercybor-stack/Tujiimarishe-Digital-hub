from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class SkillCategory(models.Model):
    """Digital Marketing, Graphic Design, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50)  # Font Awesome icon class
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = "Skill Categories"
    
    def __str__(self):
        return self.name

class LearningMaterial(models.Model):
    """YouTube videos and PDFs for each skill"""
    MATERIAL_TYPE = [
        ('video', 'YouTube Video'),
        ('pdf', 'PDF Document'),
    ]
    
    ACCESS_LEVEL = [
        ('basic', 'Basic - Free'),
        ('enterprise', 'Enterprise - KSh 100'),
        ('premium', 'Premium - KSh 200'),
    ]
    
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField()
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE)
    youtube_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True, null=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL)
    order = models.IntegerField(default=0)  # For ordering lessons
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.category.name} - {self.title}"

class UserSkillAccess(models.Model):
    """Track which access level each user has for each skill"""
    ACCESS_LEVEL = [
        ('basic', 'Basic - Free'),
        ('enterprise', 'Enterprise - KSh 100'),
        ('premium', 'Premium - KSh 200'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_access')
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL, default='basic')
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'category')
        verbose_name_plural = "User Skill Access"
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.access_level})"

class WorkSubmission(models.Model):
    """Learner work submissions for feedback"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_submissions')
    category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='work_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class MentorFeedback(models.Model):
    """Feedback from mentors on submissions"""
    RATING_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('needs_improvement', 'Needs Improvement'),
    ]
    
    submission = models.OneToOneField(WorkSubmission, on_delete=models.CASCADE, related_name='feedback')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_given')
    feedback = models.TextField()
    recommendation = models.TextField(blank=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.submission.title}"

class Payment(models.Model):
    """M-Pesa payment records"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=20)  # 'enterprise' or 'premium'
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    mpesa_code = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - KSh {self.amount}"
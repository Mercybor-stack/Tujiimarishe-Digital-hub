from django.contrib import admin
from .models import SkillCategory, LearningMaterial, UserSkillAccess, Payment, WorkSubmission, MentorFeedback

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'id']
    search_fields = ['name', 'description']

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'material_type', 'access_level', 'order']
    list_filter = ['category', 'material_type', 'access_level']
    search_fields = ['title', 'description']
    ordering = ['category', 'order']

@admin.register(UserSkillAccess)
class UserSkillAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'access_level', 'purchased_at']
    list_filter = ['access_level', 'category']
    search_fields = ['user__username', 'category__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'access_level', 'amount', 'mpesa_code', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'access_level', 'created_at']
    search_fields = ['user__username', 'mpesa_code', 'phone_number']
    readonly_fields = ['created_at']

@admin.register(WorkSubmission)
class WorkSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'submitted_at', 'is_reviewed']
    list_filter = ['is_reviewed', 'category', 'submitted_at']
    search_fields = ['title', 'user__username']

@admin.register(MentorFeedback)
class MentorFeedbackAdmin(admin.ModelAdmin):
    list_display = ['submission', 'mentor', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']

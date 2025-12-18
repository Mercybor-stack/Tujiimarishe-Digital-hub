from django import forms
from .models import WorkSubmission, MentorFeedback


class WorkSubmissionForm(forms.ModelForm):
    class Meta:
        model = WorkSubmission
        fields = ['title', 'description', 'file']


class MentorFeedbackForm(forms.ModelForm):
    class Meta:
        model = MentorFeedback
        fields = ['rating', 'feedback', 'recommendation']

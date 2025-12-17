
# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import WorkSubmission, MentorFeedback
import tempfile

User = get_user_model()

# Create your tests here.


class UserRegistrationTests(TestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_register_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
    
    def test_registration_passwords_dont_match(self):
        """Test that registration fails when passwords don't match"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123!',
            'password2': 'differentpass123!',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 0)


class UserLoginTests(TestCase):
    """Test user login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
    
    def test_user_login_success(self):
        """Test successful user login"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123!',
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class WorkSubmissionModelTests(TestCase):
    """Test WorkSubmission model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
    
    def test_work_submission_creation(self):
        """Test creating a work submission"""
        # Create a temporary file
        temp_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        submission = WorkSubmission.objects.create(
            user=self.user,
            title='Test Project',
            description='This is a test project',
            file=temp_file
        )
        
        self.assertEqual(submission.title, 'Test Project')
        self.assertEqual(submission.user, self.user)
        self.assertFalse(submission.is_reviewed)
    
    def test_work_submission_str_method(self):
        """Test WorkSubmission string representation"""
        temp_file = SimpleUploadedFile(
            "test_file.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        submission = WorkSubmission.objects.create(
            user=self.user,
            title='My Project',
            description='Description',
            file=temp_file
        )
        
        self.assertEqual(str(submission), f"My Project - testuser")
    
    def test_work_submission_ordering(self):
        """Test that submissions are ordered by submitted_at descending"""
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        submission1 = WorkSubmission.objects.create(
            user=self.user,
            title='First Project',
            description='First',
            file=temp_file
        )
        
        submission2 = WorkSubmission.objects.create(
            user=self.user,
            title='Second Project',
            description='Second',
            file=temp_file
        )
        
        submissions = WorkSubmission.objects.all()
        self.assertEqual(submissions[0], submission2)
        self.assertEqual(submissions[1], submission1)


class MentorFeedbackModelTests(TestCase):
    """Test MentorFeedback model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123!'
        )
        
        self.mentor = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='pass123!',
            is_staff=True
        )
        
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        self.submission = WorkSubmission.objects.create(
            user=self.user,
            title='Test Project',
            description='Description',
            file=temp_file
        )
    
    def test_mentor_feedback_creation(self):
        """Test creating mentor feedback"""
        feedback = MentorFeedback.objects.create(
            submission=self.submission,
            mentor=self.mentor,
            feedback='Great work! Keep it up.',
            rating='excellent'
        )
        
        self.assertEqual(feedback.submission, self.submission)
        self.assertEqual(feedback.mentor, self.mentor)
        self.assertEqual(feedback.rating, 'excellent')
    
    def test_mentor_feedback_str_method(self):
        """Test MentorFeedback string representation"""
        feedback = MentorFeedback.objects.create(
            submission=self.submission,
            mentor=self.mentor,
            feedback='Good effort',
            rating='good'
        )
        
        self.assertEqual(str(feedback), f"Feedback for Test Project")
    
    def test_one_to_one_relationship(self):
        """Test that each submission can only have one feedback"""
        feedback1 = MentorFeedback.objects.create(
            submission=self.submission,
            mentor=self.mentor,
            feedback='First feedback',
            rating='good'
        )
        
        # Try to create another feedback for the same submission
        with self.assertRaises(Exception):
            MentorFeedback.objects.create(
                submission=self.submission,
                mentor=self.mentor,
                feedback='Second feedback',
                rating='excellent'
            )
    
    def test_rating_choices(self):
        """Test that only valid rating choices are accepted"""
        feedback = MentorFeedback.objects.create(
            submission=self.submission,
            mentor=self.mentor,
            feedback='Test feedback',
            rating='excellent'
        )
        
        self.assertIn(feedback.rating, ['excellent', 'good', 'needs_improvement'])


class WorkSubmissionViewTests(TestCase):
    """Test work submission views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        self.client.login(username='testuser', password='testpass123!')
    
    def test_submission_requires_login(self):
        """Test that submission requires user to be logged in"""
        self.client.logout()
        response = self.client.get(reverse('my_submissions'))
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class MentorFeedbackViewTests(TestCase):
    """Test mentor feedback views"""
    
    def setUp(self):
        self.client = Client()
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123!'
        )
        
        self.mentor = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='pass123!',
            is_staff=True
        )
        
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        self.submission = WorkSubmission.objects.create(
            user=self.student,
            title='Test Project',
            description='Description',
            file=temp_file
        )
    
    def test_only_staff_can_give_feedback(self):
        """Test that only staff members can give feedback"""
        # Login as regular user
        self.client.login(username='student', password='pass123!')
        response = self.client.get(reverse('give_feedback', args=[self.submission.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Login as mentor (staff)
        self.client.login(username='mentor', password='pass123!')
        response = self.client.get(reverse('give_feedback', args=[self.submission.id]))
        self.assertEqual(response.status_code, 200)  # Success
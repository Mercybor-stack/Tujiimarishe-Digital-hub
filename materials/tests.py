from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import Category, Material, UserCategoryPurchase, WorkSubmission, MentorFeedback

User = get_user_model()


class CategoryModelTests(TestCase):
    """Test Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn digital marketing skills',
            is_active=True,
            order=1
        )
    
    def test_category_creation(self):
        """Test creating a category"""
        self.assertEqual(self.category.name, 'Digital Marketing')
        self.assertEqual(self.category.slug, 'digital-marketing')
        self.assertTrue(self.category.is_active)
    
    def test_category_str_method(self):
        """Test Category string representation"""
        self.assertEqual(str(self.category), 'Digital Marketing')
    
    def test_category_ordering(self):
        """Test categories are ordered by order field"""
        category2 = Category.objects.create(
            name='Graphic Design',
            slug='graphic-design',
            description='Learn design',
            order=2,
            is_active=True
        )
        
        categories = Category.objects.all()
        self.assertEqual(categories[0], self.category)
        self.assertEqual(categories[1], category2)


class MaterialModelTests(TestCase):
    """Test Material model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn digital marketing',
            is_active=True
        )
    
    def test_material_creation(self):
        """Test creating a material"""
        material = Material.objects.create(
            category=self.category,
            title='Introduction to SEO',
            description='Learn SEO basics',
            material_type='youtube',
            youtube_url='https://www.youtube.com/watch?v=test123',
            tier='basic',
            is_active=True,
            order=1
        )
        
        self.assertEqual(material.title, 'Introduction to SEO')
        self.assertEqual(material.material_type, 'youtube')
        self.assertEqual(material.tier, 'basic')
    
    def test_material_youtube_embed_url(self):
        """Test YouTube URL conversion to embed format"""
        material = Material.objects.create(
            category=self.category,
            title='YouTube Tutorial',
            material_type='youtube',
            youtube_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            tier='basic',
            is_active=True
        )
        
        embed_url = material.get_youtube_embed_url()
        self.assertEqual(embed_url, 'https://www.youtube.com/embed/dQw4w9WgXcQ')
    
    def test_material_youtube_short_url(self):
        """Test YouTube short URL conversion"""
        material = Material.objects.create(
            category=self.category,
            title='YouTube Tutorial',
            material_type='youtube',
            youtube_url='https://youtu.be/dQw4w9WgXcQ',
            tier='basic',
            is_active=True
        )
        
        embed_url = material.get_youtube_embed_url()
        self.assertEqual(embed_url, 'https://www.youtube.com/embed/dQw4w9WgXcQ')
    
    def test_material_ordering(self):
        """Test materials are ordered by order field"""
        material1 = Material.objects.create(
            category=self.category,
            title='Lesson 1',
            tier='basic',
            material_type='youtube',
            order=1,
            is_active=True
        )
        
        material2 = Material.objects.create(
            category=self.category,
            title='Lesson 2',
            tier='basic',
            material_type='youtube',
            order=2,
            is_active=True
        )
        
        materials = Material.objects.all()
        self.assertEqual(materials[0], material1)
        self.assertEqual(materials[1], material2)


class UserCategoryPurchaseModelTests(TestCase):
    """Test UserCategoryPurchase model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn digital marketing',
            is_active=True
        )
    
    def test_purchase_creation(self):
        """Test creating a purchase"""
        purchase = UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='enterprise',
            amount_paid=Decimal('100.00'),
            payment_status='completed',
            payment_method='mpesa',
            mpesa_receipt_number='ABC123'
        )
        
        self.assertEqual(purchase.tier, 'enterprise')
        self.assertEqual(purchase.amount_paid, Decimal('100.00'))
        self.assertEqual(purchase.payment_status, 'completed')
    
    def test_purchase_str_method(self):
        """Test purchase string representation"""
        purchase = UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='premium',
            amount_paid=Decimal('200.00'),
            payment_status='completed',
            payment_method='mpesa'
        )
        
        self.assertEqual(str(purchase), 'testuser - Digital Marketing (premium)')


class WorkSubmissionModelTests(TestCase):
    """Test WorkSubmission model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123!'
        )
        
        self.category = Category.objects.create(
            name='Graphic Design',
            slug='graphic-design',
            description='Learn design',
            is_active=True
        )
    
    def test_work_submission_creation(self):
        """Test creating a work submission"""
        temp_file = SimpleUploadedFile(
            "project.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        submission = WorkSubmission.objects.create(
            user=self.user,
            category=self.category,
            title='My Design Project',
            description='A beautiful design',
            file=temp_file,
            status='pending'
        )
        
        self.assertEqual(submission.title, 'My Design Project')
        self.assertEqual(submission.status, 'pending')
        self.assertEqual(submission.category, self.category)
    
    def test_submission_status_choices(self):
        """Test submission status choices"""
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        submission = WorkSubmission.objects.create(
            user=self.user,
            category=self.category,
            title='Test',
            description='Test',
            file=temp_file,
            status='reviewed'
        )
        
        self.assertIn(submission.status, ['pending', 'reviewed', 'rejected'])


class MentorFeedbackModelTests(TestCase):
    """Test MentorFeedback model"""
    
    def setUp(self):
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
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
        
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        self.submission = WorkSubmission.objects.create(
            user=self.student,
            category=self.category,
            title='Test Project',
            description='Description',
            file=temp_file,
            status='pending'
        )
    
    def test_mentor_feedback_creation(self):
        """Test creating mentor feedback"""
        feedback = MentorFeedback.objects.create(
            submission=self.submission,
            mentor=self.mentor,
            feedback='Excellent work! Well done.',
            rating='excellent'
        )
        
        self.assertEqual(feedback.rating, 'excellent')
        self.assertEqual(feedback.mentor, self.mentor)


class MaterialsHomeViewTests(TestCase):
    """Test materials home view"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('materials_home')
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
    
    def test_home_page_loads(self):
        """Test home page loads successfully"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Digital Marketing')
    
    def test_inactive_categories_not_shown(self):
        """Test inactive categories are not displayed"""
        inactive_category = Category.objects.create(
            name='Inactive Skill',
            slug='inactive-skill',
            description='This is inactive',
            is_active=False
        )
        
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Inactive Skill')


class CategoryDetailViewTests(TestCase):
    """Test category detail view"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
        
        # Create materials for different tiers
        self.basic_material = Material.objects.create(
            category=self.category,
            title='Basic Lesson',
            tier='basic',
            material_type='youtube',
            youtube_url='https://youtube.com/watch?v=test',
            is_active=True,
            order=1
        )
        
        self.enterprise_material = Material.objects.create(
            category=self.category,
            title='Enterprise Lesson',
            tier='enterprise',
            material_type='youtube',
            youtube_url='https://youtube.com/watch?v=test2',
            is_active=True,
            order=2
        )
        
        self.premium_material = Material.objects.create(
            category=self.category,
            title='Premium Lesson',
            tier='premium',
            material_type='youtube',
            youtube_url='https://youtube.com/watch?v=test3',
            is_active=True,
            order=3
        )
    
    def test_category_detail_loads(self):
        """Test category detail page loads"""
        response = self.client.get(reverse('category_detail', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Digital Marketing')
    
    def test_basic_tier_sees_only_basic_content(self):
        """Test users without purchase see only basic content"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('category_detail', args=[self.category.slug]))
        
        self.assertContains(response, 'Basic Lesson')
        self.assertNotContains(response, 'Enterprise Lesson')
        self.assertNotContains(response, 'Premium Lesson')
    
    def test_enterprise_tier_sees_basic_and_enterprise(self):
        """Test enterprise users see basic and enterprise content"""
        UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='enterprise',
            amount_paid=Decimal('100.00'),
            payment_status='completed',
            payment_method='mpesa'
        )
        
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('category_detail', args=[self.category.slug]))
        
        self.assertContains(response, 'Basic Lesson')
        self.assertContains(response, 'Enterprise Lesson')
        self.assertNotContains(response, 'Premium Lesson')
    
    def test_premium_tier_sees_all_content(self):
        """Test premium users see all content"""
        UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='premium',
            amount_paid=Decimal('200.00'),
            payment_status='completed',
            payment_method='mpesa'
        )
        
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('category_detail', args=[self.category.slug]))
        
        self.assertContains(response, 'Basic Lesson')
        self.assertContains(response, 'Enterprise Lesson')
        self.assertContains(response, 'Premium Lesson')


class PurchaseCategoryViewTests(TestCase):
    """Test purchase category view"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
    
    def test_purchase_requires_login(self):
        """Test purchase page requires login"""
        response = self.client.get(reverse('purchase_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_purchase_page_loads(self):
        """Test purchase page loads for logged in user"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('purchase_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
    
    def test_enterprise_purchase_creates_record(self):
        """Test purchasing enterprise tier creates purchase record"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.post(
            reverse('purchase_category', args=[self.category.slug]),
            {'tier': 'enterprise'}
        )
        
        self.assertEqual(UserCategoryPurchase.objects.count(), 1)
        purchase = UserCategoryPurchase.objects.first()
        self.assertEqual(purchase.tier, 'enterprise')
        self.assertEqual(purchase.amount_paid, Decimal('100.00'))
    
    def test_premium_purchase_creates_record(self):
        """Test purchasing premium tier creates purchase record"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.post(
            reverse('purchase_category', args=[self.category.slug]),
            {'tier': 'premium'}
        )
        
        purchase = UserCategoryPurchase.objects.first()
        self.assertEqual(purchase.tier, 'premium')
        self.assertEqual(purchase.amount_paid, Decimal('200.00'))
    
    def test_invalid_tier_rejected(self):
        """Test invalid tier is rejected"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.post(
            reverse('purchase_category', args=[self.category.slug]),
            {'tier': 'invalid'}
        )
        
        self.assertEqual(UserCategoryPurchase.objects.count(), 0)


class MaterialViewTests(TestCase):
    """Test material view"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
        
        self.basic_material = Material.objects.create(
            category=self.category,
            title='Basic Lesson',
            tier='basic',
            material_type='youtube',
            youtube_url='https://youtube.com/watch?v=test',
            is_active=True
        )
        
        self.premium_material = Material.objects.create(
            category=self.category,
            title='Premium Lesson',
            tier='premium',
            material_type='youtube',
            youtube_url='https://youtube.com/watch?v=test2',
            is_active=True
        )
    
    def test_material_view_requires_login(self):
        """Test material view requires login"""
        response = self.client.get(reverse('material_view', args=[self.basic_material.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_basic_user_can_view_basic_material(self):
        """Test basic tier user can view basic material"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('material_view', args=[self.basic_material.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_basic_user_cannot_view_premium_material(self):
        """Test basic tier user cannot view premium material"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('material_view', args=[self.premium_material.id]))
        self.assertEqual(response.status_code, 302)  # Redirected


class SubmitWorkViewTests(TestCase):
    """Test work submission views"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123!'
        )
        
        self.category = Category.objects.create(
            name='Graphic Design',
            slug='graphic-design',
            description='Learn design',
            is_active=True
        )
    
    def test_submit_work_requires_login(self):
        """Test submit work requires login"""
        response = self.client.get(reverse('submit_work', args=[self.category.slug]))
        self.assertEqual(response.status_code, 302)
    
    def test_basic_user_cannot_submit_work(self):
        """Test basic tier users cannot submit work"""
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('submit_work', args=[self.category.slug]))
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_enterprise_user_can_submit_work(self):
        """Test enterprise users can submit work"""
        UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='enterprise',
            amount_paid=Decimal('100.00'),
            payment_status='completed',
            payment_method='mpesa'
        )
        
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('submit_work', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
    
    def test_premium_user_can_submit_work(self):
        """Test premium users can submit work"""
        UserCategoryPurchase.objects.create(
            user=self.user,
            category=self.category,
            tier='premium',
            amount_paid=Decimal('200.00'),
            payment_status='completed',
            payment_method='mpesa'
        )
        
        self.client.login(username='testuser', password='testpass123!')
        response = self.client.get(reverse('submit_work', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)


class FeedbackViewTests(TestCase):
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
        
        self.category = Category.objects.create(
            name='Digital Marketing',
            slug='digital-marketing',
            description='Learn marketing',
            is_active=True
        )
        
        temp_file = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        
        self.submission = WorkSubmission.objects.create(
            user=self.student,
            category=self.category,
            title='Test Project',
            description='Description',
            file=temp_file,
            status='pending'
        )
    
    def test_all_submissions_requires_staff(self):
        """Test all submissions view requires staff access"""
        self.client.login(username='student', password='pass123!')
        response = self.client.get(reverse('all_submissions'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_staff_can_view_all_submissions(self):
        """Test staff can view all submissions"""
        self.client.login(username='mentor', password='pass123!')
        response = self.client.get(reverse('all_submissions'))
        self.assertEqual(response.status_code, 200)
    
    def test_give_feedback_requires_staff(self):
        """Test giving feedback requires staff access"""
        self.client.login(username='student', password='pass123!')
        response = self.client.get(reverse('give_feedback', args=[self.submission.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_can_give_feedback(self):
        """Test staff can give feedback"""
        self.client.login(username='mentor', password='pass123!')
        response = self.client.get(reverse('give_feedback', args=[self.submission.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_feedback_updates_submission_status(self):
        """Test that giving feedback updates submission status"""
        self.client.login(username='mentor', password='pass123!')
        response = self.client.post(
            reverse('give_feedback', args=[self.submission.id]),
            {
                'feedback': 'Great work!',
                'rating': 'excellent'
            }
        )
        
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, 'reviewed')

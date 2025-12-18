from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import SkillCategory, LearningMaterial, UserSkillAccess, Payment, WorkSubmission, MentorFeedback
from .forms import WorkSubmissionForm, MentorFeedbackForm

# ==================== MATERIALS VIEWS ====================

def material_list(request):
    """Browse all skills and materials"""
    categories = SkillCategory.objects.all().prefetch_related('materials')
    
    # Get user's access levels if logged in
    user_access = {}
    if request.user.is_authenticated:
        access_queryset = UserSkillAccess.objects.filter(user=request.user)
        user_access = {access.category_id: access.access_level for access in access_queryset}
    
    context = {
        'categories': categories,
        'user_access': user_access,
    }
    return render(request, 'materials/my_materials.html', context)


@login_required
def category_detail(request, category_id):
    """View materials for a specific skill category"""
    category = get_object_or_404(SkillCategory, pk=category_id)
    
    # Get user's access level for this category
    user_access_level = 'basic'  # Default (free)
    try:
        access = UserSkillAccess.objects.get(user=request.user, category=category)
        user_access_level = access.access_level
    except UserSkillAccess.DoesNotExist:
        # User has only basic (free) access
        pass
    
    # Get all materials for this category
    all_materials = LearningMaterial.objects.filter(category=category).order_by('order')
    
    # Filter materials based on user's access level
    accessible_materials = []
    locked_materials = []
    
    for material in all_materials:
        if material.access_level == 'basic':
            # Everyone can access basic materials
            accessible_materials.append(material)
        elif material.access_level == 'enterprise':
            if user_access_level in ['enterprise', 'premium']:
                accessible_materials.append(material)
            else:
                locked_materials.append(material)
        elif material.access_level == 'premium':
            if user_access_level == 'premium':
                accessible_materials.append(material)
            else:
                locked_materials.append(material)
    
    # Calculate percentages
    total_materials = all_materials.count()
    accessible_count = len(accessible_materials)
    percentage_unlocked = (accessible_count / total_materials * 100) if total_materials > 0 else 0
    
    context = {
        'category': category,
        'user_access_level': user_access_level,
        'accessible_materials': accessible_materials,
        'locked_materials': locked_materials,
        'total_materials': total_materials,
        'accessible_count': accessible_count,
        'percentage_unlocked': round(percentage_unlocked),
    }
    return render(request, 'materials/category_detail.html', context)


@login_required
def material_detail(request, category_id, material_id):
    """View a specific learning material (video or PDF)"""
    category = get_object_or_404(SkillCategory, pk=category_id)
    material = get_object_or_404(LearningMaterial, pk=material_id, category=category)
    
    # Check user's access level for this category
    user_access_level = 'basic'  # Default
    try:
        access = UserSkillAccess.objects.get(user=request.user, category=material.category)
        user_access_level = access.access_level
    except UserSkillAccess.DoesNotExist:
        pass
    
    # Check if user can access this material
    can_access = False
    if material.access_level == 'basic':
        can_access = True
    elif material.access_level == 'enterprise' and user_access_level in ['enterprise', 'premium']:
        can_access = True
    elif material.access_level == 'premium' and user_access_level == 'premium':
        can_access = True
    
    if not can_access:
        messages.warning(request, f'You need {material.get_access_level_display()} access to view this material.')
        return redirect('materials:checkout', category_id=material.category.id, level=material.access_level)
    
    # Get related materials (same category, excluding current)
    related_materials = LearningMaterial.objects.filter(
        category=material.category
    ).exclude(id=material.id).order_by('order')[:3]
    
    context = {
        'material': material,
        'can_access': can_access,
        'related_materials': related_materials,
    }
    return render(request, 'materials/material_view.html', context)


# ==================== PAYMENT VIEWS ====================

@login_required
def checkout(request, category_id, level):
    """M-Pesa payment checkout page"""
    category = get_object_or_404(SkillCategory, pk=category_id)
    
    # Check if user already has this access level or higher
    try:
        user_access = UserSkillAccess.objects.get(user=request.user, category=category)
        if level == 'enterprise' and user_access.access_level in ['enterprise', 'premium']:
            messages.info(request, 'You already have this access level or higher!')
            return redirect('materials:category_detail', category_id=category_id)
        elif level == 'premium' and user_access.access_level == 'premium':
            messages.info(request, 'You already have premium access!')
            return redirect('materials:category_detail', category_id=category_id)
    except UserSkillAccess.DoesNotExist:
        pass
    
    # Determine price based on level
    prices = {
        'enterprise': 100,
        'premium': 200
    }
    
    if level not in prices:
        messages.error(request, 'Invalid access level')
        return redirect('materials:category_detail', category_id=category_id)
    
    amount = prices[level]
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        mpesa_code = request.POST.get('mpesa_code', '').strip()
        
        # Validation
        errors = []
        
        if not phone_number:
            errors.append('Phone number is required')
        elif len(phone_number) < 10:
            errors.append('Phone number must be at least 10 digits')
        
        if not mpesa_code:
            errors.append('M-Pesa transaction code is required')
        elif len(mpesa_code) < 10:
            errors.append('M-Pesa code must be at least 10 characters')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # ===== M-PESA SIMULATION =====
            # In production, you'd verify with Safaricom Daraja API
            # For now, we accept any valid-looking code
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                category=category,
                access_level=level,
                amount=amount,
                mpesa_code=mpesa_code,
                phone_number=phone_number,
                is_verified=True  # Auto-verify for simulation
            )
            
            # Grant or upgrade access to user
            user_access, created = UserSkillAccess.objects.update_or_create(
                user=request.user,
                category=category,
                defaults={'access_level': level}
            )
            
            messages.success(request, f'🎉 Payment successful! You now have {level.title()} access to {category.name}')
            return redirect('materials:payment_success')
    
    context = {
        'category': category,
        'level': level,
        'level_display': level.title(),
        'amount': amount,
    }
    return render(request, 'materials/checkout.html', context)


@login_required
def payment_success(request):
    """Payment success page"""
    # Get user's most recent payment
    latest_payment = Payment.objects.filter(user=request.user, is_verified=True).first()
    
    context = {
        'latest_payment': latest_payment,
    }
    return render(request, 'materials/payment_success.html', context)


@login_required
def payment_history(request):
    """View all user's payments"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
    }
    return render(request, 'materials/payment_history.html', context)


# ==================== WORK SUBMISSION VIEWS ====================

@login_required
def submit_work(request, category_id=None):
    """View for learners to submit their work"""
    category = None
    if category_id:
        category = get_object_or_404(SkillCategory, pk=category_id)
    
    if request.method == 'POST':
        form = WorkSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            if category:
                submission.category = category
            submission.save()
            messages.success(request, 'Your work has been submitted successfully! A mentor will review it soon.')
            return redirect('materials:my_submissions')
    else:
        form = WorkSubmissionForm()
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'materials/submit_work.html', context)


@login_required
def my_submissions(request):
    """View all submissions by the logged-in user"""
    submissions = WorkSubmission.objects.filter(user=request.user)
    
    context = {
        'submissions': submissions,
    }
    return render(request, 'materials/my_submissions.html', context)


@login_required
def submission_detail(request, pk):
    """View details of a specific submission.

    Staff and mentors can view any submission; learners can view only their own.
    """
    # Allow mentors/staff to view any submission
    is_reviewer = request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'user_type', None) == 'mentor' or request.user.groups.filter(name='mentors').exists())

    if is_reviewer:
        submission = get_object_or_404(WorkSubmission, pk=pk)
    else:
        submission = get_object_or_404(WorkSubmission, pk=pk, user=request.user)

    context = {
        'submission': submission,
        'can_review': is_reviewer,
    }
    return render(request, 'materials/submission_detail.html', context)


@login_required
def review_submission(request, pk):
    """Allow mentors/staff to add or edit feedback and recommendation for a submission"""
    # Only staff or users with a mentor role can review
    if not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'mentor'):
        messages.error(request, 'You do not have permission to review submissions.')
        return redirect('materials:my_submissions')

    submission = get_object_or_404(WorkSubmission, pk=pk)

    # Try to get existing feedback or create a new one
    try:
        feedback = submission.feedback
    except MentorFeedback.DoesNotExist:
        feedback = None

    if request.method == 'POST':
        form = MentorFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.submission = submission
            obj.mentor = request.user
            obj.save()
            # mark submission as reviewed
            submission.is_reviewed = True
            submission.save()
            messages.success(request, 'Feedback saved.')
            return redirect('materials:submission_detail', pk=submission.pk)
    else:
        form = MentorFeedbackForm(instance=feedback)

    context = {
        'submission': submission,
        'form': form,
    }
    return render(request, 'materials/review_submission.html', context)


@login_required
def mentor_dashboard(request):
    """Mentor dashboard showing submissions to review"""
    # Only staff or mentors can access
    if not (request.user.is_staff or getattr(request.user, 'user_type', None) == 'mentor' or request.user.groups.filter(name='mentors').exists()):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Get all submissions, grouped by status
    pending_submissions = WorkSubmission.objects.filter(is_reviewed=False).select_related('user', 'category').order_by('-submitted_at')
    reviewed_submissions = WorkSubmission.objects.filter(is_reviewed=True).select_related('user', 'category', 'feedback__mentor').order_by('-submitted_at')[:10]

    context = {
        'pending_submissions': pending_submissions,
        'reviewed_submissions': reviewed_submissions,
        'pending_count': pending_submissions.count(),
    }
    return render(request, 'materials/mentor_dashboard.html', context)


# ==================== USER DASHBOARD ====================

@login_required
def my_learning(request):
    """User's learning dashboard"""
    # Get all skills user has access to
    user_access = UserSkillAccess.objects.filter(user=request.user).select_related('category')
    
    # Get recent submissions
    recent_submissions = WorkSubmission.objects.filter(user=request.user)[:5]
    
    # Get payment history
    recent_payments = Payment.objects.filter(user=request.user, is_verified=True)[:5]
    
    context = {
        'user_access': user_access,
        'recent_submissions': recent_submissions,
        'recent_payments': recent_payments,
    }
    return render(request, 'materials/my_learning.html', context)

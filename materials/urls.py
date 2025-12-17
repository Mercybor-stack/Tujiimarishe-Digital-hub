from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    # Materials browsing
    path('', views.material_list, name='my_materials'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('material/<int:material_id>/', views.material_detail, name='material_detail'),
    
    # Payments
    path('checkout/<int:category_id>/<str:level>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-history/', views.payment_history, name='payment_history'),
    
    # Work submissions
    path('submit-work/', views.submit_work, name='submit_work'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
    
    # Dashboard
    path('my-learning/', views.my_learning, name='my_learning'),
]

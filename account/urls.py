from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('api/auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    

    path('api/orders/', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('api/orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
   
    path('api/payments/', views.PaymentListCreateView.as_view(), name='payment-list-create'),
    path('api/payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    
    
    path('api/dashboard/', views.dashboard_view, name='dashboard'),
]
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Order, Payment
from .serializers import UserRegistrationSerializer, UserLoginSerializer, OrderSerializer, PaymentSerializer


# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        #generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#protected Order Views
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        #managers can see all orders, others see only their own
        if user.role == 'manager':
            return Order.objects.all()
        return Order.objects.filter(created_by=user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Order.objects.all()
        return Order.objects.filter(created_by=user)

#protected Payment Views
class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['manager', 'cashier']:
            return Payment.objects.all()
        #waiters can only see payments for their orders
        return Payment.objects.filter(order__created_by=user)
    
    def perform_create(self, serializer):
        #only managers and cashiers can process payments
        if self.request.user.role not in ['manager', 'cashier']:
            raise permissions.PermissionDenied("Only managers and cashiers can process payments")
        serializer.save()

class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['manager', 'cashier']:
            return Payment.objects.all()
        return Payment.objects.filter(order__created_by=user)

#dashboard view for managers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    if request.user.role != 'manager':
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_payments = Payment.objects.count()
    total_revenue = sum(p.amount for p in Payment.objects.filter(is_successful=True))
    
    return Response({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_payments': total_payments,
        'total_revenue': float(total_revenue)
    })

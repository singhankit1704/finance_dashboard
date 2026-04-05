from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, LoginSerializer
from .permissions import IsAdmin, IsAnyRole


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data}, status=status_code)


class LoginView(APIView):
    """Login with username/password, returns JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response(
                {"success": False, "message": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {"success": False, "message": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return success_response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }, message="Login successful.")


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/users/  - List all users (Admin only)
    POST /api/users/  - Create a new user (Admin only)
    """
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by role or status if query params provided
        role = request.query_params.get('role')
        is_active = request.query_params.get('is_active')
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        serializer = UserSerializer(queryset, many=True)
        return success_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(UserSerializer(user).data, "User created successfully.", status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/<id>/  - Get user detail (Admin only)
    PATCH  /api/users/<id>/  - Update role/status (Admin only)
    DELETE /api/users/<id>/  - Deactivate user (Admin only, soft delete)
    """
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return success_response(UserSerializer(user).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(UserSerializer(user).data, "User updated successfully.")

    def destroy(self, request, *args, **kwargs):
        """Soft delete — deactivate instead of hard delete."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {"success": False, "message": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = False
        user.save()
        return success_response(message="User deactivated successfully.")


class MeView(APIView):
    """GET /api/users/me/ - Get currently logged-in user's profile."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        return success_response(UserSerializer(request.user).data)

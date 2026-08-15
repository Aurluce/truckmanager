from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    ChangePasswordView, UserListView, UserCreateView, UserDetailView, PromoteUserView
)

urlpatterns = [
    # Authentification
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('core/logout/', LogoutView.as_view(), name='core_logout'),
    
    # Tokens JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Profil utilisateur
    path('profile/', ProfileView.as_view(), name='profile'),
    path('core/profile/', ProfileView.as_view(), name='core_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('core/change-password/', ChangePasswordView.as_view(), name='core_change_password'),
    
    # Gestion des utilisateurs (Admin)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/promote/', PromoteUserView.as_view(), name='promote_user'),
]

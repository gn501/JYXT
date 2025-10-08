# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views_test import SimpleTemplateView
from .views_simple import VerySimpleTemplateView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    # 测试视图
    path('test-template/', SimpleTemplateView.as_view(), name='test_template'),
    # 非常简单的测试视图，不要求登录
    path('very-simple/', VerySimpleTemplateView.as_view(), name='very_simple'),
]
# enterprises/urls.py
from django.urls import path
from . import views

app_name = 'enterprises'

urlpatterns = [
    # 企业管理相关URL
    path('', views.EnterpriseListView.as_view(), name='enterprise_list'),
    path('create/', views.EnterpriseCreateView.as_view(), name='enterprise_create'),
    path('<int:pk>/', views.EnterpriseDetailView.as_view(), name='enterprise_detail'),
    path('<int:pk>/update/', views.EnterpriseUpdateView.as_view(), name='enterprise_update'),
    path('select/', views.SelectEnterpriseView.as_view(), name='select_enterprise'),
    path('subscriptions/<int:pk>/', views.EnterpriseSubscriptionView.as_view(), name='subscription_update'),
    
    # 部门管理相关URL
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
]
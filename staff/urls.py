from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffListView.as_view(), name='staff_list'),
    path('create/', views.StaffCreateView.as_view(), name='staff_create'),
    path('update/<int:pk>/', views.StaffUpdateView.as_view(), name='staff_update'),
    path('detail/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('delete/<int:pk>/', views.StaffDeleteView.as_view(), name='staff_delete'),
    path('profile/', views.StaffProfileView.as_view(), name='staff_profile'),
]
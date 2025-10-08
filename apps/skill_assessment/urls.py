# apps/skill_assessment/urls.py
from django.urls import path
from . import views
from . import admin_views

app_name = 'skill_assessment'

urlpatterns = [
    # 用户功能
    path('', views.SkillAssessmentDashboardView.as_view(), name='dashboard'),
    
    # 技能标准
    path('skill-standards/', views.SkillStandardListView.as_view(), name='skill_standard_list'),
    path('skill-standards/create/', views.SkillStandardCreateView.as_view(), name='skill_standard_create'),
    path('skill-standards/<int:pk>/', views.SkillStandardDetailView.as_view(), name='skill_standard_detail'),
    path('skill-standards/<int:pk>/update/', views.SkillStandardUpdateView.as_view(), name='skill_standard_update'),
    
    # 认定计划
    path('assessment-plans/', views.AssessmentPlanListView.as_view(), name='assessment_plan_list'),
    path('assessment-plans/create/', views.AssessmentPlanCreateView.as_view(), name='assessment_plan_create'),
    path('assessment-plans/<int:pk>/', views.AssessmentPlanDetailView.as_view(), name='assessment_plan_detail'),
    path('assessment-plans/<int:pk>/update/', views.AssessmentPlanUpdateView.as_view(), name='assessment_plan_update'),
    
    # 认定记录 - 暂时注释，因为相关视图已禁用
    # path('assessment-records/', views.AssessmentRecordListView.as_view(), name='assessment_record_list'),
    # path('assessment-records/create/', views.AssessmentRecordCreateView.as_view(), name='assessment_record_create'),
    # path('assessment-records/<int:pk>/update/', views.AssessmentRecordUpdateView.as_view(), name='assessment_record_update'),
    
    # 统计分析
    path('statistics/', views.AssessmentStatisticsView.as_view(), name='statistics'),
    
    # 管理功能（系统管理员和应用管理员）
    path('management/enterprise-profiles/', admin_views.SkillAssessmentEnterpriseProfileListView.as_view(), 
         name='enterprise_profile_list'),
    path('management/enterprise-profiles/create/', admin_views.SkillAssessmentEnterpriseProfileCreateView.as_view(), 
         name='enterprise_profile_create'),
    path('management/enterprise-profiles/<int:pk>/update/', admin_views.SkillAssessmentEnterpriseProfileUpdateView.as_view(), 
         name='enterprise_profile_update'),
    
    # 配置管理
    path('management/configs/', admin_views.SkillAssessmentConfigListView.as_view(), name='config_list'),
    path('management/configs/<int:pk>/update/', admin_views.SkillAssessmentConfigUpdateView.as_view(), name='config_update'),
    
    # 管理机构仪表盘
    path('management/dashboard/', admin_views.ManagementDashboardView.as_view(), name='management_dashboard'),
]
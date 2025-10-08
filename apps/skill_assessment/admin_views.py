# apps/skill_assessment/admin_views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from JYXT.core.permissions import SuperUserRequiredMixin, AppAdminRequiredMixin
from .models import SkillAssessmentEnterpriseProfile, SkillAssessmentConfig
from enterprises.models import Enterprise

class SkillAssessmentEnterpriseProfileListView(LoginRequiredMixin, ListView):
    """职业技能认定企业档案列表"""
    model = SkillAssessmentEnterpriseProfile
    template_name = 'skill_assessment/enterprise_profile_list.html'
    context_object_name = 'profiles'
    
    def get_queryset(self):
        user = self.request.user
        
        # 系统管理员可以看到所有档案
        if user.is_superuser:
            return SkillAssessmentEnterpriseProfile.objects.all()
        
        # 应用管理员（如管理机构）可以看到相关档案
        # 这里可以根据具体业务逻辑扩展
        return SkillAssessmentEnterpriseProfile.objects.none()

class SkillAssessmentEnterpriseProfileCreateView(SuperUserRequiredMixin, CreateView):
    """创建职业技能认定企业档案"""
    model = SkillAssessmentEnterpriseProfile
    template_name = 'skill_assessment/enterprise_profile_form.html'
    fields = ['enterprise', 'contact_person', 'contact_phone', 'contact_email', 
              'org_type', 'evaluation_subtype', 'qualification_number', 
              'qualification_date', 'qualification_expiry', 'business_scope']
    
    def get_success_url(self):
        messages.success(self.request, "职业技能认定企业档案创建成功")
        return reverse_lazy('skill_assessment:enterprise_profile_list')
    
    def form_valid(self, form):
        # 检查是否已存在该企业的档案
        enterprise = form.cleaned_data['enterprise']
        if SkillAssessmentEnterpriseProfile.objects.filter(enterprise=enterprise).exists():
            messages.error(self.request, "该企业已存在职业技能认定档案")
            return self.form_invalid(form)
        
        return super().form_valid(form)

class SkillAssessmentEnterpriseProfileUpdateView(LoginRequiredMixin, UpdateView):
    """更新职业技能认定企业档案"""
    model = SkillAssessmentEnterpriseProfile
    template_name = 'skill_assessment/enterprise_profile_form.html'
    fields = ['contact_person', 'contact_phone', 'contact_email', 
              'org_type', 'evaluation_subtype', 'qualification_number', 
              'qualification_date', 'qualification_expiry', 'business_scope']
    
    def get_success_url(self):
        messages.success(self.request, "职业技能认定企业档案更新成功")
        return reverse_lazy('skill_assessment:enterprise_profile_list')
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SkillAssessmentEnterpriseProfile.objects.all()
        
        # 非系统管理员只能修改自己有权限的档案
        # 这里可以根据具体业务逻辑扩展
        return SkillAssessmentEnterpriseProfile.objects.none()

class SkillAssessmentConfigListView(LoginRequiredMixin, ListView):
    """职业技能认定配置列表"""
    model = SkillAssessmentConfig
    template_name = 'skill_assessment/config_list.html'
    context_object_name = 'configs'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SkillAssessmentConfig.objects.all()
        else:
            # 非系统管理员只能看到非系统配置
            return SkillAssessmentConfig.objects.filter(is_system=False)

class SkillAssessmentConfigUpdateView(LoginRequiredMixin, UpdateView):
    """更新职业技能认定配置"""
    model = SkillAssessmentConfig
    template_name = 'skill_assessment/config_form.html'
    fields = ['value', 'description']
    
    def get_success_url(self):
        messages.success(self.request, "配置更新成功")
        return reverse_lazy('skill_assessment:config_list')
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SkillAssessmentConfig.objects.all()
        else:
            # 非系统管理员只能修改非系统配置
            return SkillAssessmentConfig.objects.filter(is_system=False)

class ManagementDashboardView(AppAdminRequiredMixin, ListView):
    """管理机构仪表盘"""
    template_name = 'skill_assessment/management_dashboard.html'
    
    def get_queryset(self):
        # 返回管理机构需要处理的数据
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 管理机构可以看到所有评价机构的信息
        evaluation_orgs = SkillAssessmentEnterpriseProfile.objects.filter(
            org_type='evaluation_org'
        )
        context['evaluation_orgs'] = evaluation_orgs
        
        # 其他管理机构需要的数据
        return context
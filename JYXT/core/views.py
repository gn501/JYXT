# JYXT/core/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class BaseView(LoginRequiredMixin):
    """基础视图类"""
    pass

class EnterpriseRequiredMixin(UserPassesTestMixin):
    """需要企业上下文的视图"""
    
    def test_func(self):
        return hasattr(self.request, 'enterprise') and self.request.enterprise is not None
    
    def handle_no_permission(self):
        messages.error(self.request, "请先选择或创建企业")
        return redirect('enterprises:enterprise_list')

class SuperAdminRequiredMixin(UserPassesTestMixin):
    """需要超级管理员权限的视图"""
    
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, 'is_super_admin', False)
    
    def handle_no_permission(self):
        messages.error(self.request, "需要超级管理员权限")
        return redirect('dashboard')

class EnterpriseAdminRequiredMixin(UserPassesTestMixin):
    """需要企业管理员权限的视图"""
    
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user, 'is_enterprise_admin', False)
    
    def handle_no_permission(self):
        messages.error(self.request, "需要管理员权限")
        return redirect('dashboard')

# 删除或注释掉有问题的多租户视图基类，先使用简单版本
# class TenantAwareListView(BaseView, EnterpriseRequiredMixin, ListView):
#     """多租户列表视图基类"""
#     pass
# ... 其他多租户视图类
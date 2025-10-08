# JYXT/core/permissions.py
from django.contrib.auth.mixins import UserPassesTestMixin

class SuperUserRequiredMixin(UserPassesTestMixin):
    """需要系统管理员权限（Django的is_superuser）"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        
        if self.request.user.is_authenticated:
            messages.error(self.request, "需要系统管理员权限才能访问此页面")
            return redirect('dashboard')
        else:
            return redirect('accounts:login')

class EnterpriseAdminRequiredMixin(UserPassesTestMixin):
    """需要企业管理员权限"""
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        # 系统管理员有所有权限
        if user.is_superuser:
            return True
        
        # 企业管理员需要有企业关联
        return user.is_authenticated and user.is_enterprise_admin
    
    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        
        if self.request.user.is_authenticated:
            messages.error(self.request, "需要企业管理员权限才能访问此页面")
            return redirect('dashboard')
        else:
            return redirect('accounts:login')

class EnterpriseRequiredMixin(UserPassesTestMixin):
    """需要企业上下文"""
    
    def test_func(self):
        return hasattr(self.request, 'enterprise') and self.request.enterprise is not None
    
    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        
        messages.error(self.request, "请先选择或创建企业")
        return redirect('enterprises:select_enterprise')

class AppAdminRequiredMixin(UserPassesTestMixin):
    """需要应用管理员权限"""
    
    def __init__(self, app_code=None, *args, **kwargs):
        self.app_code = app_code
        super().__init__(*args, **kwargs)
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        # 系统管理员有所有权限
        if user.is_superuser:
            return True
        
        # 检查用户是否有特定应用的管理权限
        # 这里可以根据应用特定逻辑来判断
        if self.app_code == 'skill_assessment':
            # 例如，职业技能等级认定应用中，管理机构有管理权限
            enterprise = getattr(self.request, 'enterprise', None)
            if enterprise:
                from enterprises.models import EnterpriseAppProfile
                try:
                    profile = EnterpriseAppProfile.objects.get(
                        enterprise=enterprise,
                        app_code=self.app_code
                    )
                    return profile.org_type == 'management'
                except EnterpriseAppProfile.DoesNotExist:
                    return False
        
        return False
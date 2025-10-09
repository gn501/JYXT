# JYXT/views.py
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from JYXT.core.views import BaseView, EnterpriseRequiredMixin

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """系统仪表盘"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        user = request.user
        
        # 优先使用session中存储的企业ID（用户选择的企业）
        from enterprises.models import Enterprise
        from staff.models import Staff
        if 'current_enterprise_id' in request.session:
            try:
                # 验证用户是否在该企业有在职记录
                staff = user.staff_members.get(
                    enterprise_id=request.session['current_enterprise_id'],
                    employment_status=Staff.EMPLOYED
                )
                # 如果验证通过，获取企业信息
                current_enterprise = Enterprise.objects.get(id=request.session['current_enterprise_id'])
                context['current_enterprise'] = current_enterprise
            except (Staff.DoesNotExist, Enterprise.DoesNotExist):
                # 如果session中的企业不存在或用户已不在该企业任职，清除session并回退到用户默认企业
                if 'current_enterprise_id' in request.session:
                    del request.session['current_enterprise_id']
                pass
        
        # 如果session中没有有效的企业ID，再从用户对象获取默认在职企业
        if 'current_enterprise' not in context or not context['current_enterprise']:
            # 获取用户的在职企业
            employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
            if employed_staffs.exists():
                # 选择第一个在职企业作为默认企业
                context['current_enterprise'] = employed_staffs.first().enterprise
            else:
                context['current_enterprise'] = getattr(request, 'enterprise', None)
        
        return context

@method_decorator(login_required, name='dispatch')
class EnterpriseDashboardView(EnterpriseRequiredMixin, TemplateView):
    """企业仪表盘"""
    template_name = 'enterprises/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        user = request.user
        
        # 优先使用session中存储的企业ID（用户选择的企业）
        from enterprises.models import Enterprise
        from staff.models import Staff
        if 'current_enterprise_id' in request.session:
            try:
                # 验证用户是否在该企业有在职记录
                staff = user.staff_members.get(
                    enterprise_id=request.session['current_enterprise_id'],
                    employment_status=Staff.EMPLOYED
                )
                # 如果验证通过，获取企业信息
                current_enterprise = Enterprise.objects.get(id=request.session['current_enterprise_id'])
                context['current_enterprise'] = current_enterprise
            except (Staff.DoesNotExist, Enterprise.DoesNotExist):
                # 如果session中的企业不存在或用户已不在该企业任职，清除session并回退到用户默认企业
                if 'current_enterprise_id' in request.session:
                    del request.session['current_enterprise_id']
                pass
        
        # 如果session中没有有效的企业ID，再从用户对象获取默认在职企业
        if 'current_enterprise' not in context or not context['current_enterprise']:
            # 获取用户的在职企业
            employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
            if employed_staffs.exists():
                # 选择第一个在职企业作为默认企业
                context['current_enterprise'] = employed_staffs.first().enterprise
            else:
                context['current_enterprise'] = getattr(request, 'enterprise', None)
        
        return context
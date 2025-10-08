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
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context

@method_decorator(login_required, name='dispatch')
class EnterpriseDashboardView(EnterpriseRequiredMixin, TemplateView):
    """企业仪表盘"""
    template_name = 'enterprises/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context
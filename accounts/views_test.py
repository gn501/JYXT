from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class SimpleTemplateView(LoginRequiredMixin, TemplateView):
    """简单的测试视图，用于验证模板渲染是否正常工作"""
    template_name = 'accounts/test_template.html'
from django.views.generic import TemplateView

class VerySimpleTemplateView(TemplateView):
    """非常简单的测试视图，不要求登录"""
    template_name = 'accounts/very_simple_template.html'
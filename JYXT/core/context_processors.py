# JYXT/core/context_processors.py
from .registry import app_registry
from django.conf import settings

def app_registry_processor(request):
    """将应用注册表和系统设置添加到模板上下文"""
    current_enterprise = getattr(request, 'enterprise', None)
    available_apps = app_registry.get_available_apps(current_enterprise)
    
    return {
        'app_registry': app_registry,
        'available_apps': available_apps,
        'current_enterprise': current_enterprise,
        # 系统信息设置
        'SYSTEM_NAME': getattr(settings, 'SYSTEM_NAME', '景云系统'),
        'DEFAULT_PAGE_TITLE': getattr(settings, 'DEFAULT_PAGE_TITLE', '景云系统'),
        'TITLE_SEPARATOR': getattr(settings, 'TITLE_SEPARATOR', ' - '),
    }
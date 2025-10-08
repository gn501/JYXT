# JYXT/core/templatetags/app_tags.py
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def page_title(context, page_title=None):
    """统一页面标题格式的模板标签
    
    用法:
        {% page_title "页面标题" %}
        
    如果不提供页面标题，则返回默认系统标题
    """
    # 从上下文获取系统名称设置，如果没有则从settings中获取默认值
    system_name = context.get('SYSTEM_NAME', getattr(settings, 'SYSTEM_NAME', '景云系统'))
    title_separator = context.get('TITLE_SEPARATOR', getattr(settings, 'TITLE_SEPARATOR', ' - '))
    
    if not page_title:
        return system_name
    
    return f"{page_title}{title_separator}{system_name}"


@register.filter(name='with_system_name')
def with_system_name(value, separator=None):
    """将任意文本与系统名称组合的过滤器
    
    用法:
        {{ '页面标题'|with_system_name }}
        或指定分隔符:
        {{ '页面标题'|with_system_name:':' }}
    """
    system_name = getattr(settings, 'SYSTEM_NAME', '景云系统')
    sep = separator if separator is not None else getattr(settings, 'TITLE_SEPARATOR', ' - ')
    
    if not value:
        return system_name
    
    return f"{value}{sep}{system_name}"
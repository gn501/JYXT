# JYXT/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'JYXT.core'
    verbose_name = '核心功能'

    def ready(self):
        # 应用启动时的初始化代码
        # 导入templatetags以确保标签库被注册
        import JYXT.core.templatetags.app_tags
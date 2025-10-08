# apps/skill_assessment/apps.py
from django.apps import AppConfig
from JYXT.core.registry import app_registry

class SkillAssessmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.skill_assessment'
    verbose_name = '职业技能等级认定'

    def ready(self):
        # 注册应用到注册表
        from .app_config import SkillAssessmentConfig as AppConfig
        app_registry.register('skill_assessment', AppConfig)
# JYXT/core/management/commands/init_system.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = '初始化系统'
    
    def handle(self, *args, **options):
        # 1. 确保至少有一个系统管理员
        self.init_superuser()
        
        # 2. 初始化职业技能等级认定应用配置
        self.init_skill_assessment_configs()
        
        self.stdout.write(
            self.style.SUCCESS('系统初始化完成')
        )
    
    def init_superuser(self):
        """初始化系统管理员"""
        if not User.objects.filter(is_superuser=True).exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS(f'系统管理员创建成功: admin/admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('系统管理员已存在')
            )
    
    def init_skill_assessment_configs(self):
        """初始化职业技能等级认定配置"""
        from apps.skill_assessment.models import SkillAssessmentConfig
        
        default_configs = [
            ('max_assessment_duration', '30', '最大认定时长（天）', False),
            ('certificate_template', 'default', '证书模板', False),
            ('min_participants', '10', '最小参与人数', False),
            ('system_version', '1.0.0', '系统版本', True),
        ]
        
        for key, value, description, is_system in default_configs:
            SkillAssessmentConfig.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'is_system': is_system
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS('职业技能等级认定配置初始化完成')
        )
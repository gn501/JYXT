# JYXT/core/app_config.py
class AppConfig:
    """应用配置基类"""
    
    def __init__(self, app_code, name, description):
        self.app_code = app_code
        self.name = name
        self.description = description
        self.enterprise_profile_model = None  # 企业扩展信息模型
        self.config_model = None  # 应用配置模型
        self.admin_roles = []  # 应用管理员角色
    
    def set_enterprise_profile_model(self, model):
        """设置企业扩展信息模型"""
        self.enterprise_profile_model = model
    
    def set_config_model(self, model):
        """设置应用配置模型"""
        self.config_model = model
    
    def add_admin_role(self, role_code, role_name):
        """添加应用管理员角色"""
        self.admin_roles.append({
            'code': role_code,
            'name': role_name
        })

# 职业技能等级认定应用配置
class SkillAssessmentConfig(AppConfig):
    def __init__(self):
        super().__init__(
            app_code='skill_assessment',
            name='职业技能等级认定',
            description='企业职业技能等级认定管理平台'
        )
        
        # 设置模型
        from apps.skill_assessment.models import SkillAssessmentEnterpriseProfile, SkillAssessmentConfig as ConfigModel
        self.set_enterprise_profile_model(SkillAssessmentEnterpriseProfile)
        self.set_config_model(ConfigModel)
        
        # 定义管理员角色
        self.add_admin_role('management', '管理机构')

# 应用注册表
app_registry = {}

def register_app(app_config):
    """注册应用"""
    app_registry[app_config.app_code] = app_config

# 注册应用
register_app(SkillAssessmentConfig())
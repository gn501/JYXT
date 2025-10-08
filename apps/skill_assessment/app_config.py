# apps/skill_assessment/app_config.py
from JYXT.core.registry import BaseAppConfig

class SkillAssessmentConfig(BaseAppConfig):
    """职业技能等级认定应用配置"""
    
    name = "职业技能等级认定"
    code = "skill_assessment"
    description = "企业职业技能等级认定管理平台"
    version = "1.0.0"
    
    # 菜单配置
    menu_items = [
        {
            'name': '认定管理',
            'icon': 'fas fa-graduation-cap',
            'items': [
                {
                    'name': '认定计划',
                    'url': 'skill_assessment:assessment_plan_list',
                    'permission': 'skill_assessment.view_assessmentplan',
                },
                # 暂时注释，因为相关视图已禁用
                # {
                #     'name': '认定记录',
                #     'url': 'skill_assessment:assessment_record_list',
                #     'permission': 'skill_assessment.view_assessmentrecord',
                # },
                {
                    'name': '技能标准',
                    'url': 'skill_assessment:skill_standard_list',
                    'permission': 'skill_assessment.view_skillstandard',
                },
            ]
        },
        {
            'name': '统计分析',
            'icon': 'fas fa-chart-bar',
            'items': [
                {
                    'name': '认定统计',
                    'url': 'skill_assessment:statistics',
                    'permission': 'skill_assessment.view_reports',  # 修改为使用查看报告权限
                },
            ]
        },
    ]
    
    # 权限定义
    permissions = [
        ('skill_assessment.manage_assessment', '管理职业技能认定'),
        ('skill_assessment.view_reports', '查看认定报告'),
    ]

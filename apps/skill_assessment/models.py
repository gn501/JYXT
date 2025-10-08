# apps/skill_assessment/models.py
from django.db import models
from enterprises.models import Enterprise

class SkillAssessmentEnterpriseProfile(models.Model):
    """企业在职业技能等级认定应用中的扩展信息"""
    
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name='企业')
    
    # 应用联系人信息
    contact_person = models.CharField('认定业务联系人', max_length=100, blank=True)
    contact_phone = models.CharField('认定联系电话', max_length=20, blank=True)
    contact_email = models.EmailField('认定联系邮箱', blank=True)
    
    # 机构类型
    ORG_TYPE_CHOICES = [
        ('management', '管理机构'),
        ('agent', '代理商'),
        ('assessment_site', '考核点'),
        ('evaluation_org', '职业技能等级评价机构'),
    ]
    
    EVALUATION_SUBTYPE_CHOICES = [
        ('employer', '用人单位'),
        ('training_org', '社会培训评价组织'),
        ('technical_school', '技工院校'),
    ]
    
    org_type = models.CharField('机构类型', max_length=20, choices=ORG_TYPE_CHOICES, blank=True)
    evaluation_subtype = models.CharField('评价机构子类型', max_length=20, choices=EVALUATION_SUBTYPE_CHOICES, blank=True)
    
    # 资质信息
    qualification_number = models.CharField('资质编号', max_length=100, blank=True)
    qualification_date = models.DateField('资质获得日期', null=True, blank=True)
    qualification_expiry = models.DateField('资质有效期至', null=True, blank=True)
    
    # 业务范围
    business_scope = models.TextField('认定业务范围', blank=True)
    
    # 应用特定配置
    config = models.JSONField('应用配置', default=dict, blank=True)
    
    class Meta:
        db_table = 'skill_assessment_enterprise_profiles'
        verbose_name = '职业技能认定企业档案'
        verbose_name_plural = '职业技能认定企业档案管理'
        unique_together = ['enterprise']
    
    def __str__(self):
        return f"{self.enterprise.name} - 职业技能认定档案"
    
    @property
    def is_management_org(self):
        """是否是管理机构"""
        return self.org_type == 'management'
    
    @property
    def is_evaluation_org(self):
        """是否是评价机构"""
        return self.org_type == 'evaluation_org'

class SkillAssessmentConfig(models.Model):
    """职业技能等级认定应用配置"""
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    description = models.TextField('描述', blank=True)
    is_system = models.BooleanField('系统配置', default=False)
    
    class Meta:
        db_table = 'skill_assessment_config'
        verbose_name = '职业技能认定配置'
        verbose_name_plural = '职业技能认定配置管理'
    
    def __str__(self):
        return self.key

# 职业技能等级认定相关的其他模型
class SkillStandard(models.Model):
    """技能标准"""
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name='企业')
    name = models.CharField('技能名称', max_length=100)
    code = models.CharField('技能代码', max_length=50)
    description = models.TextField('技能描述', blank=True)
    level = models.CharField('等级', max_length=50)
    
    class Meta:
        db_table = 'skill_standards'
        verbose_name = '技能标准'
        verbose_name_plural = '技能标准管理'
    
    def __str__(self):
        return f"{self.name} ({self.level})"

class AssessmentPlan(models.Model):
    """认定计划"""
    PLAN_STATUS = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]
    
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name='企业')
    title = models.CharField('计划标题', max_length=200)
    skill_standard = models.ForeignKey(SkillStandard, on_delete=models.CASCADE, verbose_name='技能标准')
    plan_date = models.DateField('计划日期')
    
    class Meta:
        db_table = 'assessment_plans'
        verbose_name = '认定计划'
        verbose_name_plural = '认定计划管理'
    
    def __str__(self):
        return self.title
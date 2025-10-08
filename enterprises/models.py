# enterprises/models.py
from django.db import models
from django.core.validators import RegexValidator

class Department(models.Model):
    """企业部门模型"""
    
    # 部门名称验证器
    name_validator = RegexValidator(
        regex=r'^[^!@#$%^&*(),.?":{}|<>]+$',
        message="部门名称不能包含特殊字符"
    )
    
    # 部门名称
    name = models.CharField(
        '部门名称', 
        max_length=100,
        validators=[name_validator],
        help_text='部门的中文名称，不能包含特殊字符'
    )
    
    # 部门编码（可选，用于企业内部系统集成）
    code = models.CharField(
        '部门编码', 
        max_length=50,
        blank=True,
        null=True,
        help_text='企业内部的部门编码，可选'
    )
    
    # 所属企业
    enterprise = models.ForeignKey(
        'Enterprise',
        on_delete=models.CASCADE,
        verbose_name='所属企业',
        related_name='departments'
    )
    
    # 上级部门（支持层级结构）
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name='上级部门',
        blank=True,
        null=True,
        related_name='children'
    )
    
    # 部门负责人
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        verbose_name='部门负责人',
        blank=True,
        null=True,
        related_name='managed_departments'
    )
    
    # 部门描述
    description = models.TextField(
        '部门描述',
        blank=True,
        null=True,
        help_text='部门的职责、权限等描述信息'
    )
    
    # 系统状态
    is_active = models.BooleanField(
        '是否启用',
        default=True,
        help_text='停用后，部门将不会在列表中显示'
    )
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'departments'
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        unique_together = ['name', 'enterprise', 'parent']  # 确保同一企业下同一父部门中部门名称唯一
        ordering = ['name']
    
    def __str__(self):
        # 显示完整的部门路径，包括父部门
        if self.parent:
            return f"{self.parent} - {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """获取部门的完整路径，如：公司总部 - 技术部 - 前端开发组"""
        if self.parent:
            return f"{self.parent.full_path} - {self.name}"
        return self.name
    
    def get_all_children(self):
        """获取所有子部门（包括子部门的子部门）"""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_department_users(self):
        """获取该部门及其所有子部门的用户"""
        from accounts.models import User
        from staff.models import Staff
        
        # 获取当前部门的用户
        staff_members = Staff.objects.filter(department=self, enterprise=self.enterprise)
        user_ids = staff_members.values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids)
        
        # 获取所有子部门的用户
        for child in self.get_all_children():
            child_staff_members = Staff.objects.filter(department=child, enterprise=self.enterprise)
            child_user_ids = child_staff_members.values_list('user_id', flat=True)
            users = users | User.objects.filter(id__in=child_user_ids)
        
        return users

class Enterprise(models.Model):
    """企业模型 - 基于营业执照信息"""
    
    # 企业类型选择
    ENTERPRISE_TYPE = [
        ('limited_liability_company_natural', '有限责任公司（自然人投资或控股）'),
        ('limited_liability_company_state', '有限责任公司（国有独资）'),
        ('joint_stock_limited_company', '股份有限公司'),
        ('social_group', '社会团体法人'),
        ('private_non_enterprise', '民办非企业单位'),
        ('individual_enterprise', '个体工商户'),
        ('other', '其他'),
    ]
    
    # 营业执照基础信息
    name = models.CharField('企业名称', max_length=200, unique=True)
    unified_social_credit_code = models.CharField('统一社会信用代码', max_length=18, unique=True)
    enterprise_type = models.CharField('企业类型', max_length=100, choices=ENTERPRISE_TYPE, null=True, blank=True)
    registered_address = models.TextField('注册地址', null=True, blank=True)
    legal_representative = models.CharField('法定代表人', max_length=100, null=True, blank=True)
    registered_capital = models.DecimalField('注册资本', max_digits=15, decimal_places=4, null=True, blank=True)
    establishment_date = models.DateField('成立日期', null=True, blank=True)
    business_term_start = models.DateField('营业期限开始', null=True, blank=True)
    business_term_end = models.DateField('营业期限结束', null=True, blank=True)  # 空表示长期
    registration_authority = models.CharField('登记机关', max_length=200, null=True, blank=True)
    business_scope = models.TextField('经营范围', null=True, blank=True)
    
    # 联系信息
    contact_address = models.TextField('联系地址', null=True, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, null=True, blank=True)
    contact_email = models.EmailField('联系邮箱', null=True, blank=True)
    
    # 企业网站和LOGO
    website = models.URLField('企业网站', null=True, blank=True)
    logo = models.ImageField('企业LOGO', upload_to='enterprise_logos/', null=True, blank=True)
    
    # 系统状态
    is_active = models.BooleanField('是否激活', default=True)
    max_users = models.IntegerField('最大用户数', default=10)
    subscription_tier = models.CharField('订阅等级', max_length=50, default='basic')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'enterprises'
        verbose_name = '企业'
        verbose_name_plural = '企业管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.unified_social_credit_code})"
    
    @property
    def is_long_term(self):
        """是否长期有效"""
        return self.business_term_end is None

    def generate_admin_username(self):
        """生成企业管理员用户名 jyxxxx（xxxx是1000-9999的随机数）"""
        import random
        
        # 根据用户要求，直接生成jyxxxx格式的用户名（xxxx是1000-9999的随机数）
        base_username = f"jy{random.randint(1000, 9999)}"
        username = base_username
        
        # 如果用户名已存在，添加随机后缀或重新生成
        counter = 1
        from accounts.models import User
        while User.objects.filter(username=username).exists():
            # 重新生成一个随机数
            random_suffix = random.randint(1000, 9999)
            username = f"jy{random_suffix}"
            counter += 1
            if counter > 10:  # 防止无限循环
                # 添加额外的随机数后缀
                extra_suffix = random.randint(10, 99)
                username = f"jy{random_suffix}_{extra_suffix}"
                break
        
        return username

class EnterpriseSubscription(models.Model):
    """企业应用订阅关系"""
    SUBSCRIPTION_STATUS = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('suspended', '暂停'),
        ('expired', '过期'),
    ]
    
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name='企业')
    app_code = models.CharField('应用代码', max_length=50)
    status = models.CharField('状态', max_length=20, choices=SUBSCRIPTION_STATUS, default='inactive')
    subscribed_at = models.DateTimeField('订阅时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    config = models.JSONField('配置', default=dict, blank=True)
    
    class Meta:
        db_table = 'enterprise_subscriptions'
        verbose_name = '企业订阅'
        verbose_name_plural = '企业订阅管理'
        unique_together = ['enterprise', 'app_code']
    
    def __str__(self):
        return f"{self.enterprise.name} - {self.app_code}"
    
    @property
    def is_active(self):
        """检查订阅是否有效"""
        from django.utils import timezone
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
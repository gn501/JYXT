# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class User(AbstractUser):
    """用户认证模型 - 存储个人基本信息和认证相关信息"""
    
    # 定义用户类型常量 - 只包含系统用户类型，不包含超级管理员
    ENTERPRISE_ADMIN = 'enterprise_admin'
    ENTERPRISE_USER = 'enterprise_user'
    INDEPENDENT_USER = 'independent_user'  # 独立用户（如微信小程序注册）
    
    USER_TYPE_CHOICES = [
        (ENTERPRISE_ADMIN, '企业管理员'),
        (ENTERPRISE_USER, '企业用户'),
        (INDEPENDENT_USER, '独立用户'),
    ]
    
    # 用户类型 - 保留在认证模型中以便快速权限检查
    user_type = models.CharField('用户类型', max_length=20, choices=USER_TYPE_CHOICES, default=ENTERPRISE_USER)
    
    # 个人基本信息
    first_name = models.CharField('姓名', max_length=30, blank=True)
    last_name = models.CharField('昵称', max_length=30, blank=True)
    phone = models.CharField('个人手机号', max_length=20, blank=True)
    email = models.EmailField('个人邮箱', blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    
    # 微信相关认证字段
    wechat_openid = models.CharField('微信OpenID', max_length=100, blank=True, null=True, unique=True)
    
    # 系统认证字段
    email_verified = models.BooleanField('邮箱验证', default=False)
    last_active = models.DateTimeField('最后活跃时间', auto_now=True)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
    
    def __str__(self):
        if self.is_superuser:
            return f"{self.username} (系统管理员)"
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def department(self):
        """获取用户的部门（从staff中）"""
        if hasattr(self, 'staff') and self.staff and self.staff.department:
            return self.staff.department.name
        return ''
        
    @property
    def is_enterprise_admin(self):
        """是否是企业管理员"""
        return self.user_type == self.ENTERPRISE_ADMIN
    
    @property
    def is_independent_user(self):
        """是否是独立用户"""
        return self.user_type == self.INDEPENDENT_USER
    
    def has_app_access(self, app_code):
        """检查用户是否有应用访问权限"""
        # 系统管理员有所有权限
        if self.is_superuser:
            return True
        
        # 独立用户可能有特定应用的访问权限
        if self.is_independent_user:
            # 这里可以根据独立用户的权限设置来决定
            return True
        
        # 企业用户需要检查企业订阅
        from enterprises.models import EnterpriseSubscription
        from staff.models import Staff
        
        # 获取用户关联的所有企业
        staff_members = Staff.objects.filter(user=self)
        for staff in staff_members:
            if staff.enterprise:
                # 检查企业是否订阅了该应用
                if EnterpriseSubscription.objects.filter(
                    enterprise=staff.enterprise,
                    app_code=app_code,
                    status='active'
                ).exists():
                    return True
        
        return False
    
    # 以下是与staff应用关联的属性和方法
    @property
    def staff_profile(self):
        """获取用户的员工资料（向后兼容的方法）"""
        try:
            return self.staff_members.first()
        except ObjectDoesNotExist:
            return None
    
    @property
    def staff(self):
        """获取用户的第一个员工资料记录（向后兼容的属性）"""
        try:
            return self.staff_members.first()
        except ObjectDoesNotExist:
            return None
    
    @property
    def work_phone(self):
        """获取用户的办公电话（从staff中）"""
        if hasattr(self, 'staff') and self.staff:
            return self.staff.work_phone
        return ''
    
    @property
    def enterprise_phone(self):
        """获取用户的企业手机号（从staff中）"""
        if hasattr(self, 'staff') and self.staff:
            return self.staff.enterprise_phone
        return ''
    
    @property
    def enterprise_email(self):
        """获取用户的企业邮箱（从staff中）"""
        if hasattr(self, 'staff') and self.staff:
            return self.staff.enterprise_email
        return ''
    
    @property
    def bio(self):
        """获取用户的个人简介（从staff中）"""
        if hasattr(self, 'staff') and self.staff:
            return self.staff.bio
        return ''
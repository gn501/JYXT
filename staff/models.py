from django.db import models

from django.db import models
from django.conf import settings

class Staff(models.Model):
    """员工模型 - 存储用户在企业中的详细信息"""
    # 定义员工状态常量
    EMPLOYED = 'employed'
    RESIGNED = 'resigned'
    
    EMPLOYMENT_STATUS_CHOICES = [
        (EMPLOYED, '在职'),
        (RESIGNED, '离职'),
    ]
    
    # 与用户模型的一对多关联（一个用户可以在多个企业任职）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_members',
        verbose_name='关联用户'
    )
    
    # 企业相关信息
    # 注意：这里使用ForeignKey而不是OneToOne，因为用户可以在多个企业任职
    enterprise = models.ForeignKey(
        'enterprises.Enterprise',
        on_delete=models.CASCADE,
        verbose_name='所属企业',
        null=True,
        blank=True,
        related_name='staff_members'
    )
    
    # 企业特定信息
    work_phone = models.CharField('办公电话', max_length=20, blank=True)
    enterprise_phone = models.CharField('企业手机号', max_length=20, blank=True)
    enterprise_email = models.EmailField('企业邮箱', blank=True)
    bio = models.TextField('个人简介', blank=True)
    
    # 部门相关信息
    department = models.ForeignKey(
        'enterprises.Department',
        on_delete=models.SET_NULL,
        verbose_name='所属部门',
        null=True,
        blank=True,
        related_name='staff_members'
    )
    position = models.CharField('职位', max_length=100, blank=True)
    
    # 就业状态
    employment_status = models.CharField(
        '就业状态', 
        max_length=20, 
        choices=EMPLOYMENT_STATUS_CHOICES, 
        default=EMPLOYED
    )
    
    # 系统字段
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'staff'
        verbose_name = '员工'
        verbose_name_plural = '员工管理'
        unique_together = ('user', 'enterprise')  # 确保一个用户在一个企业中只有一条记录
    
    def __str__(self):
        enterprise_name = self.enterprise.name if self.enterprise else '无企业'
        return f'{self.user.username} - {enterprise_name}'

class StaffRole(models.Model):
    """员工角色模型 - 定义员工在企业中的角色和权限"""
    # 企业内角色类型常量
    ENTERPRISE_ADMIN = 'enterprise_admin'  # 企业管理员（在企业内的最高权限）
    DEPARTMENT_MANAGER = 'department_manager'  # 部门经理
    TEAM_LEADER = 'team_leader'  # 团队负责人
    REGULAR_STAFF = 'regular_staff'  # 普通员工
    CONTRACTOR = 'contractor'  # 合同工
    
    ROLE_TYPE_CHOICES = [
        (ENTERPRISE_ADMIN, '企业管理员'),
        (DEPARTMENT_MANAGER, '部门经理'),
        (TEAM_LEADER, '团队负责人'),
        (REGULAR_STAFF, '普通员工'),
        (CONTRACTOR, '合同工'),
    ]
    
    # 与员工的一对一关联
    staff = models.OneToOneField(
        'Staff',
        on_delete=models.CASCADE,
        related_name='role',
        verbose_name='关联员工'
    )
    
    # 角色类型
    role_type = models.CharField('角色类型', max_length=20, choices=ROLE_TYPE_CHOICES, default=REGULAR_STAFF)
    
    # 系统字段
    is_active = models.BooleanField('是否激活', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'staff_role'
        verbose_name = '员工角色'
        verbose_name_plural = '员工角色管理'
    
    def __str__(self):
        return f'{self.staff.user.username} - {self.staff.enterprise.name if self.staff.enterprise else "无企业"} - {self.get_role_type_display()}'

# 添加信号处理，确保在创建用户时自动创建相关的staff profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """在用户创建时自动创建员工资料"""
    # 注：由于一个用户可以在多个企业任职，我们不再自动为所有用户创建staff记录
    # 只有在特定场景下（如通过企业管理界面创建用户）才会创建staff记录
    pass

@receiver(post_save, sender=User)
def update_staff_profile(sender, instance, **kwargs):
    """在用户更新时同步更新员工资料"""
    # 注：由于一个用户可以在多个企业任职，我们不再自动更新所有staff记录
    # 只有在特定场景下才会更新staff记录
    pass

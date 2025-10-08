from django import forms
from django.conf import settings
from accounts.models import User
from .models import Staff
from enterprises.models import Department

class StaffProfileForm(forms.Form):
    """员工个人资料表单 - 用于用户编辑自己的资料"""
    # User模型字段
    first_name = forms.CharField(max_length=30, required=True, label='姓名')
    email = forms.EmailField(required=False, label='个人邮箱')
    avatar = forms.ImageField(required=False, label='头像')
    
    # Staff模型字段
    work_phone = forms.CharField(max_length=20, required=False, label='办公电话')
    enterprise_phone = forms.CharField(max_length=20, required=True, label='手机号')
    enterprise_email = forms.EmailField(required=False, label='企业邮箱')
    position = forms.CharField(max_length=100, required=False, label='职位')
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label='个人简介')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.instance = kwargs.pop('instance', None)  # 获取staff实例
        kwargs.pop('instance', None)  # 再次移除instance参数以避免Form基类报错
        super().__init__(*args, **kwargs)
        
        # 如果有实例，填充表单数据
        if self.instance:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['email'].initial = self.instance.user.email
            if hasattr(self.instance.user, 'avatar') and self.instance.user.avatar:
                self.fields['avatar'].initial = self.instance.user.avatar
                
            self.fields['work_phone'].initial = self.instance.work_phone
            self.fields['enterprise_phone'].initial = self.instance.enterprise_phone
            self.fields['enterprise_email'].initial = self.instance.enterprise_email
            self.fields['position'].initial = self.instance.position
            self.fields['bio'].initial = self.instance.bio

class StaffCreateForm(forms.Form):
    """员工创建表单 - 同时处理User和Staff模型的数据"""
    # User模型字段
    first_name = forms.CharField(max_length=30, required=True, label='姓名')
    email = forms.EmailField(required=False, label='个人邮箱')
    is_active = forms.BooleanField(initial=True, required=False, label='激活')
    avatar = forms.ImageField(required=False, label='头像')
    
    # Staff模型字段
    work_phone = forms.CharField(max_length=20, required=False, label='办公电话')
    enterprise_phone = forms.CharField(max_length=20, required=True, label='手机号')
    enterprise_email = forms.EmailField(required=False, label='企业邮箱')
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False, 
        label='部门',
        empty_label='请选择部门'
    )
    position = forms.CharField(max_length=100, required=False, label='职位')
    employment_status = forms.ChoiceField(
        choices=Staff.EMPLOYMENT_STATUS_CHOICES,
        initial=Staff.EMPLOYED,
        required=False,
        label='就业状态'
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        kwargs.pop('instance', None)  # 安全地移除instance参数
        super().__init__(*args, **kwargs)
        
        # 根据用户权限限制字段选项
        # 企业管理员不能创建超级管理员，且只能创建企业用户
        # 用户类型字段已从表单中移除，在视图中直接设置为enterprise_user
            
        # 根据当前用户的企业过滤部门选项
        if hasattr(self.request.user, 'staff') and self.request.user.staff and self.request.user.staff.enterprise:
            self.fields['department'].queryset = Department.objects.filter(
                enterprise=self.request.user.staff.enterprise, 
                is_active=True
            ).order_by('name')

class StaffUpdateForm(forms.Form):
    """员工更新表单 - 同时处理User和Staff模型的数据"""
    # User模型字段
    first_name = forms.CharField(max_length=30, required=True, label='姓名')
    email = forms.EmailField(required=False, label='个人邮箱')
    is_active = forms.BooleanField(required=False, label='激活')
    avatar = forms.ImageField(required=False, label='头像')
    
    # Staff模型字段
    work_phone = forms.CharField(max_length=20, required=False, label='办公电话')
    enterprise_phone = forms.CharField(max_length=20, required=True, label='手机号')
    enterprise_email = forms.EmailField(required=False, label='企业邮箱')
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False, 
        label='部门',
        empty_label='请选择部门'
    )
    position = forms.CharField(max_length=100, required=False, label='职位')
    employment_status = forms.ChoiceField(
        choices=Staff.EMPLOYMENT_STATUS_CHOICES,
        required=False,
        label='就业状态'
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.instance = kwargs.pop('instance', None)  # 获取staff实例
        kwargs.pop('instance', None)  # 再次移除instance参数以避免Form基类报错
        super().__init__(*args, **kwargs)
        
        # 如果有实例，填充表单数据
        if self.instance:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['is_active'].initial = self.instance.user.is_active
            if hasattr(self.instance.user, 'avatar') and self.instance.user.avatar:
                self.fields['avatar'].initial = self.instance.user.avatar
                
            self.fields['work_phone'].initial = self.instance.work_phone
            self.fields['enterprise_phone'].initial = self.instance.enterprise_phone
            self.fields['enterprise_email'].initial = self.instance.enterprise_email
            self.fields['department'].initial = self.instance.department
            self.fields['position'].initial = self.instance.position
            self.fields['employment_status'].initial = getattr(self.instance, 'employment_status', Staff.EMPLOYED)
        
        # 根据用户权限限制字段选项
        # 用户类型字段已从表单中移除，在视图中直接设置为enterprise_user
        
        # 根据当前用户的企业过滤部门选项
            if hasattr(self.request.user, 'staff') and self.request.user.staff and self.request.user.staff.enterprise:
                self.fields['department'].queryset = Department.objects.filter(
                    enterprise=self.request.user.staff.enterprise, 
                    is_active=True
                ).order_by('name')
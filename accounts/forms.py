# accounts/forms.py
from django import forms
from .models import User
from staff.models import Staff, StaffRole
from enterprises.models import Department

class UserForm(forms.ModelForm):
    """用户认证表单 - 只处理User模型中的认证相关字段"""
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        # 移除instance参数，因为普通Form类不处理这个参数
        kwargs.pop('instance', None)  # 安全地移除instance参数
        super().__init__(*args, **kwargs)
        
        # 根据用户权限限制字段选项
        if self.request and not getattr(self.request.user, 'is_super_admin', False):
            # 企业管理员不能创建超级管理员，且只能创建企业用户
            self.fields['user_type'].choices = [
                choice for choice in User.USER_TYPE_CHOICES 
                if choice[0] == 'enterprise_user'  # 只能创建企业用户
            ]

# StaffForm已被移除，因为Staff模型不再包含first_name、last_name和phone字段
# 个人资料相关功能现在由ProfileForm处理

class UserCreateForm(forms.Form):
    """用户创建复合表单 - 同时处理User和Staff模型的数据"""
    # User模型字段 - 用户名会自动使用手机号
    email = forms.EmailField(required=False, label='个人邮箱')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, label='用户类型', initial='enterprise_user')
    is_active = forms.BooleanField(initial=True, required=False, label='激活')
    avatar = forms.ImageField(required=False, label='头像')
    
    # Staff模型字段
    first_name = forms.CharField(max_length=30, required=True, label='姓名')
    last_name = forms.CharField(max_length=30, required=False, label='昵称')
    work_phone = forms.CharField(max_length=20, required=False, label='办公电话')
    enterprise_phone = forms.CharField(max_length=20, required=True, label='手机号')
    enterprise_email = forms.EmailField(required=False, label='企业邮箱')
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=True, 
        label='部门',
        empty_label='请选择部门'
    )
    position = forms.CharField(max_length=100, required=False, label='职位')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        # 移除instance参数，因为普通Form类不处理这个参数
        kwargs.pop('instance', None)  # 安全地移除instance参数
        super().__init__(*args, **kwargs)
        
        # 根据用户权限限制字段选项
        if self.request and not getattr(self.request.user, 'is_super_admin', False):
            # 企业管理员不能创建超级管理员，且只能创建企业用户
            self.fields['user_type'].choices = [
                choice for choice in User.USER_TYPE_CHOICES 
                if choice[0] == 'enterprise_user'  # 只能创建企业用户
            ]
            
            # 根据当前用户的企业过滤部门选项
            if hasattr(self.request.user, 'staff') and self.request.user.staff and self.request.user.staff.enterprise:
                self.fields['department'].queryset = Department.objects.filter(
                    enterprise=self.request.user.staff.enterprise, 
                    is_active=True
                ).order_by('name')

class UserUpdateForm(forms.Form):
    """用户更新复合表单 - 同时处理User和Staff模型的数据"""
    # User模型字段
    username = forms.CharField(max_length=150, required=True, label='用户名', disabled=True)
    email = forms.EmailField(required=False, label='邮箱')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, label='用户类型')
    is_active = forms.BooleanField(required=False, label='激活')
    
    # Staff模型字段
    first_name = forms.CharField(max_length=30, required=False, label='姓名')
    last_name = forms.CharField(max_length=30, required=False, label='昵称')
    enterprise_phone = forms.CharField(max_length=20, required=False, label='手机号')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        # 获取要更新的用户ID
        self.user_id = kwargs.pop('user_id', None)
        # 移除instance参数，因为普通Form类不处理这个参数
        kwargs.pop('instance', None)  # 安全地移除instance参数
        super().__init__(*args, **kwargs)
        
        # 如果有用户ID，尝试获取并设置用户名
        if self.user_id:
            try:
                user = User.objects.get(id=self.user_id)
                self.initial['username'] = user.username
            except User.DoesNotExist:
                pass
        
        # 根据用户权限限制字段选项
        if self.request and not getattr(self.request.user, 'is_super_admin', False):
            # 企业管理员不能创建超级管理员
            self.fields['user_type'].choices = [
                choice for choice in User.USER_TYPE_CHOICES 
                if choice[0] != getattr(User, 'SUPER_ADMIN', None)  # 兼容不存在的SUPER_ADMIN
            ]
            


class ProfileForm(forms.Form):
    """个人资料表单 - 处理个人信息的更新"""
    # User模型字段
    email = forms.EmailField(required=False, label='邮箱')
    first_name = forms.CharField(max_length=30, required=False, label='姓名')
    last_name = forms.CharField(max_length=30, required=False, label='昵称')
    
    # Staff模型字段
    enterprise_phone = forms.CharField(max_length=20, required=False, label='手机号')
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False, 
        label='部门',
        empty_label='请选择部门'
    )
    position = forms.CharField(max_length=100, required=False, label='职位')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        # 移除instance参数，因为普通Form类不处理这个参数
        kwargs.pop('instance', None)  # 安全地移除instance参数
        super().__init__(*args, **kwargs)
        
        # 根据当前用户的企业过滤部门选项
        if self.request and hasattr(self.request.user, 'enterprise') and self.request.user.enterprise:
            self.fields['department'].queryset = Department.objects.filter(
                enterprise=self.request.user.enterprise, 
                is_active=True
            ).order_by('name')
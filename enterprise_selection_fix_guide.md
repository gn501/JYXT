# 多企业任职选择问题的完整修复方案

根据您的问题描述，用户在两家企业任职，但登录后直接进入了一家企业，没有显示企业选择界面。以下是完整的修复方案：

## 问题分析

通过检查代码，我发现可能的问题原因包括：

1. **登录逻辑判断问题**：CustomLoginView中的逻辑可能没有正确识别用户的多企业任职情况
2. **Session缓存问题**：用户可能之前选择过企业，session中保存了企业ID
3. **企业任职状态问题**：用户的企业任职记录可能没有正确设置为"在职"状态

## 修复步骤

### 1. 检查用户的企业任职情况

首先，创建一个脚本来验证用户确实在多个企业任职：

```python
#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import django
django.setup()

from accounts.models import User
from staff.models import Staff

# 替换为实际的用户名
username = 'your_username'

try:
    user = User.objects.get(username=username)
    print(f"用户: {user.username} ({user.first_name})")
    
    # 检查所有员工记录
    staff_records = user.staff_members.all()
    print(f"总员工记录数: {staff_records.count()}")
    
    # 检查在职的员工记录
    employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
    print(f"在职员工记录数: {employed_staffs.count()}")
    
    # 显示每个记录的详细信息
    for staff in staff_records:
        enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
        status = '在职' if staff.employment_status == Staff.EMPLOYED else '离职'
        print(f"- 企业: {enterprise_name}, 状态: {status}")
        
except User.DoesNotExist:
    print(f"找不到用户 '{username}'")
```

### 2. 修改登录视图 (CustomLoginView)

确保`accounts/views.py`中的`CustomLoginView`正确处理多企业情况：

```python
# 打开文件: accounts/views.py
# 修改 CustomLoginView 类的 form_valid 方法

def form_valid(self, form):
    """处理登录表单验证成功后的逻辑"""
    # 执行父类的form_valid方法进行用户认证
    response = super().form_valid(form)
    
    # 获取当前登录的用户
    user = self.request.user
    
    # 检查用户是否有在职的企业任职记录
    employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
    
    # 清除之前可能存在的企业选择session
    if 'current_enterprise_id' in self.request.session:
        del self.request.session['current_enterprise_id']
    
    # 根据用户类型和企业任职情况设置重定向URL
    if getattr(user, 'is_super_admin', False):
        self.success_url = reverse_lazy('enterprises:enterprise_list')
    elif employed_staffs.count() == 0:
        # 如果用户没有在职的企业任职记录，作为无所属企业用户登录
        self.success_url = reverse_lazy('dashboard')
    elif employed_staffs.count() == 1:
        # 如果用户只有一个在职的企业任职记录，直接进入该企业
        # 同时将该企业ID存入session，确保后续操作正确
        self.request.session['current_enterprise_id'] = str(employed_staffs.first().enterprise.id)
        self.success_url = reverse_lazy('dashboard')
    else:
        # 如果用户有多个在职的企业任职记录，重定向到企业选择页面
        self.success_url = reverse_lazy('accounts:select_enterprise')
    
    return response
```

### 3. 修改企业选择视图 (SelectEnterpriseView)

确保`accounts/views.py`中的`SelectEnterpriseView`正确处理企业选择：

```python
# 修改 SelectEnterpriseView 类的 get 方法

def get(self, request, *args, **kwargs):
    # 获取用户所有在职的企业任职记录
    employed_staffs = request.user.staff_members.filter(employment_status=Staff.EMPLOYED)
    
    # 清除之前可能存在的企业选择session
    if 'current_enterprise_id' in request.session:
        del request.session['current_enterprise_id']
    
    # 如果用户只有一个在职企业，直接跳转到首页并设置session
    if employed_staffs.count() == 1:
        request.session['current_enterprise_id'] = str(employed_staffs.first().enterprise.id)
        return redirect('dashboard')
    elif employed_staffs.count() == 0:
        # 如果用户没有在职企业，直接跳转到首页
        return redirect('dashboard')
    
    # 用户有多个在职企业，显示选择页面
    return render(request, self.template_name, {
        'staffs': employed_staffs
    })

# 确保 post 方法正确保存企业选择

def post(self, request, *args, **kwargs):
    # 获取用户选择的企业ID
    enterprise_id = request.POST.get('enterprise_id')
    
    if not enterprise_id:
        messages.error(request, "请选择一个企业")
        return redirect('accounts:select_enterprise')
    
    try:
        # 验证用户是否在该企业有在职记录
        staff = request.user.staff_members.get(
            enterprise_id=enterprise_id,
            employment_status=Staff.EMPLOYED
        )
        
        # 保存用户选择的企业ID到session
        request.session['current_enterprise_id'] = enterprise_id
        
        return redirect('dashboard')
    except Staff.DoesNotExist:
        messages.error(request, "您没有选择企业的访问权限")
        return redirect('accounts:select_enterprise')
```

### 4. 检查URL配置

确保`accounts/urls.py`中正确配置了企业选择的URL：

```python
from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SelectEnterpriseView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('select-enterprise/', SelectEnterpriseView.as_view(), name='select_enterprise'),
    # 其他URL配置...
]
```

## 测试方法

1. **创建测试用户**：使用`test_multi_enterprise.py`脚本创建一个在多个企业任职的测试用户
2. **清除浏览器缓存**：让用户清除浏览器缓存或使用无痕模式测试
3. **验证登录流程**：使用测试用户登录，确认是否正确显示企业选择界面
4. **检查企业切换**：选择不同的企业，确认系统是否正确切换到相应的企业环境

## 常见问题排查

1. **企业选择界面仍不显示**：
   - 检查用户的企业任职记录是否都设置为"在职"状态
   - 检查数据库中user.staff_members关系是否正确
   - 确认用户不是超级管理员（超级管理员有特殊逻辑）

2. **选择企业后无法正常访问**：
   - 检查session是否正确保存了企业ID
   - 确认其他视图是否正确读取了session中的企业信息

## 总结

这个问题主要是由于登录流程中的企业判断逻辑和session管理导致的。通过以上修复步骤，应该能够解决用户在多个企业任职时不显示企业选择界面的问题。

如果问题仍然存在，请使用提供的诊断脚本进一步检查系统状态，并根据输出结果调整修复方案。
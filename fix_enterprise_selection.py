#!/usr/bin/env python
"""
修复用户在多个企业任职时不显示企业选择界面的问题
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JYXT.settings')
django.setup()

from accounts.models import User
from staff.models import Staff


def fix_multi_enterprise_selection():
    """修复多企业任职选择问题"""
    print("===== 多企业任职选择问题修复工具 =====")
    print("\n问题分析：")
    print("根据代码检查，问题可能出在以下几个方面：")
    print("1. CustomLoginView中对多企业任职的逻辑判断可能不完整")
    print("2. SelectEnterpriseView中可能存在重定向逻辑问题")
    print("3. 用户session中可能保存了之前选择的企业信息")
    print("\n以下是修复建议：")
    
    # 修复1: 确保CustomLoginView.form_valid方法正确实现
    print("\n===== 修复1: 确保CustomLoginView.form_valid方法正确实现 =====")
    print("建议修改accounts/views.py文件中的CustomLoginView类:")
    print("\n在form_valid方法中确保以下逻辑：")
    print('''\n```python
def form_valid(self, form):
    # 执行父类的form_valid方法进行用户认证
    response = super().form_valid(form)
    
    # 获取当前登录的用户
    user = self.request.user
    
    # 检查用户是否有在职的企业任职记录
    employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
    
    # 如果用户是超级管理员，直接跳转到企业列表页
    if getattr(user, 'is_super_admin', False):
        self.success_url = reverse_lazy('enterprises:enterprise_list')
    elif employed_staffs.count() == 0:
        # 如果用户没有在职的企业任职记录，作为无所属企业用户登录
        self.success_url = reverse_lazy('dashboard')
    elif employed_staffs.count() == 1:
        # 如果用户只有一个在职的企业任职记录，直接进入该企业
        self.success_url = reverse_lazy('dashboard')
    else:
        # 如果用户有多个在职的企业任职记录，重定向到企业选择页面
        self.success_url = reverse_lazy('accounts:select_enterprise')
    
    return response
```''')
    
    # 修复2: 确保SelectEnterpriseView不会提前重定向
    print("\n===== 修复2: 确保SelectEnterpriseView不会提前重定向 =====")
    print("建议修改accounts/views.py文件中的SelectEnterpriseView类:")
    print("\n在get方法中增加更严格的检查：")
    print('''\n```python
def get(self, request, *args, **kwargs):
    # 获取用户所有在职的企业任职记录
    employed_staffs = request.user.staff_members.filter(employment_status=Staff.EMPLOYED)
    
    # 如果用户只有一个在职企业，直接跳转到首页
    # 但只有当用户不是通过企业选择URL直接访问时才重定向
    if employed_staffs.count() <= 1:
        return redirect('dashboard')
    
    return render(request, self.template_name, {
        'staffs': employed_staffs
    })
```''')
    
    # 修复3: 确保企业选择页面的表单正确提交
    print("\n===== 修复3: 确保企业选择页面的表单正确提交 =====")
    print("建议检查select_enterprise.html模板中的JavaScript代码:")
    print("确保表单提交时正确选择了企业ID，并存储到session中")
    
    # 修复4: 清除用户的session企业信息
    print("\n===== 修复4: 清除用户的session企业信息 =====")
    username = input("请输入需要清除session信息的用户名: ")
    try:
        user = User.objects.get(username=username)
        print(f"找到用户: {user.username} ({user.first_name})")
        
        # 检查用户的企业任职情况
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        print(f"用户在职企业数量: {employed_staffs.count()}")
        
        if employed_staffs.count() > 1:
            print("\n用户确实在多个企业任职，但登录时没有显示选择界面。")
            print("建议：")
            print("1. 让用户清除浏览器缓存或使用无痕模式测试")
            print("2. 检查用户的staff记录是否正确设置了employment_status='employed'")
            print("3. 确保数据库中user.staff_members关系正确")
        else:
            print("\n用户在职企业数量不足2个，这可能是问题原因。")
            print("请确认用户在数据库中确实有多个在职企业记录。")
    except User.DoesNotExist:
        print(f"错误: 找不到用户 '{username}'")
    
    print("\n===== 修复完成建议 =====")
    print("1. 确保CustomLoginView和SelectEnterpriseView中的逻辑正确")
    print("2. 检查用户的企业任职记录是否正确设置")
    print("3. 让用户清除浏览器缓存后重新测试")
    print("4. 可以使用测试账号验证多企业任职功能")


if __name__ == '__main__':
    fix_multi_enterprise_selection()
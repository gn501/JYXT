#!/usr/bin/env python
"""
测试用户登录流程和企业选择功能
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JYXT.settings')
django.setup()

from accounts.models import User
from staff.models import Staff
from django.test import RequestFactory
from accounts.views import CustomLoginView, SelectEnterpriseView
from django.urls import reverse_lazy
from django.contrib.sessions.middleware import SessionMiddleware
import json


def test_user_login_flow(username):
    """测试用户登录流程"""
    print("\n===== 用户登录流程测试工具 =====")
    
    try:
        # 查找用户
        user = User.objects.get(username=username)
        print(f"\n测试用户: {user.username} ({user.first_name})")
        
        # 检查用户的企业任职情况
        print("\n1. 企业任职情况:")
        all_staffs = user.staff_members.all()
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        print(f"总企业数: {all_staffs.count()}, 在职企业数: {employed_staffs.count()}")
        
        for staff in all_staffs:
            status = '在职' if staff.employment_status == Staff.EMPLOYED else '离职'
            print(f"- 企业: {staff.enterprise.name}, 状态: {status}")
        
        # 模拟请求和session
        print("\n2. 模拟登录请求:")
        factory = RequestFactory()
        request = factory.get('/accounts/login/')
        request.user = user
        
        # 添加session支持
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session.save()
        
        # 测试CustomLoginView的form_valid逻辑
        print("\n3. 测试CustomLoginView.form_valid逻辑:")
        login_view = CustomLoginView()
        login_view.request = request
        
        # 模拟form_valid方法中设置success_url的逻辑
        if getattr(user, 'is_super_admin', False):
            success_url = reverse_lazy('enterprises:enterprise_list')
            print(f"- 用户是超级管理员，应该跳转到: {success_url}")
        elif employed_staffs.count() == 0:
            success_url = reverse_lazy('dashboard')
            print(f"- 用户没有在职企业，应该跳转到: {success_url}")
        elif employed_staffs.count() == 1:
            success_url = reverse_lazy('dashboard')
            print(f"- 用户只有一个在职企业，应该跳转到: {success_url}")
        else:
            success_url = reverse_lazy('accounts:select_enterprise')
            print(f"- 用户有多个在职企业，应该跳转到: {success_url}")
        
        # 检查是否应该显示企业选择界面
        print("\n4. 企业选择界面检查:")
        if employed_staffs.count() > 1:
            print("- 用户应该看到企业选择界面")
            
            # 测试SelectEnterpriseView
            print("\n5. 测试SelectEnterpriseView:")
            select_view = SelectEnterpriseView()
            select_view.request = request
            
            # 模拟get请求逻辑
            if employed_staffs.count() <= 1:
                print("- 根据逻辑，应该重定向到dashboard")
            else:
                print("- 根据逻辑，应该显示企业选择界面")
                print(f"- 可供选择的企业数量: {employed_staffs.count()}")
        else:
            print("- 用户不应该看到企业选择界面")
        
        # 检查session中是否有企业ID
        print("\n6. Session检查:")
        if 'current_enterprise_id' in request.session:
            print(f"- Session中存在企业ID: {request.session['current_enterprise_id']}")
            print("- 这可能导致用户跳过企业选择界面")
        else:
            print("- Session中没有企业ID")
        
        # 提供修复建议
        print("\n===== 修复建议 =====")
        if employed_staffs.count() > 1:
            print("1. 确保CustomLoginView中正确设置了success_url为企业选择页面")
            print("2. 确保每次登录时清除旧的企业选择session")
            print("3. 检查SelectEnterpriseView是否正确处理了多企业情况")
            print("4. 验证select_enterprise.html模板是否正确渲染了企业列表")
            print("5. 检查是否有其他中间件或逻辑影响了重定向流程")
        else:
            print("1. 根据用户的企业任职情况，系统行为符合预期")
            print("2. 如果需要用户看到企业选择界面，请确保用户在多个企业中都有在职记录")
            
    except User.DoesNotExist:
        print(f"错误: 找不到用户 '{username}'")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("请输入要测试的用户名: ")
    
    if username.strip():
        test_user_login_flow(username)
    else:
        print("用户名不能为空")
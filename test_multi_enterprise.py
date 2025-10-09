#!/usr/bin/env python
"""
测试用户在多个企业任职的功能并诊断登录问题
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JYXT.settings')
django.setup()

from accounts.models import User
from enterprises.models import Enterprise
from staff.models import Staff
from django.contrib.auth import authenticate
from django.http import HttpRequest
import random


def diagnose_login_issue(username):
    """诊断用户登录后不显示企业选择页面的问题"""
    try:
        # 获取用户
        user = User.objects.get(username=username)
        print(f"\n===== 开始诊断用户: {user.username} ({user.first_name}) =====")
        print(f"用户ID: {user.id}")
        
        # 获取所有员工记录
        all_staffs = user.staff_members.all()
        print(f"总员工记录数: {all_staffs.count()}")
        
        # 获取在职的员工记录
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        print(f"在职员工记录数: {employed_staffs.count()}")
        
        # 显示每个员工记录的详细信息
        print("\n=== 员工记录详情 ===")
        for staff in all_staffs:
            enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
            status = '在职' if staff.employment_status == Staff.EMPLOYED else '离职'
            print(f"- 企业: {enterprise_name}, 状态: {status}, 职位: {staff.position}")
        
        # 模拟登录逻辑判断
        print("\n=== 登录逻辑分析 ===")
        print(f"用户是否超级管理员: {user.is_superuser}")
        print(f"用户is_super_admin属性: {getattr(user, 'is_super_admin', False)}")
        
        # 分析应该走哪个流程
        if user.is_superuser or getattr(user, 'is_super_admin', False):
            print("根据代码逻辑: 用户应该进入企业列表页")
        elif employed_staffs.count() == 0:
            print("根据代码逻辑: 用户应该作为无所属企业用户登录")
        elif employed_staffs.count() == 1:
            print("根据代码逻辑: 用户应该直接进入唯一的企业")
        else:
            print("根据代码逻辑: 用户应该看到企业选择页面")
            print("但实际上用户直接进入了一家企业，这表明存在问题！")
            
            # 分析可能的问题
            print("\n=== 可能的问题原因 ===")
            
            # 1. 检查staff_members.filter查询
            print("1. 检查staff_members.filter查询")
            print(f"staff_members是否正确返回所有员工记录: {all_staffs.count() > 0}")
            print(f"filter(employment_status=Staff.EMPLOYED)是否正确过滤: {employed_staffs.count() == sum(1 for s in all_staffs if s.employment_status == Staff.EMPLOYED)}")
            
            # 2. 检查staff.employment_status值
            print("\n2. 检查employment_status值")
            for staff in all_staffs:
                print(f"- 企业'{staff.enterprise.name}': employment_status='{staff.employment_status}'")
            
            # 3. 检查session中是否有残留的企业信息
            print("\n3. 检查session问题")
            print("提示: 用户之前可能已经选择过企业，session中存储了企业ID")
            print("建议清除浏览器缓存或使用无痕模式测试")
            
            # 4. 提供修复建议
            print("\n=== 修复建议 ===")
            print("1. 确保CustomLoginView.form_valid方法正确实现")
            print("2. 检查是否有其他代码覆盖了success_url")
            print("3. 验证用户在职状态是否正确设置")
            print("4. 确保企业选择URL在urls.py中正确配置")
        
    except User.DoesNotExist:
        print(f"错误: 找不到用户 '{username}'")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def create_test_user_with_multi_enterprise():
    """创建一个在多个企业任职的测试用户"""
    print("\n===== 创建测试用户 =====")
    
    # 生成唯一的企业名称
suffix = random.randint(1000, 9999)
    enterprise_a_name = f'企业A_{suffix}'
    enterprise_b_name = f'企业B_{suffix}'
    
    # 创建两个企业（需要提供唯一的统一社会信用代码）
    enterprise_a = Enterprise.objects.create(name=enterprise_a_name, unified_social_credit_code=f'91310101MA1G8{suffix}45')
    enterprise_b = Enterprise.objects.create(name=enterprise_b_name, unified_social_credit_code=f'91310101MA1G8{suffix}46')
    print(f"创建了两个企业: {enterprise_a.name}, {enterprise_b.name}")
    
    # 检查是否已存在测试用户，如果存在则删除
try:
        test_user = User.objects.get(username='13801609753')
        test_user.delete()
        print("删除了已存在的测试用户")
    except User.DoesNotExist:
        pass
    
    # 创建测试用户
    user = User.objects.create(
        username='13801609753',
        first_name='周腾',
        user_type='enterprise_user',
        is_active=True
    )
    user.set_password('123456')  # 设置默认密码
    user.save()
    print(f"创建了测试用户: {user.first_name} (手机号: {user.username}), 密码: 123456")
    
    # 在企业A中创建员工记录
    staff_a = Staff.objects.create(
        user=user,
        enterprise=enterprise_a,
        enterprise_phone='13801609753',
        position='开发工程师',
        employment_status='employed'
    )
    print(f"在{enterprise_a.name}中创建了员工记录")
    
    # 在企业B中创建员工记录
    staff_b = Staff.objects.create(
        user=user,
        enterprise=enterprise_b,
        enterprise_phone='13801609753',
        position='市场专员',
        employment_status='employed'
    )
    print(f"在{enterprise_b.name}中创建了员工记录")
    
    return user.username


def main():
    """主函数"""
    print("===== 多企业任职登录问题诊断工具 =====")
    
    # 询问是否创建新的测试用户
    create_new = input("是否创建新的测试用户? (y/n, 默认n): ")
    username = None
    
    if create_new.lower() == 'y':
        username = create_test_user_with_multi_enterprise()
    else:
        # 获取要诊断的用户名
        username = input("请输入要诊断的用户名: ")
    
    # 执行诊断
    diagnose_login_issue(username)
    
    # 额外提示
    print("\n===== 附加信息 ====")
    print("如果问题仍然存在，建议检查以下文件：")
    print("1. accounts/views.py - CustomLoginView.form_valid方法")
    print("2. accounts/templates/accounts/select_enterprise.html - 企业选择模板")
    print("3. accounts/urls.py - 确保URL正确配置")


if __name__ == '__main__':
    main()
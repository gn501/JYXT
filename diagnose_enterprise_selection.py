#!/usr/bin/env python
"""
诊断用户在多个企业任职时不显示企业选择界面的问题
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JYXT.settings')
django.setup()

from accounts.models import User
from staff.models import Staff
from django.db import connection

def analyze_user_enterprise_selection(username):
    """分析指定用户的企业任职情况"""
    print(f"\n===== 用户企业任职分析工具 =====")
    
    try:
        # 查找用户
        user = User.objects.get(username=username)
        print(f"\n用户信息:")
        print(f"用户名: {user.username}")
        print(f"姓名: {user.first_name}{user.last_name}")
        print(f"用户类型: {user.get_user_type_display()}")
        print(f"是否超级管理员: {'是' if getattr(user, 'is_super_admin', False) else '否'}")
        print(f"是否Django超级用户: {'是' if user.is_superuser else '否'}")
        
        # 检查所有企业任职记录
        print(f"\n所有企业任职记录:")
        all_staffs = user.staff_members.all()
        print(f"总企业任职记录数: {all_staffs.count()}")
        
        if all_staffs.count() > 0:
            for i, staff in enumerate(all_staffs, 1):
                enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
                status = '在职' if staff.employment_status == Staff.EMPLOYED else '离职'
                status_color = '\033[92m' if staff.employment_status == Staff.EMPLOYED else '\033[91m'
                reset_color = '\033[0m'
                print(f"{i}. 企业: {enterprise_name}, 状态: {status_color}{status}{reset_color}")
        else:
            print("该用户没有任何企业任职记录")
        
        # 检查在职的企业任职记录
        print(f"\n在职企业任职记录:")
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        print(f"在职企业任职记录数: {employed_staffs.count()}")
        
        if employed_staffs.count() > 0:
            for i, staff in enumerate(employed_staffs, 1):
                enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
                print(f"{i}. 企业: {enterprise_name}")
        else:
            print("该用户没有在职的企业任职记录")
        
        # 分析登录流程
        print(f"\n登录流程分析:")
        if getattr(user, 'is_super_admin', False):
            print("用户是超级管理员，登录后将直接跳转到企业列表页")
        elif employed_staffs.count() == 0:
            print("用户没有在职的企业任职记录，登录后将作为无所属企业用户进入系统")
        elif employed_staffs.count() == 1:
            print("用户只有一个在职的企业任职记录，登录后将直接进入该企业")
        else:
            print("用户有多个在职的企业任职记录，登录后应该显示企业选择界面")
            print("如果没有显示选择界面，可能的原因：")
            print("1. 用户浏览器缓存中可能保存了之前选择的企业信息")
            print("2. 系统session中可能已经存储了企业ID")
            print("3. 浏览器Cookie问题")
            print("4. 代码中可能存在其他重定向逻辑")
        
        # 提供修复建议
        print(f"\n修复建议:")
        if employed_staffs.count() > 1:
            print("1. 请用户清除浏览器缓存或使用无痕模式重新登录")
            print("2. 检查用户的企业任职记录，确保所有需要显示的企业都设置为在职状态")
            print("3. 如果问题仍然存在，请修改CustomLoginView中的逻辑，确保在form_valid方法中正确判断多企业任职情况")
            print("4. 可以在CustomLoginView中添加代码，在用户登录时清除之前的企业选择session")
        else:
            print("1. 根据分析结果，用户当前的企业任职情况不会触发企业选择界面")
            print("2. 如果需要用户能够选择企业，请确保用户在多个企业中都有在职记录")
            print("3. 可以在数据库中检查用户的staff_members记录是否正确")
        
        # 数据库查询调试
        print(f"\n数据库查询调试:")
        print(f"查询用户所有企业任职记录的SQL:")
        print(str(user.staff_members.all().query))
        print(f"\n查询用户在职企业任职记录的SQL:")
        print(str(user.staff_members.filter(employment_status=Staff.EMPLOYED).query))
        
    except User.DoesNotExist:
        print(f"错误: 找不到用户 '{username}'")
        print("请确认用户名是否正确，或者该用户是否存在于系统中")
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        print("请检查系统配置和数据库连接")

if __name__ == '__main__':
    print("欢迎使用用户企业任职分析工具")
    print("此工具用于诊断用户在多个企业任职时不显示企业选择界面的问题")
    
    if len(sys.argv) > 1:
        # 从命令行参数获取用户名
        username = sys.argv[1]
        analyze_user_enterprise_selection(username)
    else:
        # 交互式输入用户名
        username = input("请输入要分析的用户名: ")
        if username.strip():
            analyze_user_enterprise_selection(username)
        else:
            print("用户名不能为空，请重新运行工具并输入有效的用户名")
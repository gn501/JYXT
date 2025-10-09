#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""检查用户数据脚本"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JYXT.settings')

import django
django.setup()

# 导入User模型
from accounts.models import User

# 检查用户ID为35、37和39的数据
for user_id in [35, 37, 39]:
    try:
        user = User.objects.get(id=user_id)
        print(f"\n用户ID: {user.id}")
        print(f"用户名(username): '{user.username}'")
        print(f"姓名(first_name): '{user.first_name}'")
        print(f"昵称(last_name): '{user.last_name}'")
        print(f"邮箱(email): '{user.email}'")
        print(f"手机号(phone): '{user.phone}'")
        print(f"用户类型(user_type): '{user.user_type}'")
        print(f"是否激活(is_active): {user.is_active}")
        print(f"是否是超级用户(is_superuser): {user.is_superuser}")
        print(f"是否是企业管理员(is_enterprise_admin): {user.is_enterprise_admin}")
        
        # 检查员工资料
        try:
            staff = user.staff_members.first()
            if staff:
                print(f"员工资料:")
                print(f"企业ID: {staff.enterprise.id if staff.enterprise else '无'}")
                print(f"企业名称: {staff.enterprise.name if staff.enterprise else '无'}")
                print(f"部门: {staff.department.name if staff.department else '无'}")
                print(f"职位: '{staff.position}'")
                print(f"就业状态: '{staff.employment_status}'")
            else:
                print("该用户没有关联的员工资料")
        except Exception as e:
            print(f"获取员工资料时出错: {str(e)}")
    except User.DoesNotExist:
        print(f"错误: ID为{user_id}的用户不存在")
    except Exception as e:
        print(f"获取用户{user_id}数据时出错: {str(e)}")

print("\n脚本执行完毕")
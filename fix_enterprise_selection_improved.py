#!/usr/bin/env python
"""
改进版 - 修复用户在多个企业任职时不显示企业选择界面的问题
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

def analyze_and_fix_enterprise_selection():
    """分析并修复多企业任职选择问题"""
    print("===== 多企业任职选择问题修复工具 (改进版) =====")
    print("\n问题分析：")
    print("1. 用户在多个企业任职时，登录后应该显示企业选择界面")
    print("2. 常见问题原因：")
    print("   - CustomLoginView中的逻辑问题")
    print("   - SelectEnterpriseView中的重定向问题")
    print("   - 用户session中保存了之前选择的企业信息")
    print("   - 用户的企业任职状态设置不正确")
    print("\n请按照以下步骤进行修复：")
    
    # 步骤1: 检查用户的企业任职情况
    print("\n===== 步骤1: 检查用户的企业任职情况 =====")
    username = input("请输入需要检查的用户名: ")
    
    try:
        user = User.objects.get(username=username)
        print(f"\n找到用户: {user.username} ({user.first_name})\n")
        
        # 显示用户基本信息
        print("用户基本信息:")
        print(f"- 用户类型: {user.get_user_type_display()}")
        print(f"- 是否超级管理员: {'是' if getattr(user, 'is_super_admin', False) else '否'}")
        
        # 检查所有企业任职记录
        all_staffs = user.staff_members.all()
        print(f"\n所有企业任职记录 ({all_staffs.count()}):")
        
        for staff in all_staffs:
            enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
            status = '在职' if staff.employment_status == Staff.EMPLOYED else '离职'
            status_color = '\033[92m' if staff.employment_status == Staff.EMPLOYED else '\033[91m'
            reset_color = '\033[0m'
            print(f"- 企业: {enterprise_name}, 状态: {status_color}{status}{reset_color}")
        
        # 检查在职的企业任职记录
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        print(f"\n在职企业任职记录 ({employed_staffs.count()}):")
        
        for staff in employed_staffs:
            enterprise_name = staff.enterprise.name if staff.enterprise else '无企业'
            print(f"- 企业: {enterprise_name}")
        
        # 分析登录行为
        print(f"\n登录行为分析:")
        if getattr(user, 'is_super_admin', False):
            print("- 用户是超级管理员，登录后将直接跳转到企业列表页")
        elif employed_staffs.count() == 0:
            print("- 用户没有在职的企业任职记录，登录后将作为无所属企业用户进入系统")
        elif employed_staffs.count() == 1:
            print("- 用户只有一个在职的企业任职记录，登录后将直接进入该企业")
        else:
            print("- 用户有多个在职的企业任职记录，登录后应该显示企业选择界面")
            print("  但如果没有显示，可能是session缓存或代码逻辑问题")
        
        # 步骤2: 提供修复建议
        print("\n===== 步骤2: 代码修复建议 =====")
        
        # 修复1: 优化CustomLoginView
        print("\n修复1: 优化CustomLoginView类")
        print("\n建议修改accounts/views.py文件中的CustomLoginView类，添加以下改进：")
        print('''\n```python
class CustomLoginView(LoginView):
    """自定义登录视图"""
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        """处理登录表单验证成功后的逻辑"""
        # 执行父类的form_valid方法进行用户认证
        response = super().form_valid(form)
        
        # 获取当前登录的用户
        user = self.request.user
        
        # 清除之前可能存在的企业选择session
        if 'current_enterprise_id' in self.request.session:
            del self.request.session['current_enterprise_id']
        
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
            # 同时将该企业ID存入session，确保后续操作正确
            self.request.session['current_enterprise_id'] = str(employed_staffs.first().enterprise.id)
            self.success_url = reverse_lazy('dashboard')
        else:
            # 如果用户有多个在职的企业任职记录，重定向到企业选择页面
            self.success_url = reverse_lazy('accounts:select_enterprise')
        
        return response
```''')
        
        # 修复2: 优化SelectEnterpriseView
        print("\n修复2: 优化SelectEnterpriseView类")
        print("\n建议修改accounts/views.py文件中的SelectEnterpriseView类，添加以下改进：")
        print('''\n```python
class SelectEnterpriseView(LoginRequiredMixin, View):
    """企业选择视图"""
    template_name = 'accounts/select_enterprise.html'
    
    def get(self, request, *args, **kwargs):
        # 清除之前可能存在的企业选择session
        if 'current_enterprise_id' in request.session:
            del request.session['current_enterprise_id']
        
        # 获取用户所有在职的企业任职记录
        employed_staffs = request.user.staff_members.filter(employment_status=Staff.EMPLOYED)
        
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
```''')
        
        # 步骤3: 验证企业选择模板
        print("\n===== 步骤3: 验证企业选择模板 =====")
        print("\n建议检查accounts/templates/accounts/select_enterprise.html模板，确保以下内容正确：")
        print('''\n```html
<form method="post" action="{% url 'accounts:select_enterprise' %}">
    {% csrf_token %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">选择企业</h3>
        </div>
        <div class="card-body">
            {% if staffs %}
                {% for staff in staffs %}
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="radio" name="enterprise_id"
                               id="enterprise_{{ staff.enterprise.id }}" 
                               value="{{ staff.enterprise.id }}" 
                               {% if forloop.first %}checked{% endif %}>
                        <label class="form-check-label" for="enterprise_{{ staff.enterprise.id }}">
                            {{ staff.enterprise.name }}
                        </label>
                    </div>
                {% endfor %}
            {% else %}
                <p class="text-danger">您没有可访问的企业</p>
            {% endif %}
        </div>
        <div class="card-footer">
            <button type="submit" class="btn btn-primary">确认选择</button>
        </div>
    </div>
</form>
```''')
        
        # 步骤4: 最终修复建议
        print("\n===== 步骤4: 最终修复建议 =====")
        print("\n实施以上修复后，请执行以下操作验证：")
        print("1. 清除浏览器缓存或使用无痕模式测试")
        print("2. 使用具有多个在职企业的用户账号登录系统")
        print("3. 确认登录后是否正确显示企业选择界面")
        print("4. 选择不同的企业，验证是否能够正确切换企业环境")
        
        # 提供附加工具
        print("\n===== 附加工具 =====")
        print("\n请运行 diagnose_enterprise_selection.py 脚本获取更详细的用户企业任职分析")
        
    except User.DoesNotExist:
        print(f"错误: 找不到用户 '{username}'")
        print("请确认用户名是否正确，或者该用户是否存在于系统中")
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        print("请检查系统配置和数据库连接")

if __name__ == '__main__':
    analyze_and_fix_enterprise_selection()
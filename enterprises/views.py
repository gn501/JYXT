# enterprises/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.forms import ModelChoiceField
from JYXT.core.permissions import SuperUserRequiredMixin, EnterpriseRequiredMixin, EnterpriseAdminRequiredMixin
from .models import Enterprise, EnterpriseSubscription, Department
from accounts.models import User

# 自定义的ModelChoiceField，用于在表单中显示用户的姓名作为标签
class UserNameChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        # 使用用户的姓名作为标签，如果没有姓名则使用用户名
        full_name = f"{obj.first_name}{obj.last_name}"
        if full_name:
            return full_name
        return obj.username

class EnterpriseBaseView(LoginRequiredMixin):
    """基础视图类"""
    pass

class EnterpriseListView(SuperUserRequiredMixin, ListView):
    """企业列表（超级管理员视图）"""
    model = Enterprise
    template_name = 'enterprises/enterprise_list.html'
    context_object_name = 'enterprises'
    paginate_by = 20
    
    def get_queryset(self):
        """重写get_queryset方法，预加载企业管理员信息"""
        # 使用prefetch_related优化查询，预加载关联的用户
        queryset = super().get_queryset()
        # 我们不能在模板中直接过滤，但可以在视图中添加属性
        # 在视图层面，我们不需要做特殊处理，而是在模板中使用一个辅助方法
        return queryset
    
    def get_context_data(self, **kwargs):
        """重写get_context_data方法，为每个企业添加管理员信息"""
        context = super().get_context_data(**kwargs)
        # 为每个企业添加管理员信息
        for enterprise in context['enterprises']:
            # 获取企业管理员用户 - 通过Staff模型关联
            admin = User.objects.filter(staff_members__enterprise=enterprise, user_type='enterprise_admin').first()
            # 将管理员信息添加到企业对象上，方便在模板中使用
            enterprise.admin_username = admin.username if admin else '-'  
        return context

class EnterpriseCreateView(SuperUserRequiredMixin, CreateView):
    """创建企业"""
    model = Enterprise
    template_name = 'enterprises/enterprise_form.html'
    fields = [
        # 基本信息
        'name', 'unified_social_credit_code', 'enterprise_type', 'registered_address', 
        'legal_representative', 'registered_capital', 'establishment_date', 
        'business_term_start', 'business_term_end', 'registration_authority', 'business_scope',
        # 企业信息
        'contact_address', 'contact_phone', 'contact_email', 'website', 'logo',
        # 系统状态
        'is_active'
    ]
    success_url = reverse_lazy('enterprises:enterprise_list')

    def form_valid(self, form):
        # 保存企业对象，获取企业实例
        enterprise = form.save()
        
        # 生成企业管理员用户名
        admin_username = enterprise.generate_admin_username()
        admin_password = admin_username  # 密码同用户名
        
        # 创建企业管理员用户
        from accounts.models import User
        from staff.models import Staff, StaffRole
        from django.contrib.auth.hashers import make_password
        
        # 确保用户名唯一（理论上generate_admin_username已经保证了唯一性，但为了安全起见再次检查）
        username = admin_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{admin_username}_{counter}"
            counter += 1
            
        # 创建用户（包含认证相关信息和基本信息）
        admin_user = User.objects.create(
            username=username,
            password=make_password(admin_password),  # 加密存储密码
            user_type=User.ENTERPRISE_ADMIN,
            is_active=True,  # 激活用户
            first_name="企业管理员"  # 存储在User对象中
        )
        
        # 创建员工资料记录（存储企业相关信息）
        # 检查用户是否已有Staff记录
        staff, created = Staff.objects.get_or_create(
            user=admin_user,
            defaults={'enterprise': enterprise}
        )
        
        # 如果Staff记录已存在，更新企业信息
        if not created:
            staff.enterprise = enterprise
            staff.save()
        
        # 创建员工角色记录
        StaffRole.objects.create(
            staff=staff,
            role_type=StaffRole.ENTERPRISE_ADMIN,
            is_active=True
        )
        
        # 使用Django messages框架创建符合AdminLTE风格的成功消息
        messages.success(
            self.request,
            '<i class="fas fa-check-circle mr-2"></i>企业"%s"创建成功！' % form.cleaned_data['name'] +
            '<br><small class="text-sm text-gray-600">企业管理员账号: <strong>%s</strong>, 密码: <strong>%s</strong></small>' % (username, admin_password)
        )
        
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        # 处理表单验证失败的情况
        # 特别处理企业名称和统一社会信用代码重复的情况
        if 'name' in form.errors:
            # 检查是否是唯一性约束错误
            name_errors = str(form.errors['name']).lower()
            if 'unique' in name_errors or 'duplicate' in name_errors or '已存在' in name_errors:
                messages.error(
                    self.request,
                    '<i class="fas fa-exclamation-circle mr-2"></i>企业名称已存在，请使用其他名称！'
                )
            else:
                messages.error(
                    self.request,
                    f'<i class="fas fa-exclamation-circle mr-2"></i>企业名称: {form.errors["name"][0]}'
                )
        
        if 'unified_social_credit_code' in form.errors:
            # 检查是否是唯一性约束错误
            code_errors = str(form.errors['unified_social_credit_code']).lower()
            if 'unique' in code_errors or 'duplicate' in code_errors or '已存在' in code_errors:
                messages.error(
                    self.request,
                    '<i class="fas fa-exclamation-circle mr-2"></i>统一社会信用代码已存在，请检查输入！'
                )
            else:
                messages.error(
                    self.request,
                    f'<i class="fas fa-exclamation-circle mr-2"></i>统一社会信用代码: {form.errors["unified_social_credit_code"][0]}'
                )
        
        # 对于其他验证错误
        if not form.errors:
            messages.error(
                self.request,
                '<i class="fas fa-exclamation-circle mr-2"></i>表单验证失败，请检查输入内容！'
            )
        
        # 将错误信息保存到会话中，确保重定向后仍然可见
        self.request.session['form_errors'] = form.errors
        
        # 确保在表单返回时显示错误消息
        return self.render_to_response(self.get_context_data(form=form))

class EnterpriseUpdateView(EnterpriseAdminRequiredMixin, UpdateView):
    """更新企业信息"""
    model = Enterprise
    template_name = 'enterprises/enterprise_form.html'
    fields = [
        # 基本信息
        'name', 'unified_social_credit_code', 'enterprise_type', 'registered_address', 
        'legal_representative', 'registered_capital', 'establishment_date', 
        'business_term_start', 'business_term_end', 'registration_authority', 'business_scope',
        # 企业信息
        'contact_address', 'contact_phone', 'contact_email', 'website', 'logo',
        # 系统状态
        'is_active'
    ]
    success_url = reverse_lazy('enterprises:enterprise_list')
    
    def get_queryset(self):
        """限制查询集，确保企业管理员只能编辑自己的企业"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # 系统管理员可以编辑所有企业
        if user.is_superuser:
            return queryset
        
        # 企业管理员只能编辑自己的企业
        if user.is_enterprise_admin:
            # 通过staff模型获取企业信息
            if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
                return queryset.filter(id=user.staff.enterprise.id)
        
        # 其他用户没有权限编辑任何企业
        return queryset.none()
    
    def form_valid(self, form):
        # 使用Django messages框架创建符合AdminLTE风格的成功消息
        messages.success(
            self.request,
            '<i class="fas fa-check-circle mr-2"></i>企业"%s"更新成功！' % form.cleaned_data['name']
        )
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # 处理表单验证失败的情况
        # 特别处理企业名称和统一社会信用代码重复的情况
        if 'name' in form.errors:
            # 检查是否是唯一性约束错误
            name_errors = str(form.errors['name']).lower()
            if 'unique' in name_errors or 'duplicate' in name_errors or '已存在' in name_errors:
                messages.error(
                    self.request,
                    '<i class="fas fa-exclamation-circle mr-2"></i>企业名称已存在，请使用其他名称！'
                )
            else:
                messages.error(
                    self.request,
                    f'<i class="fas fa-exclamation-circle mr-2"></i>企业名称: {form.errors["name"][0]}'
                )
        
        if 'unified_social_credit_code' in form.errors:
            # 检查是否是唯一性约束错误
            code_errors = str(form.errors['unified_social_credit_code']).lower()
            if 'unique' in code_errors or 'duplicate' in code_errors or '已存在' in code_errors:
                messages.error(
                    self.request,
                    '<i class="fas fa-exclamation-circle mr-2"></i>统一社会信用代码已存在，请检查输入！'
                )
            else:
                messages.error(
                    self.request,
                    f'<i class="fas fa-exclamation-circle mr-2"></i>统一社会信用代码: {form.errors["unified_social_credit_code"][0]}'
                )
        
        # 对于其他验证错误
        if not form.errors:
            messages.error(
                self.request,
                '<i class="fas fa-exclamation-circle mr-2"></i>表单验证失败，请检查输入内容！'
            )
        
        # 将错误信息保存到会话中，确保重定向后仍然可见
        self.request.session['form_errors'] = form.errors
        
        # 确保在表单返回时显示错误消息
        return self.render_to_response(self.get_context_data(form=form))

class EnterpriseDetailView(SuperUserRequiredMixin, DetailView):
    """企业详情"""
    model = Enterprise
    template_name = 'enterprises/enterprise_detail.html'
    context_object_name = 'enterprise'

class SelectEnterpriseView(EnterpriseBaseView, ListView):
    """选择企业视图"""
    model = Enterprise
    template_name = 'enterprises/select_enterprise.html'
    context_object_name = 'enterprises'
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'super_admin':
            return Enterprise.objects.filter(is_active=True)
        else:
            # 普通用户只能看到自己所属的企业
            if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
                return Enterprise.objects.filter(id=user.staff.enterprise.id, is_active=True)
            return Enterprise.objects.none()
    
    def post(self, request, *args, **kwargs):
        """处理企业选择"""
        enterprise_id = request.POST.get('enterprise_id')
        if enterprise_id:
            try:
                enterprise = Enterprise.objects.get(id=enterprise_id, is_active=True)
                request.session['current_enterprise_id'] = enterprise.id
                messages.success(request, f"已切换到企业: {enterprise.name}")
            except Enterprise.DoesNotExist:
                messages.error(request, "企业不存在或已被禁用")
        
        return redirect('dashboard')

class EnterpriseSubscriptionView(SuperUserRequiredMixin, UpdateView):
    model = EnterpriseSubscription
    template_name = 'enterprises/subscription_form.html'
    fields = ['status', 'expires_at', 'config']  # 添加更多字段
    
    def get_success_url(self):
        messages.success(self.request, "订阅信息更新成功")
        return reverse_lazy('enterprises:enterprise_list')


# ========== 部门管理相关视图 ==========

class BaseDepartmentView(LoginRequiredMixin):
    """部门基础视图类"""
    model = Department
    context_object_name = 'department'
    
    def get_queryset(self):
        """限制查询集为当前用户所在企业的部门"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            queryset = queryset.filter(enterprise=user.staff.enterprise)
        else:
            queryset = queryset.none()
        return queryset

class DepartmentListView(EnterpriseAdminRequiredMixin, BaseDepartmentView, ListView):
    """部门列表视图"""
    template_name = 'enterprises/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20
    
    def get_queryset(self):
        """获取当前企业的部门列表，按层级关系排序"""
        queryset = super().get_queryset()
        # 只显示启用的部门
        queryset = queryset.filter(is_active=True)
        # 先获取所有根部门
        root_departments = queryset.filter(parent__isnull=True)
        # 然后递归获取子部门并组织
        departments = []
        for root_dept in root_departments.order_by('name'):
            departments.append(root_dept)
            departments.extend(self._get_nested_departments(root_dept, queryset))
        return departments
    
    def _get_nested_departments(self, parent, queryset, level=1):
        """递归获取子部门"""
        nested_departments = []
        # 从查询集中获取当前父部门的子部门
        children = queryset.filter(parent=parent).order_by('name')
        for child in children:
            # 添加层级标记，方便前端显示
            child.level = level
            nested_departments.append(child)
            # 递归获取下一级子部门
            nested_departments.extend(self._get_nested_departments(child, queryset, level + 1))
        return nested_departments
    
    def get_context_data(self, **kwargs):
        """添加额外上下文数据"""
        context = super().get_context_data(**kwargs)
        # 添加企业信息
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = None
        return context

class DepartmentCreateView(EnterpriseAdminRequiredMixin, BaseDepartmentView, CreateView):
    """创建部门视图"""
    template_name = 'enterprises/department_form.html'
    fields = ['name', 'code', 'parent', 'manager', 'description']
    success_url = reverse_lazy('enterprises:department_list')
    
    def get_form(self, form_class=None):
        """自定义表单，限制可选的父部门和负责人范围"""
        form = super().get_form(form_class)
        user = self.request.user
        
        # 限制父部门只能是当前企业的部门
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            form.fields['parent'].queryset = Department.objects.filter(
                enterprise=user.staff.enterprise,
                is_active=True
            ).exclude(id=self.kwargs.get('pk'))  # 防止自引用（更新时）
            
            # 限制负责人只能是当前企业的用户
            form.fields['manager'] = UserNameChoiceField(
                queryset=User.objects.filter(
                    staff_members__enterprise=user.staff.enterprise,
                    is_active=True
                ),
                required=False,
                label='部门负责人'
            )
        else:
            # 如果用户没有关联的企业，设置空查询集
            form.fields['parent'].queryset = Department.objects.none()
            form.fields['manager'].queryset = User.objects.none()
        
        return form
    
    def form_valid(self, form):
        """保存部门时自动设置所属企业"""
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            form.instance.enterprise = user.staff.enterprise
        response = super().form_valid(form)
        
        # 添加成功消息
        messages.success(
            self.request,
            f'<i class="fas fa-check-circle mr-2"></i>部门"{form.cleaned_data["name"]}"创建成功！'
        )
        
        return response
    
    def form_invalid(self, form):
        """处理表单验证失败的情况"""
        # 显示通用错误消息
        messages.error(
            self.request,
            '<i class="fas fa-exclamation-circle mr-2"></i>表单验证失败，请检查输入内容！'
        )
        
        return self.render_to_response(self.get_context_data(form=form))

class DepartmentUpdateView(EnterpriseAdminRequiredMixin, BaseDepartmentView, UpdateView):
    """更新部门视图"""
    template_name = 'enterprises/department_form.html'
    fields = ['name', 'code', 'parent', 'manager', 'description', 'is_active']
    success_url = reverse_lazy('enterprises:department_list')
    
    def get_form(self, form_class=None):
        """自定义表单，限制可选的父部门和负责人范围"""
        form = super().get_form(form_class)
        user = self.request.user
        
        # 限制父部门只能是当前企业的部门，并且不能是自己或自己的子部门
        current_department = self.get_object()
        excluded_ids = [current_department.id]
        # 添加所有子部门的ID到排除列表
        for child in current_department.get_all_children():
            excluded_ids.append(child.id)
        
        # 限制父部门只能是当前企业的部门
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            form.fields['parent'].queryset = Department.objects.filter(
                enterprise=user.staff.enterprise,
                is_active=True
            ).exclude(id__in=excluded_ids)
            
            # 限制负责人只能是当前企业的用户
            form.fields['manager'] = UserNameChoiceField(
                queryset=User.objects.filter(
                    staff_members__enterprise=user.staff.enterprise,
                    is_active=True
                ),
                required=False,
                label='部门负责人'
            )
        else:
            # 如果用户没有关联的企业，设置空查询集
            form.fields['parent'].queryset = Department.objects.none()
            form.fields['manager'].queryset = User.objects.none()
        
        return form
    
    def form_valid(self, form):
        """更新部门信息"""
        response = super().form_valid(form)
        
        # 添加成功消息
        messages.success(
            self.request,
            f'<i class="fas fa-check-circle mr-2"></i>部门"{form.cleaned_data["name"]}"更新成功！'
        )
        
        return response
    
    def form_invalid(self, form):
        """处理表单验证失败的情况"""
        # 显示通用错误消息
        messages.error(
            self.request,
            '<i class="fas fa-exclamation-circle mr-2"></i>表单验证失败，请检查输入内容！'
        )
        
        return self.render_to_response(self.get_context_data(form=form))

class DepartmentDetailView(EnterpriseAdminRequiredMixin, BaseDepartmentView, DetailView):
    """部门详情视图"""
    template_name = 'enterprises/department_detail.html'
    
    def get_context_data(self, **kwargs):
        """添加部门的用户和子部门信息"""
        context = super().get_context_data(**kwargs)
        department = self.get_object()
        
        # 获取部门的用户
        context['department_users'] = department.get_department_users()
        
        # 获取部门的子部门
        context['sub_departments'] = department.children.filter(is_active=True)
        
        return context

class DepartmentDeleteView(EnterpriseAdminRequiredMixin, BaseDepartmentView, DeleteView):
    """删除部门视图"""
    template_name = 'enterprises/department_confirm_delete.html'
    success_url = reverse_lazy('enterprises:department_list')
    
    def get_context_data(self, **kwargs):
        """添加额外的上下文数据"""
        context = super().get_context_data(**kwargs)
        department = self.get_object()
        
        # 计算子部门数量
        context['sub_department_count'] = department.children.filter(is_active=True).count()
        
        # 计算部门用户数量
        context['department_user_count'] = department.get_department_users().count()
        
        # 检查是否有子部门
        context['has_sub_departments'] = department.children.filter(is_active=True).exists()
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """处理删除操作"""
        department = self.get_object()
        department_name = department.name
        
        # 检查部门是否有子部门
        if department.children.filter(is_active=True).exists():
            messages.error(
                self.request,
                f'<i class="fas fa-exclamation-circle mr-2"></i>部门"{department_name}"下有子部门，不能直接删除！'
            )
            return redirect('enterprises:department_detail', pk=department.id)
            
        # 执行删除操作
        response = super().delete(request, *args, **kwargs)
        
        # 添加成功消息
        messages.success(
            self.request,
            f'<i class="fas fa-check-circle mr-2"></i>部门"{department_name}"已成功删除！'
        )
        
        return response
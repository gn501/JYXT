# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from JYXT.core.permissions import SuperUserRequiredMixin, EnterpriseAdminRequiredMixin
from .models import User
from staff.models import Staff, StaffRole

class BaseView(LoginRequiredMixin):
    """基础视图类"""
    pass

class CustomLoginView(LoginView):
    """自定义登录视图"""
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        """处理登录表单验证成功后的逻辑"""
        # 获取当前登录的用户（在父类form_valid前，我们需要先认证用户）
        user = form.get_user()
        
        # 清除之前可能存在的企业选择session - 关键修复点
        if 'current_enterprise_id' in self.request.session:
            del self.request.session['current_enterprise_id']
        
        # 检查用户是否有在职的企业任职记录
        employed_staffs = user.staff_members.filter(employment_status=Staff.EMPLOYED)
        
        # 根据用户情况设置success_url
        if getattr(user, 'is_super_admin', False):
            self.success_url = reverse_lazy('enterprises:enterprise_list')
        elif employed_staffs.count() == 0:
            self.success_url = reverse_lazy('dashboard')
        elif employed_staffs.count() == 1:
            self.success_url = reverse_lazy('dashboard')
        else:
            self.success_url = reverse_lazy('accounts:select_enterprise')
        
        # 现在执行父类的form_valid方法，它会使用我们已经设置好的success_url
        return super().form_valid(form)
    
    def get_success_url(self):
        # 优先使用form_valid中设置的success_url
        if hasattr(self, 'success_url'):
            return self.success_url
        # 否则使用默认逻辑
        user = self.request.user
        if getattr(user, 'is_super_admin', False):
            return reverse_lazy('enterprises:enterprise_list')
        else:
            return reverse_lazy('dashboard')

class CustomLogoutView(LogoutView):
    """自定义登出视图"""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "您已成功退出系统")
        return super().dispatch(request, *args, **kwargs)

class SelectEnterpriseView(LoginRequiredMixin, View):
    """企业选择视图"""
    template_name = 'accounts/select_enterprise.html'
    
    def get(self, request, *args, **kwargs):
        # 清除之前可能存在的企业选择session - 关键修复点
        if 'current_enterprise_id' in request.session:
            del request.session['current_enterprise_id']
        
        # 获取用户所有在职的企业任职记录
        employed_staffs = request.user.staff_members.filter(employment_status=Staff.EMPLOYED)
        
        # 如果用户只有一个在职企业，直接跳转到首页
        if employed_staffs.count() <= 1:
            return redirect('dashboard')
        
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
            
            # 可以在这里添加逻辑来设置用户当前选择的企业
            # 例如，使用session来存储用户当前选择的企业ID
            request.session['current_enterprise_id'] = enterprise_id
            
            return redirect('dashboard')
        except Staff.DoesNotExist:
            messages.error(request, "您没有选择企业的访问权限")
            return redirect('accounts:select_enterprise')

class UserListView(EnterpriseAdminRequiredMixin, ListView):
    """用户列表"""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 系统管理员（Django的is_superuser）和超级管理员可以看到所有用户
        if not (self.request.user.is_superuser or getattr(self.request.user, 'is_super_admin', False)):
            if hasattr(self.request.user, 'staff') and self.request.user.staff and self.request.user.staff.enterprise:
                queryset = queryset.filter(staff_members__enterprise=self.request.user.staff.enterprise)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context

class UserCreateView(EnterpriseAdminRequiredMixin, CreateView):
    """创建用户"""
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_form_class(self):
        # 从forms.py导入UserCreateForm
        from .forms import UserCreateForm
        return UserCreateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['user_id'] = self.kwargs.get('pk')  # 传递用户ID给表单
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context
    
    def form_valid(self, form):
        # 获取当前登录用户的企业
        current_user = self.request.user
        enterprise = None
        if hasattr(current_user, 'staff') and current_user.staff and current_user.staff.enterprise:
            enterprise = current_user.staff.enterprise
        
        # 获取手机号（用作用户名）
        enterprise_phone = form.cleaned_data['enterprise_phone']
        
        # 检查用户是否已存在
        try:
            user = User.objects.get(username=enterprise_phone)
            # 用户已存在，更新信息
            user.user_type = 'enterprise_user'  # 强制设置为企业用户
            user.first_name = form.cleaned_data['first_name']
            user.email = form.cleaned_data.get('email', '')
            user.is_active = form.cleaned_data['is_active']
            
            # 更新头像（如果有）
            if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
                user.avatar = form.cleaned_data['avatar']
            
            user.save()
        except User.DoesNotExist:
            # 用户不存在，创建新用户
            user = User.objects.create(
                username=enterprise_phone,
                first_name=form.cleaned_data['first_name'],
                email=form.cleaned_data.get('email', ''),
                user_type='enterprise_user',  # 默认设置为企业用户
                is_active=form.cleaned_data['is_active']
            )
            
            # 设置默认密码为手机号后六位
            if len(enterprise_phone) >= 6:
                password = enterprise_phone[-6:]
            else:
                password = '123456'  # 手机号过短的备用密码
            user.set_password(password)
            
            # 设置头像（如果有）
            if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
                user.avatar = form.cleaned_data['avatar']
            
            user.save()
        
        # 检查该用户是否在当前企业已有staff记录
        staff = None
        if enterprise:
            try:
                # 检查用户是否在当前企业已有staff记录
                staff = Staff.objects.get(user=user, enterprise=enterprise)
                # 用户在当前企业已有staff记录，更新信息
                staff.first_name = form.cleaned_data['first_name']
                staff.last_name = form.cleaned_data.get('last_name', '')
                staff.work_phone = form.cleaned_data.get('work_phone', '')
                staff.enterprise_email = form.cleaned_data.get('enterprise_email', '')
                staff.department = form.cleaned_data['department']
                staff.position = form.cleaned_data.get('position', '')
                staff.save()
            except Staff.DoesNotExist:
                # 用户在当前企业没有staff记录，创建新记录
                staff = Staff.objects.create(
                    user=user,
                    enterprise=enterprise,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data.get('last_name', ''),
                    work_phone=form.cleaned_data.get('work_phone', ''),
                    enterprise_phone=enterprise_phone,
                    enterprise_email=form.cleaned_data.get('enterprise_email', ''),
                    department=form.cleaned_data['department'],
                    position=form.cleaned_data.get('position', '')
                )
        
        # 确保员工角色记录存在
        if staff:
            staff_role, created = StaffRole.objects.get_or_create(
                staff=staff,
                defaults={
                    'role_type': 'regular_staff',  # 默认设置为普通员工
                    'is_active': form.cleaned_data['is_active']
                }
            )
            
            # 如果记录已存在，更新状态
            if not created:
                staff_role.is_active = form.cleaned_data['is_active']
                staff_role.save()
        
        messages.success(self.request, "用户创建成功")
        return redirect(self.success_url)

class UserUpdateView(EnterpriseAdminRequiredMixin, UpdateView):
    """更新用户信息"""
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_form_class(self):
        # 从forms.py导入UserUpdateForm
        from .forms import UserUpdateForm
        return UserUpdateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['user_id'] = self.kwargs.get('pk')  # 传递用户ID给表单
        return kwargs
    
    def get_initial(self):
        # 获取用户和员工资料对象
        user = User.objects.get(id=self.kwargs.get('pk'))
        staff = getattr(user, 'staff', None)
        
        # 设置表单初始值
        initial = {
            'username': user.username,  # 直接设置用户名初始值
            'email': user.email,
            'user_type': user.user_type,
            'is_active': user.is_active,
        }
        
        # 如果存在员工资料，添加员工字段的初始值
        if staff:
            initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'enterprise_phone': staff.enterprise_phone,
            })
        
        return initial
    
    def get_queryset(self):
        # 获取基础查询集
        queryset = User.objects.all()
        
        # 调试信息
        user = self.request.user
        pk = self.kwargs.get('pk')
        
        # 判断用户类型和权限
        is_super_admin = getattr(user, 'is_super_admin', False) or user.is_superuser
        is_enterprise_admin = getattr(user, 'is_enterprise_admin', False)
        
        # 应用权限过滤
        if not is_super_admin:
            if is_enterprise_admin:
                # 允许企业管理员查看所有企业管理员用户
                queryset = queryset.filter(user_type='enterprise_admin')
            elif hasattr(user, 'staff') and user.staff and user.staff.enterprise:
                # 普通企业用户只能查看自己企业的用户
                queryset = queryset.filter(staff_members__enterprise=user.staff.enterprise)
            else:
                # 没有企业关联的用户只能查看自己
                queryset = queryset.filter(id=user.id)
        
        # 额外安全检查 - 确保用户可以访问请求的对象
        if pk and not is_super_admin:
            try:
                target_user = User.objects.get(id=pk)
                if hasattr(target_user, 'staff') and target_user.staff and target_user.staff.enterprise and hasattr(user, 'staff') and user.staff and user.staff.enterprise and target_user.staff.enterprise != user.staff.enterprise and target_user.user_type != 'enterprise_admin':
                    # 确保不是跨企业访问非管理员用户
                    queryset = queryset.none()
            except User.DoesNotExist:
                pass
        
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context
    
    def form_valid(self, form):
        # 获取用户对象
        user = User.objects.get(id=self.kwargs.get('pk'))
        
        # 更新用户认证信息
        user.email = form.cleaned_data['email']
        user.user_type = form.cleaned_data['user_type']
        user.is_active = form.cleaned_data['is_active']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        # 获取当前用户所在的企业
        current_enterprise = None
        if hasattr(self.request.user, 'staff') and self.request.user.staff and self.request.user.staff.enterprise:
            current_enterprise = self.request.user.staff.enterprise
        
        # 获取或创建当前企业的员工资料对象
        if current_enterprise:
            staff, created = Staff.objects.get_or_create(user=user, enterprise=current_enterprise)
            
            # 更新员工资料信息
            staff.enterprise_phone = form.cleaned_data['enterprise_phone']
            staff.department = form.cleaned_data['department']  # 现在这个字段是一个Department对象
            staff.position = form.cleaned_data['position']
            
            staff.save()
        
        # 更新员工角色信息
        role, created = StaffRole.objects.get_or_create(staff=staff)
        role.role_type = form.cleaned_data['user_type']
        role.is_active = form.cleaned_data['is_active']
        role.save()
        
        messages.success(self.request, "用户信息更新成功")
        return redirect(self.success_url)

class ProfileView(BaseView, UpdateView):
    """用户个人资料"""
    model = User
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_form_class(self):
        # 从forms.py导入ProfileForm
        from .forms import ProfileForm
        return ProfileForm
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 使用更可靠的方式获取企业信息：直接从用户对象获取
        user = self.request.user
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            context['current_enterprise'] = user.staff.enterprise
        else:
            context['current_enterprise'] = getattr(self.request, 'enterprise', None)
        return context
    
    def get_initial(self):
        # 获取用户和员工资料对象
        user = self.request.user
        staff = getattr(user, 'staff', None)
        
        # 设置表单初始值
        initial = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        # 如果存在员工资料，添加员工字段的初始值
        if staff:
            initial.update({
                'enterprise_phone': staff.enterprise_phone,
                'department': staff.department,  # 现在这个字段是一个Department对象
                'position': staff.position,
            })
        
        return initial
        
    def get_form_kwargs(self):
        # 获取默认的表单kwargs
        kwargs = super().get_form_kwargs()
        # 移除instance参数，因为ProfileForm不支持这个参数
        kwargs.pop('instance', None)
        # 添加request到kwargs中，以便表单可以访问请求对象
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        # 获取用户对象
        user = self.request.user
        
        # 更新用户认证信息
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        
        # 获取当前用户所在的企业
        current_enterprise = None
        if hasattr(user, 'staff') and user.staff and user.staff.enterprise:
            current_enterprise = user.staff.enterprise
        
        # 获取或创建当前企业的员工资料对象
        if current_enterprise:
            staff, created = Staff.objects.get_or_create(user=user, enterprise=current_enterprise)
            
            # 更新员工资料信息
            staff.enterprise_phone = form.cleaned_data['enterprise_phone']
            staff.department = form.cleaned_data['department']  # 现在这个字段是一个Department对象
            staff.position = form.cleaned_data['position']
            
            staff.save()
        
        messages.success(self.request, "个人资料更新成功")
        return redirect(self.success_url)

class ChangePasswordView(BaseView, UpdateView):
    """修改密码"""
    model = User
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user

class UserDetailView(EnterpriseAdminRequiredMixin, DetailView):
    """用户详情"""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user'
    
    def get_queryset(self):
        # 获取基础查询集
        queryset = super().get_queryset()
        
        # 调试信息
        user = self.request.user
        pk = self.kwargs.get('pk')
        
        # 判断用户类型和权限
        is_super_admin = getattr(user, 'is_super_admin', False) or user.is_superuser
        is_enterprise_admin = getattr(user, 'is_enterprise_admin', False)
        
        # 应用权限过滤
        if not is_super_admin:
            if is_enterprise_admin:
                # 允许企业管理员查看所有企业管理员用户
                queryset = queryset.filter(user_type='enterprise_admin')
            elif hasattr(user, 'staff') and user.staff and user.staff.enterprise:
                # 普通企业用户只能查看自己企业的用户
                queryset = queryset.filter(staff_members__enterprise=user.staff.enterprise)
            else:
                # 没有企业关联的用户只能查看自己
                queryset = queryset.filter(id=user.id)
        
        # 额外安全检查 - 确保用户可以访问请求的对象
        if pk and not is_super_admin:
            try:
                target_user = User.objects.get(id=pk)
                if hasattr(target_user, 'staff') and target_user.staff and target_user.staff.enterprise and hasattr(user, 'staff') and user.staff and user.staff.enterprise and target_user.staff.enterprise != user.staff.enterprise and target_user.user_type != 'enterprise_admin':
                    # 确保不是跨企业访问非管理员用户
                    queryset = queryset.none()
            except User.DoesNotExist:
                pass
        
        return queryset
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from accounts.models import User
from .models import Staff, StaffRole
from .forms import StaffCreateForm, StaffUpdateForm, StaffProfileForm
from enterprises.models import Department

class EnterpriseAdminRequiredMixin(LoginRequiredMixin):
    """企业管理员权限验证混入类"""
    def dispatch(self, request, *args, **kwargs):
        # 检查用户是否登录
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 检查用户是否为企业管理员
        if not hasattr(request.user, 'staff') or not request.user.staff:
            messages.error(request, "您没有访问此页面的权限")
            return redirect('dashboard')
        
        # 获取用户的企业
        staff = request.user.staff
        if not staff.enterprise:
            messages.error(request, "您尚未关联到任何企业")
            return redirect('dashboard')
        
        # 检查用户是否为企业管理员角色
        try:
            staff_role = StaffRole.objects.get(staff=staff)
            if staff_role.role_type != 'enterprise_admin':
                messages.error(request, "只有企业管理员可以访问此页面")
                return redirect('dashboard')
        except StaffRole.DoesNotExist:
            messages.error(request, "您的企业角色信息不存在")
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)

class StaffListView(EnterpriseAdminRequiredMixin, ListView):
    """员工列表视图 - 显示企业的所有员工"""
    model = Staff
    template_name = 'staff/staff_list.html'
    context_object_name = 'staff_list'
    paginate_by = 20
    
    def get_queryset(self):
        # 获取当前用户的企业
        enterprise = self.request.user.staff.enterprise
        # 只显示当前企业的员工
        queryset = Staff.objects.filter(enterprise=enterprise).order_by('created_at')
        
        # 搜索功能
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(enterprise_phone__icontains=search_query) |
                Q(work_phone__icontains=search_query) |
                Q(position__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前企业信息到上下文
        context['current_enterprise'] = self.request.user.staff.enterprise
        # 添加搜索查询到上下文
        context['search_query'] = self.request.GET.get('search', '')
        return context

class StaffProfileView(LoginRequiredMixin, UpdateView):
    """员工个人资料视图 - 用于用户编辑自己的个人资料"""
    template_name = 'staff/staff_profile.html'
    success_url = reverse_lazy('staff:staff_profile')
    
    def get_form_class(self):
        return StaffProfileForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # 传递request对象给表单
        kwargs['instance'] = self.get_object()  # 传递staff实例给表单
        return kwargs
    
    def get_object(self, queryset=None):
        # 获取当前登录用户的staff记录
        try:
            return Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            # 如果staff记录不存在，创建一个新的关联到当前用户
            return Staff.objects.create(
                user=self.request.user,
                enterprise=None
            )
    
    def form_valid(self, form):
        # 更新用户信息
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.email = form.cleaned_data.get('email', '')
        
        # 更新头像（如果有）
        if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
            user.avatar = form.cleaned_data['avatar']
        
        user.save()
        
        # 更新员工信息
        staff = self.get_object()
        staff.work_phone = form.cleaned_data.get('work_phone', '')
        staff.enterprise_phone = form.cleaned_data['enterprise_phone']
        staff.enterprise_email = form.cleaned_data.get('enterprise_email', '')
        staff.position = form.cleaned_data.get('position', '')
        staff.bio = form.cleaned_data.get('bio', '')
        staff.save()
        
        messages.success(self.request, "个人资料更新成功")
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加页面标题
        context['page_title'] = '个人资料'
        # 添加当前企业信息到上下文（如果有）
        if hasattr(self.request.user, 'staff') and self.request.user.staff.enterprise:
            context['current_enterprise'] = self.request.user.staff.enterprise
        return context

class StaffCreateView(EnterpriseAdminRequiredMixin, CreateView):
    """员工创建视图 - 在企业中添加新员工"""
    template_name = 'staff/staff_form.html'
    success_url = reverse_lazy('staff:staff_list')
    
    def get_form_class(self):
        return StaffCreateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # 传递request对象给表单
        return kwargs
    
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
        
        # 检查该用户是否已有员工记录，如果有则更新，没有则创建
        staff = None
        if enterprise:
            # 首先检查用户是否已有staff记录
            try:
                staff = Staff.objects.get(user=user)
                # 用户已有staff记录，更新企业和相关信息
                staff.enterprise = enterprise
                staff.work_phone = form.cleaned_data.get('work_phone', '')
                staff.enterprise_phone = enterprise_phone
                staff.enterprise_email = form.cleaned_data.get('enterprise_email', '')
                staff.department = form.cleaned_data.get('department')
                staff.position = form.cleaned_data.get('position', '')
                staff.employment_status = form.cleaned_data.get('employment_status', Staff.EMPLOYED)
                staff.save()
            except Staff.DoesNotExist:
                # 用户没有staff记录，检查企业中是否已有该手机号的员工
                try:
                    staff = Staff.objects.get(enterprise=enterprise, enterprise_phone=enterprise_phone)
                    # 企业中已有该手机号的员工记录，更新用户关联和信息
                    staff.user = user
                    staff.work_phone = form.cleaned_data.get('work_phone', '')
                    staff.enterprise_email = form.cleaned_data.get('enterprise_email', '')
                    staff.department = form.cleaned_data.get('department')
                    staff.position = form.cleaned_data.get('position', '')
                    staff.employment_status = form.cleaned_data.get('employment_status', Staff.EMPLOYED)
                    staff.save()
                except Staff.DoesNotExist:
                    # 员工记录不存在，创建新记录
                    staff = Staff.objects.create(
                        user=user,
                        enterprise=enterprise,
                        work_phone=form.cleaned_data.get('work_phone', ''),
                        enterprise_phone=enterprise_phone,
                        enterprise_email=form.cleaned_data.get('enterprise_email', ''),
                        department=form.cleaned_data.get('department'),
                        position=form.cleaned_data.get('position', ''),
                        employment_status=form.cleaned_data.get('employment_status', Staff.EMPLOYED)
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
        
        messages.success(self.request, "员工创建成功")
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前企业信息到上下文
        context['current_enterprise'] = self.request.user.staff.enterprise
        return context

class StaffDetailView(EnterpriseAdminRequiredMixin, DetailView):
    """员工详情视图 - 显示员工的详细信息"""
    model = Staff
    template_name = 'staff/staff_detail.html'
    context_object_name = 'staff'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前企业信息到上下文
        context['current_enterprise'] = self.request.user.staff.enterprise
        # 获取员工角色信息
        try:
            context['staff_role'] = StaffRole.objects.get(staff=self.object)
        except StaffRole.DoesNotExist:
            context['staff_role'] = None
        return context

class StaffDeleteView(EnterpriseAdminRequiredMixin, DeleteView):
    """员工删除视图 - 删除企业中的员工"""
    model = Staff
    template_name = 'staff/staff_confirm_delete.html'
    success_url = reverse_lazy('staff:staff_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前企业信息到上下文
        context['current_enterprise'] = self.request.user.staff.enterprise
        return context
    
    def delete(self, request, *args, **kwargs):
        # 获取要删除的员工
        staff = self.get_object()
        staff_name = staff.user.first_name
        
        # 验证员工是否属于当前企业
        enterprise = request.user.staff.enterprise
        if staff.enterprise != enterprise:
            messages.error(request, "您只能删除本企业的员工")
            return redirect(self.success_url)
        
        # 执行删除操作
        response = super().delete(request, *args, **kwargs)
        
        messages.success(request, f"员工'{staff_name}'已成功删除")
        return response

class StaffUpdateView(EnterpriseAdminRequiredMixin, UpdateView):
    """员工更新视图 - 更新企业中的现有员工信息"""
    model = Staff
    template_name = 'staff/staff_form.html'
    success_url = reverse_lazy('staff:staff_list')
    
    def get_form_class(self):
        return StaffUpdateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # 传递request对象给表单
        kwargs['instance'] = self.get_object()  # 传递staff实例给表单
        return kwargs
    
    def form_valid(self, form):
        # 获取当前登录用户的企业
        current_user = self.request.user
        enterprise = current_user.staff.enterprise
        
        # 获取要更新的员工
        staff = self.get_object()
        
        # 验证员工是否属于当前企业
        if staff.enterprise != enterprise:
            messages.error(self.request, "您只能编辑本企业的员工")
            return redirect(self.success_url)
        
        # 更新用户信息
        user = staff.user
        user.first_name = form.cleaned_data['first_name']
        user.email = form.cleaned_data.get('email', '')
        user.user_type = 'enterprise_user'  # 强制设置为企业用户
        user.is_active = form.cleaned_data['is_active']
        
        # 更新头像（如果有）
        if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
            user.avatar = form.cleaned_data['avatar']
        
        user.save()
        
        # 更新员工信息
        staff.work_phone = form.cleaned_data.get('work_phone', '')
        staff.enterprise_phone = form.cleaned_data['enterprise_phone']
        staff.enterprise_email = form.cleaned_data.get('enterprise_email', '')
        staff.department = form.cleaned_data['department']
        staff.position = form.cleaned_data.get('position', '')
        staff.employment_status = form.cleaned_data.get('employment_status', Staff.EMPLOYED)
        staff.save()
        
        # 更新员工角色状态
        try:
            staff_role = StaffRole.objects.get(staff=staff)
            staff_role.is_active = form.cleaned_data['is_active']
            staff_role.save()
        except StaffRole.DoesNotExist:
            # 如果角色记录不存在，创建一个新的
            StaffRole.objects.create(
                staff=staff,
                role_type='regular_staff',  # 默认设置为普通员工
                is_active=form.cleaned_data['is_active']
            )
        
        messages.success(self.request, "员工信息更新成功")
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加当前企业信息到上下文
        context['current_enterprise'] = self.request.user.staff.enterprise
        return context

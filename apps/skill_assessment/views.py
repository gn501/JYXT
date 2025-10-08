# apps/skill_assessment/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import SkillStandard, AssessmentPlan

# 使用简单的视图基类，先让系统运行起来
class BaseView(LoginRequiredMixin):
    """基础视图类"""
    pass

class SkillAssessmentDashboardView(BaseView, TemplateView):
    """职业技能认定仪表盘"""
    template_name = 'skill_assessment/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enterprise = getattr(self.request, 'enterprise', None)
        
        if enterprise:
            # 统计信息
            context['total_standards'] = SkillStandard.objects.filter(enterprise=enterprise).count()
            context['active_plans'] = AssessmentPlan.objects.filter(
                enterprise=enterprise, 
            ).count()
            # 由于AssessmentRecord模型已被删除，暂时使用默认值
            context['total_records'] = 0
        
        return context

# 技能标准相关视图
class SkillStandardListView(BaseView, ListView):
    """技能标准列表"""
    model = SkillStandard
    template_name = 'skill_assessment/skill_standard_list.html'
    context_object_name = 'skill_standards'
    
    def get_queryset(self):
        enterprise = getattr(self.request, 'enterprise', None)
        if enterprise:
            return SkillStandard.objects.filter(enterprise=enterprise)
        return SkillStandard.objects.none()

class SkillStandardCreateView(BaseView, CreateView):
    """创建技能标准"""
    model = SkillStandard
    template_name = 'skill_assessment/skill_standard_form.html'
    fields = ['name', 'code', 'description', 'level']
    
    def form_valid(self, form):
        enterprise = getattr(self.request, 'enterprise', None)
        if enterprise:
            form.instance.enterprise = enterprise
            messages.success(self.request, "技能标准创建成功")
            return super().form_valid(form)
        else:
            messages.error(self.request, "请先选择企业")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('skill_assessment:skill_standard_list')

class SkillStandardUpdateView(BaseView, UpdateView):
    """更新技能标准"""
    model = SkillStandard
    template_name = 'skill_assessment/skill_standard_form.html'
    fields = ['name', 'code', 'description', 'level']
    
    def get_success_url(self):
        messages.success(self.request, "技能标准更新成功")
        return reverse_lazy('skill_assessment:skill_standard_list')

class SkillStandardDetailView(BaseView, DetailView):
    """技能标准详情"""
    model = SkillStandard
    template_name = 'skill_assessment/skill_standard_detail.html'

# 认定计划相关视图
class AssessmentPlanListView(BaseView, ListView):
    """认定计划列表"""
    model = AssessmentPlan
    template_name = 'skill_assessment/assessment_plan_list.html'
    context_object_name = 'assessment_plans'
    
    def get_queryset(self):
        enterprise = getattr(self.request, 'enterprise', None)
        if enterprise:
            return AssessmentPlan.objects.filter(enterprise=enterprise)
        return AssessmentPlan.objects.none()

class AssessmentPlanCreateView(BaseView, CreateView):
    """创建认定计划"""
    model = AssessmentPlan
    template_name = 'skill_assessment/assessment_plan_form.html'
    fields = ['title', 'skill_standard', 'plan_date', 'location', 'examiner']
    
    def form_valid(self, form):
        enterprise = getattr(self.request, 'enterprise', None)
        if enterprise:
            form.instance.enterprise = enterprise
            messages.success(self.request, "认定计划创建成功")
            return super().form_valid(form)
        else:
            messages.error(self.request, "请先选择企业")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('skill_assessment:assessment_plan_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # 只显示当前企业的技能标准
        enterprise = getattr(self.request, 'enterprise', None)
        if enterprise:
            form.fields['skill_standard'].queryset = SkillStandard.objects.filter(enterprise=enterprise)
        return form

class AssessmentPlanUpdateView(BaseView, UpdateView):
    """更新认定计划"""
    model = AssessmentPlan
    template_name = 'skill_assessment/assessment_plan_form.html'
    fields = ['title', 'skill_standard', 'plan_date', 'location', 'examiner']
    
    def get_success_url(self):
        messages.success(self.request, "认定计划更新成功")
        return reverse_lazy('skill_assessment:assessment_plan_list')

class AssessmentPlanDetailView(BaseView, DetailView):
    """认定计划详情"""
    model = AssessmentPlan
    template_name = 'skill_assessment/assessment_plan_detail.html'

# 认定记录相关视图 - 暂时注释，因为AssessmentRecord模型不存在
# class AssessmentRecordListView(BaseView, ListView):
#     """认定记录列表"""
#     model = AssessmentRecord
#     template_name = 'skill_assessment/assessment_record_list.html'
#     context_object_name = 'assessment_records'
#     
#     def get_queryset(self):
#         enterprise = getattr(self.request, 'enterprise', None)
#         if enterprise:
#             return AssessmentRecord.objects.filter(enterprise=enterprise)
#         return AssessmentRecord.objects.none()
# 
# class AssessmentRecordCreateView(BaseView, CreateView):
#     """创建认定记录"""
#     model = AssessmentRecord
#     template_name = 'skill_assessment/assessment_record_form.html'
#     fields = ['assessment_plan', 'participant_name', 'participant_id', 'score', 'result']
#     
#     def form_valid(self, form):
#         enterprise = getattr(self.request, 'enterprise', None)
#         if enterprise:
#             form.instance.enterprise = enterprise
#             messages.success(self.request, "认定记录创建成功")
#             return super().form_valid(form)
#         else:
#             messages.error(self.request, "请先选择企业")
#             return self.form_invalid(form)
#     
#     def get_success_url(self):
#         return reverse_lazy('skill_assessment:assessment_record_list')
#     
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         # 只显示当前企业的认定计划
#         enterprise = getattr(self.request, 'enterprise', None)
#         if enterprise:
#             form.fields['assessment_plan'].queryset = AssessmentPlan.objects.filter(enterprise=enterprise)
#         return form
# 
# class AssessmentRecordUpdateView(BaseView, UpdateView):
#     """更新认定记录"""
#     model = AssessmentRecord
#     template_name = 'skill_assessment/assessment_record_form.html'
#     fields = ['assessment_plan', 'participant_name', 'participant_id', 'score', 'result']
#     
#     def get_success_url(self):
#         messages.success(self.request, "认定记录更新成功")
#         return reverse_lazy('skill_assessment:assessment_record_list')

class AssessmentStatisticsView(BaseView, TemplateView):
    """认定统计"""
    template_name = 'skill_assessment/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enterprise = getattr(self.request, 'enterprise', None)
        
        if enterprise:
            # 基础统计 - 暂时注释，因为AssessmentRecord模型不存在
            # total_records = AssessmentRecord.objects.filter(enterprise=enterprise)
            # context['total_count'] = total_records.count()
            # context['passed_count'] = total_records.filter(result='passed').count()
            
            # 按技能标准统计 - 暂时注释，因为AssessmentRecord模型不存在
            # skill_stats = []
            # standards = SkillStandard.objects.filter(enterprise=enterprise)
            # for standard in standards:
            #     records = total_records.filter(assessment_plan__skill_standard=standard)
            #     if records.exists():
            #         skill_stats.append({
            #             'standard': standard,
            #             'total': records.count(),
            #             'passed': records.filter(result='passed').count(),
            #         })
            
            # 提供默认值避免模板错误
            context['total_count'] = 0
            context['passed_count'] = 0
            context['skill_stats'] = []
        
        return context
from django.contrib import admin

# Register your models here.
# 应该注册模型以便在 Django Admin 中管理
from django.contrib import admin
from .models import Enterprise, EnterpriseSubscription

@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ['name', 'unified_social_credit_code', 'legal_representative', 'is_active']
    list_filter = ['is_active', 'subscription_tier']
    search_fields = ['name', 'unified_social_credit_code']

@admin.register(EnterpriseSubscription)
class EnterpriseSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['enterprise', 'app_code', 'status', 'subscribed_at']
    list_filter = ['status', 'app_code']
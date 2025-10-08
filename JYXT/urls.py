# JYXT/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/')),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('enterprise-dashboard/', views.EnterpriseDashboardView.as_view(), name='enterprise_dashboard'),
    path('accounts/', include('accounts.urls')),
    path('enterprises/', include('enterprises.urls')),
    path('staff/', include('staff.urls')),
    path('apps/skill-assessment/', include('apps.skill_assessment.urls')),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
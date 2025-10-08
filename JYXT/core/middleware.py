# JYXT/core/middleware.py
from django.utils.deprecation import MiddlewareMixin

class TenantMiddleware(MiddlewareMixin):
    """多租户中间件"""
    
    def process_request(self, request):
        """处理请求，设置当前企业上下文"""
        if request.user.is_authenticated:
            # 系统管理员可以从session中选择企业
            if request.user.is_superuser:
                enterprise_id = request.session.get('current_enterprise_id')
                if enterprise_id:
                    try:
                        from enterprises.models import Enterprise
                        request.enterprise = Enterprise.objects.get(id=enterprise_id)
                    except Enterprise.DoesNotExist:
                        request.enterprise = None
                else:
                    request.enterprise = None
            # 企业用户使用其关联的企业
            elif hasattr(request.user, 'enterprise') and request.user.enterprise:
                request.enterprise = request.user.enterprise
            # 独立用户没有企业上下文
            else:
                request.enterprise = None
        else:
            request.enterprise = None
        
        return None
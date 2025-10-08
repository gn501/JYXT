# JYXT/core/registry.py
class AppRegistry:
    def __init__(self):
        self._apps = {}
    
    def register(self, app_code, config_class):
        """注册应用"""
        self._apps[app_code] = config_class
    
    def get_app_config(self, app_code):
        """获取应用配置"""
        return self._apps.get(app_code)
    
    def get_all_apps(self):
        """获取所有注册的应用"""
        return self._apps.items()
    
    def get_available_apps(self, enterprise=None):
        """获取可用的应用"""
        # 简化版本，后续可以添加企业订阅检查
        return self._apps

# 全局应用注册表
app_registry = AppRegistry()

class BaseAppConfig:
    """应用配置基类"""
    name = "未命名应用"
    code = "unknown"
    description = "应用描述"
    version = "1.0.0"
    models = []
    menu_items = []
    permissions = []
    settings = {}
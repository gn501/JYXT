from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 注册用户模型到admin后台
admin.site.register(User, UserAdmin)

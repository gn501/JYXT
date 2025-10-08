# accounts/management/commands/init_super_admin.py
from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = '初始化超级管理员账户'
    
    def handle(self, *args, **options):
        # 检查是否已存在超级管理员
        if User.objects.filter(user_type=User.SUPER_ADMIN).exists():
            self.stdout.write(
                self.style.WARNING('超级管理员账户已存在')
            )
            return
        
        # 创建超级管理员
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if not User.objects.filter(username=username).exists():
            super_admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # 设置用户类型为超级管理员
            super_admin.user_type = User.SUPER_ADMIN
            super_admin.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'超级管理员创建成功: {username}/{password}')
            )
        else:
            # 将现有管理员升级为超级管理员
            admin_user = User.objects.get(username=username)
            admin_user.user_type = User.SUPER_ADMIN
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'用户 {username} 已升级为超级管理员')
            )
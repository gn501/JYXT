# JYXT - 企业管理系统

## 项目简介
JYXT 是一个企业管理系统，提供了用户管理、企业管理、员工管理等功能，帮助企业高效管理内部资源和人员。

## 技术栈
- **后端框架**：Django 5.2.6
- **数据库**：SQLite（可配置为其他数据库）
- **前端**：Bootstrap、AdminLTE
- **语言**：Python 3.12

## 功能特点
- **用户管理**：用户注册、登录、权限控制
- **企业管理**：企业信息管理、部门管理
- **员工管理**：员工信息管理、职位管理、在职状态管理
- **技能评估**：员工技能评估功能

## 安装步骤

### 1. 克隆项目
```bash
# 从 GitHub 克隆项目（替换为你的实际仓库地址）
git clone https://github.com/your-username/jyxt.git
cd jyxt
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置数据库
项目默认使用 SQLite 数据库，如需使用其他数据库，请修改 `JYXT/settings.py` 文件中的数据库配置。

### 5. 执行数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 创建超级用户
```bash
python manage.py createsuperuser
```
按照提示输入用户名、邮箱和密码。

## 运行项目
```bash
python manage.py runserver
```
项目将在 http://127.0.0.1:8000/ 启动

## 访问管理后台
在浏览器中访问 http://127.0.0.1:8000/admin/，使用超级用户账号登录。

## 目录结构
```
JYXT/
├── JYXT/            # 项目核心配置
├── accounts/        # 用户账号相关功能
├── enterprises/     # 企业管理相关功能
├── staff/           # 员工管理相关功能
├── apps/            # 其他应用
├── templates/       # HTML 模板
├── static/          # 静态资源文件
├── media/           # 媒体文件（如用户头像、企业Logo）
├── manage.py        # Django 管理脚本
└── requirements.txt # 项目依赖列表
```

## 配置说明
### 环境变量配置
项目支持通过环境变量进行配置，主要配置项包括：
- SECRET_KEY：Django 密钥
- DEBUG：调试模式开关
- ALLOWED_HOSTS：允许的主机名
- DATABASE_URL：数据库连接字符串

### 媒体文件配置
默认情况下，用户上传的媒体文件（如头像、Logo）存储在 `media/` 目录下。

## 许可证
本项目采用 MIT 许可证。

## 注意事项
- 在生产环境中，请确保关闭 DEBUG 模式并设置安全的 SECRET_KEY
- 定期备份数据库以防止数据丢失
- 根据实际需求调整权限控制策略
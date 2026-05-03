# Phase 1 后端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 Docker + Django Ninja + PostgreSQL 构建小程序后端，实现 20 个用户端 API 接口

**Architecture:** 4 容器 Docker Compose（Nginx → Django → PG + MinIO），Django 按领域拆分 8 个 app，Ninja 路由统一注册，JWT 认证，统一 `{success, data/error}` 响应

**Tech Stack:** Python 3.12, Django 5.x, Django Ninja, PostgreSQL 16, MinIO, Gunicorn + Uvicorn, Nginx, Docker Compose

---

### Task 1: 项目骨架 — Docker 基础设施 + .env

**Files:**
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `nginx/default.conf`

- [ ] **Step 1: 创建 .env.example**

```bash
# .env.example
DB_PASSWORD=changeme
MINIO_PASSWORD=changeme
WX_APPID=your_appid
WX_SECRET=your_secret
JWT_SECRET=your_jwt_secret
```

- [ ] **Step 2: 创建 docker-compose.yml**

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: jiaoge
      POSTGRES_USER: jiaoge
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jiaoge"]
      interval: 5s
      timeout: 3s
      retries: 5

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      minio:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://jiaoge:${DB_PASSWORD}@db:5432/jiaoge
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: ${MINIO_PASSWORD}
      WX_APPID: ${WX_APPID}
      WX_SECRET: ${WX_SECRET}
      JWT_SECRET: ${JWT_SECRET}
      DJANGO_SECRET_KEY: ${JWT_SECRET}
      DEBUG: "true"
    ports:
      - "8000:8000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pgdata:
  minio_data:
```

- [ ] **Step 3: 创建 nginx/default.conf**

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    client_max_body_size 20M;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://backend;
    }

    location /static/ {
        alias /app/static/;
    }
}
```

---

### Task 2: Django 项目骨架 + requirements.txt

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/config/asgi.py`

- [ ] **Step 1: 创建 requirements.txt**

```
django>=5.0,<6.0
django-ninja>=1.0,<2.0
psycopg[binary]>=3.0
dj-database-url>=2.0
pyjwt>=2.0
minio>=7.0
django-storages[s3]>=1.0
requests>=2.0
gunicorn>=22.0
uvicorn>=0.30
django-cors-headers>=4.0
python-decouple>=3.0
```

- [ ] **Step 2: 创建 Dockerfile**

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

- [ ] **Step 3: 创建 manage.py**

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 创建 config/__init__.py**

空文件

- [ ] **Step 5: 创建 config/settings.py**

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "corsheaders",
    "storages",
    "core",
    "apps.auth_app",
    "apps.activity",
    "apps.theme",
    "apps.category",
    "apps.order",
    "apps.review",
    "apps.upload",
    "apps.config_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "postgres://jiaoge:jiaoge@localhost:5432/jiaoge"),
        conn_max_age=600,
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True
TIME_ZONE = "Asia/Shanghai"

# MinIO storage (django-storages)
AWS_S3_ENDPOINT_URL = f"http://{os.environ.get('MINIO_ENDPOINT', 'localhost:9000')}"
AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
AWS_S3_REGION_NAME = "us-east-1"
AWS_STORAGE_BUCKET_NAME = "jiaoge"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "path"
AWS_DEFAULT_ACL = "public-read"
```

- [ ] **Step 6: 创建 config/urls.py**

```python
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(
    title="交个朋友 API",
    version="1.0.0",
    docs_url="/api/docs",
)

# Routers will be added in later tasks
# api.add_router("/auth", auth_router, tags=["认证"])
# ...

urlpatterns = [
    path("api/", api.urls),
]
```

- [ ] **Step 7: 创建 config/wsgi.py**

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

- [ ] **Step 8: 创建 config/asgi.py**

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
```

- [ ] **Step 9: 创建 apps 目录结构**

```bash
mkdir -p backend/apps/auth_app
mkdir -p backend/apps/activity
mkdir -p backend/apps/theme
mkdir -p backend/apps/category
mkdir -p backend/apps/order
mkdir -p backend/apps/review
mkdir -p backend/apps/upload
mkdir -p backend/apps/config_app
mkdir -p backend/core
```

每个 app 目录下创建空的 `__init__.py`，`core` 目录下也创建 `__init__.py`。

---

### Task 3: Core — JWT 认证 + 全局异常 + 分页

**Files:**
- Create: `backend/core/__init__.py`
- Create: `backend/core/auth.py`
- Create: `backend/core/exceptions.py`
- Create: `backend/core/pagination.py`

- [ ] **Step 1: 创建 core/auth.py**

```python
import os
import jwt
from datetime import datetime, timedelta
from ninja.security import HttpBearer

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


def create_token(user_id: int, openid: str) -> str:
    payload = {
        "user_id": user_id,
        "openid": openid,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


class BearerAuth(HttpBearer):
    def authenticate(self, request, token: str):
        payload = verify_token(token)
        if payload is None:
            return None
        return payload
```

- [ ] **Step 2: 创建 core/exceptions.py**

```python
from ninja import NinjaAPI


def register_exception_handlers(api: NinjaAPI):
    @api.exception_handler(Exception)
    def global_handler(request, exc):
        return api.create_response(
            request,
            {"success": False, "error": str(exc)},
            status=500,
        )
```

- [ ] **Step 3: 创建 core/pagination.py**

```python
from typing import Generic, TypeVar
from pydantic import BaseModel
from ninja import Query

T = TypeVar("T")


class PaginationParams(Query):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    list: list[T]
    total: int
    page: int
    page_size: int
```

---

### Task 4: Auth App — User 模型 + 微信登录接口

**Files:**
- Create: `backend/apps/auth_app/__init__.py`
- Create: `backend/apps/auth_app/models.py`
- Create: `backend/apps/auth_app/schemas.py`
- Create: `backend/apps/auth_app/services.py`
- Create: `backend/apps/auth_app/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models


class User(models.Model):
    openid = models.CharField(max_length=64, unique=True)
    nick_name = models.CharField(max_length=100, default="微信用户")
    avatar_url = models.CharField(max_length=500, default="/images/avatar.png")
    phone = models.CharField(max_length=20, blank=True, default="")
    points = models.IntegerField(default=0)
    coupons = models.JSONField(default=list, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema
from datetime import datetime


class LoginRequest(Schema):
    code: str


class UserOut(Schema):
    id: int
    openid: str
    nick_name: str
    avatar_url: str
    phone: str
    points: int
    coupons: list = []
    created_time: datetime


class LoginResponse(Schema):
    token: str
    user: UserOut
    is_new: bool = False
```

- [ ] **Step 3: 创建 services.py**

```python
import os
import requests
from .models import User

WX_APPID = os.environ.get("WX_APPID", "")
WX_SECRET = os.environ.get("WX_SECRET", "")
WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


def get_openid_from_wx(code: str) -> str | None:
    resp = requests.get(WX_CODE2SESSION_URL, params={
        "appid": WX_APPID,
        "secret": WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }, timeout=10)
    data = resp.json()
    if "openid" in data:
        return data["openid"]
    return None


def login_with_code(code: str) -> tuple[User, bool]:
    openid = get_openid_from_wx(code)
    if not openid:
        raise Exception("微信登录失败: invalid code")

    from django.utils import timezone
    user, is_new = User.objects.get_or_create(
        openid=openid,
        defaults={"last_login_time": timezone.now()},
    )
    if not is_new:
        user.last_login_time = timezone.now()
        user.save(update_fields=["last_login_time"])
    return user, is_new
```

- [ ] **Step 4: 创建 routers.py**

```python
from ninja import Router
from core.auth import create_token
from .schemas import LoginRequest, LoginResponse, UserOut
from .services import login_with_code
from .models import User

router = Router()


@router.post("/login", response={200: dict, 400: dict})
def login(request, body: LoginRequest):
    user, is_new = login_with_code(body.code)
    token = create_token(user.id, user.openid)
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "openid": user.openid,
                "nick_name": user.nick_name,
                "avatar_url": user.avatar_url,
                "phone": user.phone,
                "points": user.points,
                "coupons": user.coupons or [],
                "created_time": user.created_time.isoformat(),
            },
            "is_new": is_new,
        },
    }
```

- [ ] **Step 5: 注册路由到 config/urls.py**

```python
# 在 config/urls.py 的 api 定义和 urlpatterns 之间添加:
from apps.auth_app.routers import router as auth_router
api.add_router("/auth", auth_router, tags=["认证"])
```

- [ ] **Step 6: 创建 migration 并验证**

```bash
cd backend
python manage.py makemigrations auth_app
python manage.py migrate
```

---

### Task 5: Activity App — 活动接口

**Files:**
- Create: `backend/apps/activity/__init__.py`
- Create: `backend/apps/activity/models.py`
- Create: `backend/apps/activity/schemas.py`
- Create: `backend/apps/activity/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models


class Activity(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.JSONField(default=list, blank=True)
    detail_images = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=50, blank=True, default="")
    time_category = models.CharField(max_length=50, blank=True, default="")
    group_category = models.CharField(max_length=50, blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")
    duration = models.CharField(max_length=50, blank=True, default="")
    difficulty = models.CharField(max_length=50, blank=True, default="")
    min_people = models.IntegerField(default=2)
    max_people = models.IntegerField(default=20)
    club = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    detail = models.TextField(blank=True, default="")
    display_type = models.CharField(max_length=20, default="small")
    is_new = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="上架")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    rating_count = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    theme_id = models.BigIntegerField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activities"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["time_category"]),
            models.Index(fields=["group_category"]),
            models.Index(fields=["status"]),
        ]
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema
from datetime import datetime


class ClubSchema(Schema):
    name: str = ""
    logo: str = ""
    location: str = ""


class ActivityBrief(Schema):
    id: int
    title: str
    price: float
    images: list = []
    category: str = ""
    time_category: str = ""
    group_category: str = ""
    location: str = ""
    duration: str = ""
    difficulty: str = ""
    min_people: int = 2
    max_people: int = 20
    club: ClubSchema | None = None
    tags: list = []
    display_type: str = "small"
    is_new: bool = False
    rating: float = 5.0
    rating_count: int = 0
    sold_count: int = 0
    theme_id: int | None = None


class ActivityDetail(ActivityBrief):
    detail_images: list = []
    detail: str = ""
    status: str = ""
    created_time: datetime | None = None
    updated_time: datetime | None = None
```

- [ ] **Step 3: 创建 routers.py**

```python
from ninja import Router, Query
from django.db.models import Q
from core.pagination import PaginationParams
from .models import Activity
from .schemas import ActivityBrief, ActivityDetail

router = Router()


def activity_to_brief(a: Activity) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "price": float(a.price),
        "images": a.images or [],
        "category": a.category,
        "time_category": a.time_category,
        "group_category": a.group_category,
        "location": a.location,
        "duration": a.duration,
        "difficulty": a.difficulty,
        "min_people": a.min_people,
        "max_people": a.max_people,
        "club": a.club or {},
        "tags": a.tags or [],
        "display_type": a.display_type,
        "is_new": a.is_new,
        "rating": float(a.rating),
        "rating_count": a.rating_count,
        "sold_count": a.sold_count,
        "theme_id": a.theme_id,
    }


def activity_to_detail(a: Activity) -> dict:
    base = activity_to_brief(a)
    base.update({
        "detail_images": a.detail_images or [],
        "detail": a.detail,
        "status": a.status,
        "created_time": a.created_time,
        "updated_time": a.updated_time,
    })
    return base


@router.get("", response=dict)
def list_activities(
    request,
    pagination: PaginationParams = Query(...),
    status: str = "上架",
    category: str | None = None,
    time_category: str | None = None,
    group_category: str | None = None,
):
    qs = Activity.objects.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if time_category:
        qs = qs.filter(time_category=time_category)
    if group_category:
        qs = qs.filter(group_category=group_category)

    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    activities = qs.order_by("-created_time")[offset:offset + pagination.page_size]

    return {
        "success": True,
        "data": {
            "list": [activity_to_brief(a) for a in activities],
            "total": total,
        },
    }


@router.get("/{activity_id}", response=dict)
def get_activity(request, activity_id: int):
    try:
        a = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return {"success": False, "error": "活动不存在"}
    return {"success": True, "data": activity_to_detail(a)}
```

- [ ] **Step 4: 注册路由**

```python
# config/urls.py 添加:
from apps.activity.routers import router as activity_router
api.add_router("/activities", activity_router, tags=["活动"])
```

- [ ] **Step 5: makemigrations + migrate**

```bash
cd backend
python manage.py makemigrations activity
python manage.py migrate
```

---

### Task 6: Theme App — 主题接口

**Files:**
- Create: `backend/apps/theme/__init__.py`
- Create: `backend/apps/theme/models.py`
- Create: `backend/apps/theme/schemas.py`
- Create: `backend/apps/theme/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models


class Theme(models.Model):
    name = models.CharField(max_length=100)
    cover_image = models.CharField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    sort = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="显示")
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "themes"
        indexes = [models.Index(fields=["status", "sort"])]
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema


class ThemeOut(Schema):
    id: int
    name: str
    cover_image: str = ""
    description: str = ""
    sort: int = 0
    status: str = ""
```

- [ ] **Step 3: 创建 routers.py**

```python
from ninja import Router
from .models import Theme

router = Router()


@router.get("", response=dict)
def list_themes(request):
    themes = Theme.objects.filter(status="显示").order_by("sort")
    return {
        "success": True,
        "data": {
            "list": [
                {
                    "id": t.id,
                    "name": t.name,
                    "cover_image": t.cover_image,
                    "description": t.description,
                    "sort": t.sort,
                    "status": t.status,
                }
                for t in themes
            ],
        },
    }
```

- [ ] **Step 4: 注册路由**

```python
# config/urls.py 添加:
from apps.theme.routers import router as theme_router
api.add_router("/themes", theme_router, tags=["主题"])
```

- [ ] **Step 5: makemigrations + migrate**

---

### Task 7: Category App — 分类接口 + 种子数据

**Files:**
- Create: `backend/apps/category/__init__.py`
- Create: `backend/apps/category/models.py`
- Create: `backend/apps/category/schemas.py`
- Create: `backend/apps/category/routers.py`
- Create: `backend/apps/category/migrations/0002_seed_data.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, default="")
    type = models.CharField(max_length=20)
    sort = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["type", "sort"]),
        ]
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema


class CategoryOut(Schema):
    id: int
    name: str
    icon: str = ""
    type: str
    sort: int = 0
```

- [ ] **Step 3: 创建 routers.py**

```python
from ninja import Router
from .models import Category

router = Router()


@router.get("", response=dict)
def list_categories(request):
    categories = Category.objects.all().order_by("type", "sort")
    return {
        "success": True,
        "data": {
            "list": [
                {
                    "id": c.id,
                    "name": c.name,
                    "icon": c.icon,
                    "type": c.type,
                    "sort": c.sort,
                }
                for c in categories
            ],
        },
    }
```

- [ ] **Step 4: 注册路由**

```python
# config/urls.py 添加:
from apps.category.routers import router as category_router
api.add_router("/categories", category_router, tags=["分类"])
```

- [ ] **Step 5: 创建种子数据 migration**

```bash
cd backend
python manage.py makemigrations category --empty --name seed_data
```

修改 `apps/category/migrations/0002_seed_data.py`:

```python
from django.db import migrations

SEED_DATA = [
    {"name": "户外徒步", "icon": "hiking", "type": "activity", "sort": 1},
    {"name": "民俗体验", "icon": "festival", "type": "activity", "sort": 2},
    {"name": "手作艺术", "icon": "palette", "type": "activity", "sort": 3},
    {"name": "地道美食", "icon": "restaurant", "type": "activity", "sort": 4},
    {"name": "露营时光", "icon": "camping", "type": "activity", "sort": 5},
    {"name": "亲子研学", "icon": "child_care", "type": "activity", "sort": 6},
    {"name": "艺术沙龙", "icon": "theater_comedy", "type": "activity", "sort": 7},
    {"name": "山野寻踪", "icon": "landscape", "type": "activity", "sort": 8},
    {"name": "单日活动", "icon": "today", "type": "time", "sort": 1},
    {"name": "多日进阶", "icon": "date_range", "type": "time", "sort": 2},
    {"name": "儿童", "icon": "child_friendly", "type": "group", "sort": 1},
    {"name": "家庭", "icon": "family_restroom", "type": "group", "sort": 2},
    {"name": "情侣闺蜜好友", "icon": "group", "type": "group", "sort": 3},
]


def insert_seed(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    for item in SEED_DATA:
        Category.objects.get_or_create(
            name=item["name"], type=item["type"],
            defaults={"icon": item["icon"], "sort": item["sort"]},
        )


def remove_seed(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    for item in SEED_DATA:
        Category.objects.filter(name=item["name"], type=item["type"]).delete()


class Migration(migrations.Migration):
    dependencies = [("category", "0001_initial")]
    operations = [migrations.RunPython(insert_seed, remove_seed)]
```

- [ ] **Step 6: makemigrations + migrate**

---

### Task 8: Config App — 系统配置接口

**Files:**
- Create: `backend/apps/config_app/__init__.py`
- Create: `backend/apps/config_app/models.py`
- Create: `backend/apps/config_app/schemas.py`
- Create: `backend/apps/config_app/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models


class Config(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField(blank=True, default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "config"
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema


class ConfigPublicOut(Schema):
    contact_phone: str = ""
    service_time: str = ""
    app_version: str = ""
```

- [ ] **Step 3: 创建 routers.py**

```python
from ninja import Router
from .models import Config

router = Router()

PUBLIC_KEYS = ["contactPhone", "serviceTime", "appVersion"]


@router.get("/public", response=dict)
def public_config(request):
    configs = {c.key: c.value for c in Config.objects.filter(key__in=PUBLIC_KEYS)}
    return {
        "success": True,
        "data": {
            "contactPhone": configs.get("contactPhone", ""),
            "serviceTime": configs.get("serviceTime", ""),
            "appVersion": configs.get("appVersion", ""),
        },
    }
```

- [ ] **Step 4: 注册路由**

```python
# config/urls.py 添加:
from apps.config_app.routers import router as config_router
api.add_router("/config", config_router, tags=["配置"])
```

- [ ] **Step 5: makemigrations + migrate**

---

### Task 9: Order App — 订单 + 支付 mock

**Files:**
- Create: `backend/apps/order/__init__.py`
- Create: `backend/apps/order/models.py`
- Create: `backend/apps/order/schemas.py`
- Create: `backend/apps/order/services.py`
- Create: `backend/apps/order/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models
from apps.auth_app.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ("待付款", "待付款"),
        ("已付款", "已付款"),
        ("已退款", "已退款"),
        ("已取消", "已取消"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    openid = models.CharField(max_length=64)
    activity_id = models.BigIntegerField()
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="待付款", choices=STATUS_CHOICES)
    contact_name = models.CharField(max_length=50, blank=True, default="")
    contact_phone = models.CharField(max_length=20, blank=True, default="")
    remark = models.CharField(max_length=500, blank=True, default="")
    pay_time = models.DateTimeField(null=True, blank=True)
    pay_method = models.CharField(max_length=50, blank=True, default="")
    refund_time = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=64, blank=True, default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["openid"]),
            models.Index(fields=["activity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_time"]),
        ]
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema
from datetime import datetime


class CreateOrderRequest(Schema):
    activity_id: int
    quantity: int = 1
    total_amount: float
    contact_name: str = ""
    contact_phone: str = ""
    remark: str = ""


class PayCallbackRequest(Schema):
    order_id: int


class OrderOut(Schema):
    id: int
    user_id: int
    openid: str = ""
    activity_id: int
    quantity: int = 1
    total_amount: float
    status: str = "待付款"
    contact_name: str = ""
    contact_phone: str = ""
    remark: str = ""
    pay_time: datetime | None = None
    pay_method: str = ""
    refund_time: datetime | None = None
    transaction_id: str = ""
    created_time: datetime | None = None
```

- [ ] **Step 3: 创建 services.py**

```python
import uuid
from datetime import datetime
from .models import Order


def mock_payment_params(order: Order) -> dict:
    return {
        "timeStamp": str(int(datetime.now().timestamp())),
        "nonceStr": uuid.uuid4().hex[:32],
        "package": "prepay_id=mock_" + uuid.uuid4().hex[:16],
        "signType": "MD5",
        "paySign": "MOCK_PAY_SIGN",
    }


def simulate_pay_callback(order: Order) -> None:
    from django.utils import timezone
    order.status = "已付款"
    order.pay_time = timezone.now()
    order.pay_method = "微信支付(MOCK)"
    order.transaction_id = "MOCK_TXN_" + uuid.uuid4().hex[:16]
    order.save()


def simulate_refund(order: Order) -> None:
    from django.utils import timezone
    if order.status != "已付款":
        raise Exception("只有已付款的订单可以退款")
    order.status = "已退款"
    order.refund_time = timezone.now()
    order.save()
```

- [ ] **Step 4: 创建 routers.py**

```python
from ninja import Router
from django.shortcuts import get_object_or_404
from core.auth import BearerAuth
from core.pagination import PaginationParams
from .models import Order
from .schemas import CreateOrderRequest, PayCallbackRequest
from .services import mock_payment_params, simulate_pay_callback, simulate_refund

router = Router(auth=BearerAuth())


@router.post("", response=dict)
def create_order(request, body: CreateOrderRequest):
    payload = request.auth
    order = Order.objects.create(
        user_id=payload["user_id"],
        openid=payload["openid"],
        activity_id=body.activity_id,
        quantity=body.quantity,
        total_amount=body.total_amount,
        contact_name=body.contact_name,
        contact_phone=body.contact_phone,
        remark=body.remark,
    )
    payment_params = mock_payment_params(order)
    return {
        "success": True,
        "data": {"order_id": order.id, "payment_params": payment_params},
    }


@router.get("", response=dict)
def list_orders(request, pagination: PaginationParams):
    payload = request.auth
    qs = Order.objects.filter(user_id=payload["user_id"]).order_by("-created_time")
    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    orders = qs[offset:offset + pagination.page_size]

    def order_to_dict(o):
        return {
            "id": o.id, "user_id": o.user_id, "openid": o.openid,
            "activity_id": o.activity_id, "quantity": o.quantity,
            "total_amount": float(o.total_amount), "status": o.status,
            "contact_name": o.contact_name, "contact_phone": o.contact_phone,
            "remark": o.remark, "pay_time": o.pay_time, "pay_method": o.pay_method,
            "refund_time": o.refund_time, "transaction_id": o.transaction_id,
            "created_time": o.created_time.isoformat() if o.created_time else None,
        }

    return {"success": True, "data": {"list": [order_to_dict(o) for o in orders], "total": total}}


@router.get("/{order_id}", response=dict)
def get_order(request, order_id: int):
    payload = request.auth
    order = get_object_or_404(Order, id=order_id, user_id=payload["user_id"])
    return {
        "success": True,
        "data": {
            "id": order.id, "user_id": order.user_id, "openid": order.openid,
            "activity_id": order.activity_id, "quantity": order.quantity,
            "total_amount": float(order.total_amount), "status": order.status,
            "contact_name": order.contact_name, "contact_phone": order.contact_phone,
            "remark": order.remark, "pay_time": order.pay_time, "pay_method": order.pay_method,
            "refund_time": order.refund_time, "transaction_id": order.transaction_id,
            "created_time": order.created_time.isoformat() if order.created_time else None,
        },
    }


@router.post("/pay-callback", response=dict, auth=None)
def pay_callback(request, body: PayCallbackRequest):
    order = get_object_or_404(Order, id=body.order_id)
    simulate_pay_callback(order)
    return {"success": True, "data": {"status": order.status}}


@router.post("/{order_id}/refund", response=dict)
def refund_order(request, order_id: int):
    payload = request.auth
    order = get_object_or_404(Order, id=order_id, user_id=payload["user_id"])
    simulate_refund(order)
    return {"success": True, "data": {"status": order.status}}
```

- [ ] **Step 5: 注册路由**

```python
# config/urls.py 添加:
from apps.order.routers import router as order_router
api.add_router("/orders", order_router, tags=["订单"])
```

- [ ] **Step 6: makemigrations + migrate**

---

### Task 10: Review App — 评价接口

**Files:**
- Create: `backend/apps/review/__init__.py`
- Create: `backend/apps/review/models.py`
- Create: `backend/apps/review/schemas.py`
- Create: `backend/apps/review/routers.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 创建 models.py**

```python
from django.db import models
from apps.auth_app.models import User


class Review(models.Model):
    activity_id = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    order_id = models.BigIntegerField(null=True, blank=True)
    rating = models.SmallIntegerField()
    content = models.TextField(blank=True, default="")
    images = models.JSONField(default=list, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        indexes = [
            models.Index(fields=["activity_id"]),
            models.Index(fields=["user"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "user"], name="unique_order_user_review"
            ),
        ]
```

- [ ] **Step 2: 创建 schemas.py**

```python
from ninja import Schema
from datetime import datetime


class CreateReviewRequest(Schema):
    activity_id: int
    rating: int
    content: str = ""
    images: list = []
    order_id: int | None = None


class ReviewOut(Schema):
    id: int
    activity_id: int
    user_id: int
    user_name: str = ""
    avatar_url: str = ""
    rating: int
    content: str = ""
    images: list = []
    created_time: datetime | None = None
```

- [ ] **Step 3: 创建 routers.py**

```python
from ninja import Router
from django.db import IntegrityError
from core.auth import BearerAuth
from core.pagination import PaginationParams
from .models import Review
from .schemas import CreateReviewRequest

router = Router()


@router.get("", response=dict)
def list_reviews(request, activity_id: int, pagination: PaginationParams):
    qs = Review.objects.filter(activity_id=activity_id).order_by("-created_time")
    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    reviews = qs[offset:offset + pagination.page_size]

    return {
        "success": True,
        "data": {
            "list": [
                {
                    "id": r.id, "activity_id": r.activity_id, "user_id": r.user_id,
                    "user_name": r.user.nick_name, "avatar_url": r.user.avatar_url,
                    "rating": r.rating, "content": r.content,
                    "images": r.images or [], "created_time": r.created_time.isoformat(),
                }
                for r in reviews
            ],
            "total": total,
        },
    }


@router.post("", response=dict, auth=BearerAuth())
def create_review(request, body: CreateReviewRequest):
    payload = request.auth
    try:
        review = Review.objects.create(
            activity_id=body.activity_id,
            user_id=payload["user_id"],
            order_id=body.order_id,
            rating=body.rating,
            content=body.content,
            images=body.images,
        )
    except IntegrityError:
        return {"success": False, "error": "该订单已评价"}

    return {
        "success": True,
        "data": {
            "id": review.id, "activity_id": review.activity_id,
            "user_id": review.user_id, "rating": review.rating,
            "content": review.content, "images": review.images or [],
            "created_time": review.created_time.isoformat(),
        },
    }
```

- [ ] **Step 4: 注册路由**

```python
# config/urls.py 添加:
from apps.review.routers import router as review_router
api.add_router("/reviews", review_router, tags=["评价"])
```

- [ ] **Step 5: makemigrations + migrate**

---

### Task 11: Upload App — MinIO 文件上传

**Files:**
- Create: `backend/apps/upload/__init__.py`
- Create: `backend/apps/upload/services.py`
- Create: `backend/apps/upload/routers.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/config/settings.py` (add MinIO bucket init)

- [ ] **Step 1: 创建 services.py**

```python
import os
import uuid
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "jiaoge"


def get_minio_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def ensure_bucket():
    client = get_minio_client()
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"],
                }
            ],
        }
        client.set_bucket_policy(BUCKET_NAME, json.dumps(policy))


def upload_file(file_data, file_name: str, category: str = "general") -> str:
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    object_name = f"{category}/{uuid.uuid4().hex}.{ext}"
    client = get_minio_client()
    client.put_object(
        BUCKET_NAME, object_name, file_data, length=-1, part_size=10 * 1024 * 1024,
        content_type=file_data.content_type if hasattr(file_data, "content_type") else "application/octet-stream",
    )
    return f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"


def delete_file(object_name: str):
    client = get_minio_client()
    client.remove_object(BUCKET_NAME, object_name)
```

- [ ] **Step 2: 创建 routers.py**

```python
import json
from ninja import Router, UploadedFile, File
from core.auth import BearerAuth
from .services import upload_file, delete_file

router = Router(auth=BearerAuth())


@router.post("", response=dict)
def upload_single(request, file: UploadedFile = File(...), category: str = "general"):
    url = upload_file(file, file.name, category)
    return {"success": True, "data": {"url": url}}


@router.post("/batch", response=dict)
def upload_batch(request, files: list[UploadedFile] = File(...), category: str = "general"):
    urls = [upload_file(f, f.name, category) for f in files]
    return {"success": True, "data": {"urls": urls}}


@router.delete("/{object_name:path}", response=dict)
def remove_file(request, object_name: str):
    delete_file(object_name)
    return {"success": True, "data": None}
```

- [ ] **Step 3: 注册路由**

```python
# config/urls.py 添加:
from apps.upload.routers import router as upload_router
api.add_router("/upload", upload_router, tags=["上传"])
```

- [ ] **Step 4: 在 settings.py 末尾添加 MinIO bucket 初始化**

```python
# settings.py 末尾:
import importlib.util
if importlib.util.find_spec("apps.upload"):
    from apps.upload.services import ensure_bucket
    try:
        ensure_bucket()
    except Exception:
        pass  # MinIO not available yet (e.g. during collectstatic)
```

---

### Task 12: Admin Users 模型预留

**Files:**
- Create: `backend/apps/auth_app/models.py` (追加 AdminUser)

- [ ] **Step 1: 在 auth_app/models.py 追加 AdminUser**

```python
# 追加到 apps/auth_app/models.py 末尾:
class AdminUser(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, default="admin")
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_users"
```

- [ ] **Step 2: makemigrations + migrate**

---

### Task 13: 全局异常处理器注册 + 最终集成

**Files:**
- Modify: `backend/config/urls.py`

- [ ] **Step 1: 在 config/urls.py 注册异常处理器，最终完整版**

```python
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(
    title="交个朋友 API",
    version="1.0.0",
    docs_url="/api/docs",
)

# 全局异常处理
from core.exceptions import register_exception_handlers
register_exception_handlers(api)

# 路由注册
from apps.auth_app.routers import router as auth_router
from apps.activity.routers import router as activity_router
from apps.theme.routers import router as theme_router
from apps.category.routers import router as category_router
from apps.config_app.routers import router as config_router
from apps.order.routers import router as order_router
from apps.review.routers import router as review_router
from apps.upload.routers import router as upload_router

api.add_router("/auth", auth_router, tags=["认证"])
api.add_router("/activities", activity_router, tags=["活动"])
api.add_router("/themes", theme_router, tags=["主题"])
api.add_router("/categories", category_router, tags=["分类"])
api.add_router("/config", config_router, tags=["配置"])
api.add_router("/orders", order_router, tags=["订单"])
api.add_router("/reviews", review_router, tags=["评价"])
api.add_router("/upload", upload_router, tags=["上传"])

urlpatterns = [
    path("api/", api.urls),
]
```

---

### Task 14: 最终验证 — Docker Compose 启动 + API 冒烟测试

- [ ] **Step 1: 复制 .env**

```bash
cp .env.example .env
# 编辑 .env 填入真实值（或保留开发默认值）
```

- [ ] **Step 2: 启动全部服务**

```bash
docker-compose up -d --build
```

- [ ] **Step 3: 验证服务状态**

```bash
docker-compose ps
# 预期: db, minio, backend, nginx 全部 Up
```

- [ ] **Step 4: 验证数据库迁移**

```bash
docker-compose exec backend python manage.py showmigrations
# 预期: 所有 migration 标记为 [X]
```

- [ ] **Step 5: 验证 API docs 可访问**

```bash
curl http://localhost/api/docs
# 预期: 返回 Swagger HTML 页面
```

- [ ] **Step 6: 冒烟测试 — 公开接口**

```bash
# 分类接口
curl http://localhost/api/categories
# 预期: { "success": true, "data": { "list": [...] } }

# 主题接口
curl http://localhost/api/themes

# 公开配置
curl http://localhost/api/config/public

# 活动列表（空数据正常）
curl http://localhost/api/activities
```

- [ ] **Step 7: 冒烟测试 — 认证接口**

```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code": "test_fake_code"}'
# 预期: 微信 API 报错（code 无效），返回 { "success": false, "error": "微信登录失败: invalid code" }
```

---

## 计划总结

| 序号 | 任务 | 产出 |
|------|------|------|
| 1 | Docker 基础设施 | docker-compose.yml, nginx/default.conf, .env.example |
| 2 | Django 骨架 | settings.py, urls.py, wsgi.py, asgi.py, manage.py, Dockerfile, requirements.txt |
| 3 | Core 模块 | auth.py (JWT), exceptions.py, pagination.py |
| 4 | Auth App | User 模型, 微信登录接口 |
| 5 | Activity App | Activity 模型, 列表+详情接口 |
| 6 | Theme App | Theme 模型, 列表接口 |
| 7 | Category App | Category 模型, 列表接口, 种子数据 |
| 8 | Config App | Config 模型, 公开配置接口 |
| 9 | Order App | Order 模型, CRUD + 支付 mock |
| 10 | Review App | Review 模型, 列表+提交接口 |
| 11 | Upload App | MinIO 文件上传 |
| 12 | Admin 预留 | AdminUser 模型 |
| 13 | 最终集成 | 异常处理器 + 全部路由注册 |
| 14 | 验证 | Docker 启动 + 冒烟测试 |

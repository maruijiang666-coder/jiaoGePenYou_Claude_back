# Phase 1 后端设计文档

> 日期：2026-05-02
> 目标：将微信小程序从腾讯云开发迁移到 Docker + Django Ninja + PostgreSQL 自建后端

---

## 技术栈

| 层 | 选型 | 版本 |
|---|------|------|
| 语言 | Python | 3.12+ |
| 框架 | Django + Django Ninja | 5.x + 最新 |
| 数据库 | PostgreSQL | 16-alpine |
| 认证 | PyJWT | 最新 |
| 文件存储 | MinIO（Python SDK） | 最新 |
| Web 服务器 | Gunicorn + Uvicorn worker | 最新 |
| 反向代理 | Nginx | alpine |
| 容器编排 | Docker Compose | v2 |

---

## 一、项目结构（方案 A：按领域拆分 Django App）

```
HouDuan_v1/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py              # NinjaAPI 注册所有路由器
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── auth_app/            # 微信登录
│   │   │   ├── models.py        # User 模型
│   │   │   ├── schemas.py       # Ninja Schema
│   │   │   ├── routers.py
│   │   │   └── services.py      # 微信 code2session
│   │   ├── activity/            # 活动
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routers.py
│   │   ├── theme/               # 主题
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routers.py
│   │   ├── category/            # 分类
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routers.py
│   │   ├── order/               # 订单 + 支付 mock
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   ├── review/              # 评价
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routers.py
│   │   ├── upload/              # MinIO 文件上传
│   │   │   ├── routers.py
│   │   │   └── services.py
│   │   └── config_app/          # 系统配置
│   │       ├── models.py
│   │       ├── schemas.py
│   │       └── routers.py
│   ├── core/
│   │   ├── auth.py              # JWT Bearer 认证 + 鉴权
│   │   ├── pagination.py        # 统一分页
│   │   └── exceptions.py        # 全局异常处理 + 统一响应
│   ├── manage.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── nginx/
│   └── default.conf
└── .env.example                  # 环境变量模板
```

---

## 二、第一阶段模块范围

| 模块 | 接口数 | 路径 | 状态 |
|------|--------|------|------|
| 微信登录 | 1 | POST /api/auth/login | 实现 |
| 活动列表/详情 | 6 | GET /api/activities... | 实现 |
| 主题列表 | 1 | GET /api/themes | 实现 |
| 分类列表 | 1 | GET /api/categories | 实现 |
| 评价列表/提交 | 2 | GET+POST /api/reviews | 实现 |
| 订单 CRUD + 支付 | 5 | /api/orders... | 实现，支付 mock |
| 文件上传 | 3 | /api/upload... | 实现，MinIO |
| 公开配置 | 1 | GET /api/config/public | 实现 |

**暂不实现**：管理员接口（19个）、聊天/客服接口（4个，后续接微信官方客服）

---

## 三、数据库设计（MySQL → PostgreSQL 适配）

### 关键类型映射

| MySQL | PostgreSQL |
|------|-----------|
| BIGINT UNSIGNED AUTO_INCREMENT | BIGSERIAL |
| TINYINT(1) | BOOLEAN |
| DATETIME | TIMESTAMP |
| JSON | JSONB |
| FULLTEXT INDEX | GIN INDEX + tsvector |
| ENGINE=InnoDB | 不需要 |

### 时间字段统一

- 所有表的创建时间：`created_time`（TIMESTAMP, DEFAULT NOW()）
- 所有表的更新时间：`updated_time`（TIMESTAMP, DEFAULT NULL）

### Django ORM 使用 JSONField

所有 JSON 字段使用 `django.db.models.JSONField`，PostgreSQL 自动映射为 JSONB 类型，支持索引和查询。

### Admin 表

管理员功能第一阶段不做，但 `admin_users` 表在 migration 中建好预留。

---

## 四、认证流程

```
小程序                          Django                          微信
  │                               │                              │
  │  1. wx.login() → code        │                              │
  │  2. POST /api/auth/login     │                              │
  │     { code }                  │                              │
  │                               │  3. GET code2session         │
  │                               │  4. { openid, session_key }  │
  │                               │  5. upsert user              │
  │                               │  6. sign JWT                 │
  │  7. { token, user, isNew }   │                              │
  │  8. Authorization: Bearer    │  9. verify → request.auth    │
```

JWT payload: `{ user_id, openid, exp }`，有效期 7 天。

---

## 五、统一响应格式

所有接口返回：

```json
// 成功
{ "success": true, "data": { ... } }

// 失败
{ "success": false, "error": "错误信息" }
```

通过 Django Ninja 全局异常处理器 + Schema 泛型包装实现。

---

## 六、各模块要点

| 模块 | 要点 |
|------|------|
| auth_app | 通过 code 调用微信 code2session，upsert 用户，返回 JWT |
| activity | 支持 category/timeCategory/groupCategory 多条件筛选 + 分页 |
| theme | status='显示'，按 sort 升序，纯读接口 |
| category | 按 type 分组，seed data 通过 migration 写入 |
| order | 支付 mock：创建订单不调微信，paymentParams 返回假数据；callback 手动触发状态更新 |
| review | 提交需登录，order_id+user_id 联合唯一约束 |
| upload | minio-py SDK，multipart/form-data，分类目录存储 |
| config_app | key-value 表，公开接口筛选手动指定的 key |

---

## 七、Docker 架构

```
                    ┌─────────────────────────┐
                    │       Nginx :80          │
                    └───────────┬───────────────┘
                                │ proxy_pass
                    ┌───────────▼───────────────┐
                    │     Django :8000          │
                    │   Gunicorn + Uvicorn      │
                    └─────┬──────────┬──────────┘
                          │          │
                    ┌─────▼────┐ ┌──▼──────────┐
                    │ PG :5432 │ │ MinIO :9000 │
                    │          │ │  :9001(web) │
                    └──────────┘ └─────────────┘
```

### 服务清单

| 服务 | 镜像 | 端口 |
|------|------|------|
| db | postgres:16-alpine | 5432 |
| minio | minio/minio | 9000, 9001(console) |
| backend | 自定义 Dockerfile | 8000 |
| nginx | nginx:alpine | 80 |

### 敏感信息

所有密钥（DB_PASSWORD、MINIO_PASSWORD、WX_APPID、WX_SECRET、JWT_SECRET）通过 `.env` 文件注入，不提交到版本控制。

---

## 八、依赖清单（requirements.txt）

```
django>=5.0,<6.0
django-ninja>=1.0,<2.0
djangorestframework-stubs  # Ninja 不依赖 DRF，仅用于类型参考
psycopg[binary]>=3.0       # PostgreSQL 驱动
dj-database-url>=2.0       # DATABASE_URL 解析
pyjwt>=2.0                 # JWT
minio>=7.0                 # MinIO SDK
django-storages[s3]>=1.0   # Django S3 存储后端
requests>=2.0              # 微信 API 调用
gunicorn>=22.0             # WSGI
uvicorn>=0.30              # ASGI worker
django-cors-headers>=4.0   # CORS
```

---

## 九、测试策略

- 所有 API 端点用 Django TestCase 覆盖
- 支付 mock 返回固定数据用于集成测试
- MinIO 测试使用独立 bucket
- CI 中通过 docker-compose 启动依赖服务

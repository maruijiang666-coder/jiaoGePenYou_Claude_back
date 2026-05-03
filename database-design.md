# 数据库设计文档

> 本文档列出将小程序从腾讯云开发（NoSQL 文档数据库）迁移到 Docker 自建数据库的完整设计。
> 推荐使用 **MySQL** 或 **PostgreSQL**（原 NoSQL 的非结构化字段用 JSON 类型兼容）。

---

## 目录

1. [集合/表概览](#集合概览)
2. [users — 用户表](#1-users--用户表)
3. [activities — 活动表](#2-activities--活动表)
4. [themes — 主题表](#3-themes--主题表)
5. [categories — 分类表](#4-categories--分类表)
6. [orders — 订单表](#5-orders--订单表)
7. [reviews — 评价表](#6-reviews--评价表)
8. [chat_messages — 聊天消息表](#7-chat_messages--聊天消息表)
9. [config — 系统配置表](#8-config--系统配置表)
10. [admin_users — 管理员表（新增）](#9-admin_users--管理员表新增)
11. [种子数据](#种子数据)

---

## 集合概览

| 表名 | 原集合 | 用途 | 记录量估算 |
|------|--------|------|------------|
| users | users | 用户信息 | ~1K-10K |
| activities | activities | 活动信息 | ~100-1K |
| themes | themes | 活动主题 | ~10 |
| categories | categories | 分类数据 | ~20 |
| orders | orders | 订单记录 | ~1K-10K |
| reviews | reviews | 活动评价 | ~1K-10K |
| chat_messages | chat_messages | 聊天消息 | ~10K-100K |
| config | config | 系统配置 | ~10 |
| admin_users | 无(新增) | 后台管理员 | ~5 |

---

## 1. users — 用户表

**原集合**: `users` | **来源**: `userLogin` 云函数

### MySQL DDL

```sql
CREATE TABLE users (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    openid      VARCHAR(64)     NOT NULL COMMENT '微信openid',
    nick_name   VARCHAR(100)    DEFAULT '微信用户' COMMENT '用户昵称',
    avatar_url  VARCHAR(500)    DEFAULT '/images/avatar.png' COMMENT '头像URL',
    phone       VARCHAR(20)     DEFAULT '' COMMENT '手机号',
    points      INT             DEFAULT 0 COMMENT '积分',
    coupons     JSON            DEFAULT NULL COMMENT '优惠券列表',
    last_login_time DATETIME    DEFAULT NULL COMMENT '最后登录时间',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 字段说明

| 字段 | 类型 | 原类型 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id (auto) | 主键 |
| openid | VARCHAR(64) | openid (string) | 微信唯一标识 |
| nick_name | VARCHAR(100) | nickName | 用户昵称 |
| avatar_url | VARCHAR(500) | avatarUrl | 头像图片URL |
| phone | VARCHAR(20) | phone | 手机号 |
| points | INT | points | 用户积分 |
| coupons | JSON | coupons (array) | 优惠券列表 |
| last_login_time | DATETIME | lastLoginTime | 最后登录时间（原 userLogin 云函数更新） |
| create_time | DATETIME | createTime | 注册时间 |
| update_time | DATETIME | — | 更新时间 |

### coupons JSON 结构

```json
[
  {
    "id": "优惠券ID",
    "type": "满减券",
    "amount": 20,
    "minAmount": 200,
    "expireTime": "2025-12-31T23:59:59Z",
    "status": "未使用"
  }
]
```

---

## 2. activities — 活动表

**原集合**: `activities` | **来源**: `adminApi` 云函数 / `initDB` 云函数

### MySQL DDL

```sql
CREATE TABLE activities (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200)    NOT NULL COMMENT '活动标题',
    price           DECIMAL(10,2)   NOT NULL COMMENT '价格（元）',
    images          JSON            DEFAULT NULL COMMENT '封面图片URL数组',
    detail_images   JSON            DEFAULT NULL COMMENT '详情图片URL数组',
    category        VARCHAR(50)     DEFAULT NULL COMMENT '活动分类',
    time_category   VARCHAR(50)     DEFAULT NULL COMMENT '时长分类',
    group_category  VARCHAR(50)     DEFAULT NULL COMMENT '人群分类',
    location        VARCHAR(200)    DEFAULT NULL COMMENT '活动地点',
    duration        VARCHAR(50)     DEFAULT NULL COMMENT '活动时长',
    difficulty      VARCHAR(50)     DEFAULT NULL COMMENT '难度等级',
    min_people      INT             DEFAULT 2 COMMENT '最少成团人数',
    max_people      INT             DEFAULT 20 COMMENT '最多人数',
    club            JSON            DEFAULT NULL COMMENT '俱乐部信息',
    tags            JSON            DEFAULT NULL COMMENT '标签数组',
    detail          TEXT            DEFAULT NULL COMMENT '活动详情（Markdown格式）',
    display_type    VARCHAR(20)     DEFAULT 'small' COMMENT '首页展示类型: small/large',
    is_new          TINYINT(1)      DEFAULT 0 COMMENT '是否新品',
    status          VARCHAR(20)     DEFAULT '上架' COMMENT '状态: 上架/下架',
    rating          DECIMAL(2,1)    DEFAULT 5.0 COMMENT '平均评分',
    rating_count    INT             DEFAULT 0 COMMENT '评价数量',
    sold_count      INT             DEFAULT 0 COMMENT '已售数量',
    theme_id        BIGINT UNSIGNED DEFAULT NULL COMMENT '关联主题ID',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_category (category),
    INDEX idx_time_category (time_category),
    INDEX idx_group_category (group_category),
    INDEX idx_status (status),
    INDEX idx_theme_id (theme_id),
    INDEX idx_sold_count (sold_count),
    FULLTEXT INDEX idx_title_detail (title, detail)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动表';
```

### 字段说明

| 字段 | 类型 | 原字段 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id | 主键 |
| title | VARCHAR(200) | title | 活动标题 |
| price | DECIMAL(10,2) | price (number) | 价格，单位元 |
| images | JSON | images (array) | 封面图片URL数组 |
| detail_images | JSON | detailImages (array) | 详情图URL数组 |
| category | VARCHAR(50) | category | 活动分类（如：户外徒步、民俗体验） |
| time_category | VARCHAR(50) | timeCategory | 时长分类（如：单日活动、多日进阶） |
| group_category | VARCHAR(50) | groupCategory | 人群分类（如：儿童、家庭、情侣闺蜜好友） |
| location | VARCHAR(200) | location | 活动地点 |
| duration | VARCHAR(50) | duration | 活动时长描述 |
| difficulty | VARCHAR(50) | difficulty | 难度（如：无门槛、初级强度、中等强度、高强度） |
| min_people | INT | minPeople | 最少人数 |
| max_people | INT | maxPeople | 最多人数 |
| club | JSON | club (object) | 俱乐部信息 |
| tags | JSON | tags (array) | 标签数组 |
| detail | TEXT | detail (string) | Markdown 格式详情 |
| display_type | VARCHAR(20) | displayType | 首页展示尺寸（small/large） |
| is_new | TINYINT | isNew (bool) | 是否新品 |
| status | VARCHAR(20) | status | 上架/下架 |
| rating | DECIMAL(2,1) | rating | 平均评分 |
| rating_count | INT | ratingCount | 评价总数 |
| sold_count | INT | soldCount | 已售数量（支付成功后 +1） |
| theme_id | BIGINT | themeId | 关联主题ID |
| create_time | DATETIME | createTime | 创建时间 |
| update_time | DATETIME | updateTime | 更新时间 |

### club JSON 结构

```json
{
  "name": "野行户外俱乐部",
  "logo": "/images/logo.png",
  "location": "北京 · 门头沟区"
}
```

### tags JSON 结构

```json
["热门推荐", "户外徒步", "亲子友好"]
```

---

## 3. themes — 主题表

**原集合**: `themes` | **来源**: `adminApi` 云函数 / `initDB` 云函数

### MySQL DDL

```sql
CREATE TABLE themes (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL COMMENT '主题名称',
    cover_image VARCHAR(500)    DEFAULT '' COMMENT '封面图片URL',
    description TEXT            DEFAULT NULL COMMENT '主题描述',
    sort        INT             DEFAULT 0 COMMENT '排序（越小越前）',
    status      VARCHAR(20)     DEFAULT '显示' COMMENT '状态: 显示/隐藏',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_status_sort (status, sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题表';
```

### 字段说明

| 字段 | 类型 | 原字段 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id | 主键 |
| name | VARCHAR(100) | name | 主题名称 |
| cover_image | VARCHAR(500) | coverImage | 封面图URL |
| description | TEXT | description | 主题描述 |
| sort | INT | sort | 排序权重 |
| status | VARCHAR(20) | status | 显示/隐藏 |
| create_time | DATETIME | createTime | 创建时间 |

---

## 4. categories — 分类表

**原集合**: `categories` | **来源**: `initDB` 云函数（种子数据）

### MySQL DDL

```sql
CREATE TABLE categories (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)     NOT NULL COMMENT '分类名称',
    icon        VARCHAR(50)     DEFAULT NULL COMMENT '图标标识',
    type        VARCHAR(20)     NOT NULL COMMENT '分类类型: activity/time/group',
    sort        INT             DEFAULT 0 COMMENT '排序',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_type (type),
    INDEX idx_type_sort (type, sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分类表';
```

### 种子数据

| type | 分类名称 | icon | sort |
|------|---------|------|------|
| activity | 户外徒步 | hiking | 1 |
| activity | 民俗体验 | festival | 2 |
| activity | 手作艺术 | palette | 3 |
| activity | 地道美食 | restaurant | 4 |
| activity | 露营时光 | camping | 5 |
| activity | 亲子研学 | child_care | 6 |
| activity | 艺术沙龙 | theater_comedy | 7 |
| activity | 山野寻踪 | landscape | 8 |
| time | 单日活动 | today | 1 |
| time | 多日进阶 | date_range | 2 |
| group | 儿童 | child_friendly | 1 |
| group | 家庭 | family_restroom | 2 |
| group | 情侣闺蜜好友 | group | 3 |

---

## 5. orders — 订单表

**原集合**: `orders` | **来源**: `wxPay` / `adminApi` 云函数

### MySQL DDL

```sql
CREATE TABLE orders (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    openid          VARCHAR(64)     NOT NULL COMMENT '用户openid（冗余方便查询）',
    activity_id     BIGINT UNSIGNED NOT NULL COMMENT '活动ID',
    quantity        INT             DEFAULT 1 COMMENT '购买数量',
    total_amount    DECIMAL(10,2)   NOT NULL COMMENT '订单金额（元）',
    status          VARCHAR(20)     DEFAULT '待付款' COMMENT '订单状态: 待付款/已付款/已退款/已取消',
    contact_name    VARCHAR(50)     DEFAULT NULL COMMENT '联系人姓名',
    contact_phone   VARCHAR(20)     DEFAULT NULL COMMENT '联系人电话',
    remark          VARCHAR(500)    DEFAULT NULL COMMENT '备注',
    pay_time        DATETIME        DEFAULT NULL COMMENT '支付时间',
    pay_method      VARCHAR(50)     DEFAULT NULL COMMENT '支付方式',
    refund_time     DATETIME        DEFAULT NULL COMMENT '退款时间',
    transaction_id  VARCHAR(64)     DEFAULT NULL COMMENT '微信支付交易号',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_user_id (user_id),
    INDEX idx_openid (openid),
    INDEX idx_activity_id (activity_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
```

### 字段说明

| 字段 | 类型 | 原字段 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id | 主键 |
| user_id | BIGINT | userId | 关联 users.id |
| openid | VARCHAR(64) | — | 冗余存储，方便多条件查询 |
| activity_id | BIGINT | activityId | 关联 activities.id |
| quantity | INT | quantity | 购买数量 |
| total_amount | DECIMAL(10,2) | totalAmount | 订单金额 |
| status | VARCHAR(20) | status | 待付款 / 已付款 / 已退款 |
| contact_name | VARCHAR(50) | contactName | 联系人 |
| contact_phone | VARCHAR(20) | contactPhone | 联系电话 |
| remark | VARCHAR(500) | remark | 备注 |
| pay_time | DATETIME | payTime | 支付完成时间 |
| pay_method | VARCHAR(50) | payMethod | 支付方式 |
| refund_time | DATETIME | — | 退款时间 |
| transaction_id | VARCHAR(64) | — | 微信支付交易号（新增） |
| create_time | DATETIME | createTime | 创建时间 |
| update_time | DATETIME | — | 更新时间 |

### 状态流转

```
待付款 ──支付──▶ 已付款 ──退款──▶ 已退款
  │                           
  └────超时/取消──▶ 已取消
```

---

## 6. reviews — 评价表

**原集合**: `reviews` | **来源**: `adminApi` 云函数 / `pages/reviews`

### MySQL DDL

```sql
CREATE TABLE reviews (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    activity_id BIGINT UNSIGNED NOT NULL COMMENT '活动ID',
    user_id     BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    order_id    BIGINT UNSIGNED DEFAULT NULL COMMENT '关联订单ID',
    rating      TINYINT         NOT NULL COMMENT '评分(1-5)',
    content     TEXT            DEFAULT NULL COMMENT '评价内容',
    images      JSON            DEFAULT NULL COMMENT '评价图片URL数组',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_activity_id (activity_id),
    INDEX idx_user_id (user_id),
    UNIQUE INDEX idx_order_user (order_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评价表';
```

### 字段说明

| 字段 | 类型 | 原字段 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id | 主键 |
| activity_id | BIGINT | activityId | 关联活动 |
| user_id | BIGINT | userId | 评价用户 |
| order_id | BIGINT | — | 关联订单（一个订单只能评价一次） |
| rating | TINYINT | rating | 1-5星评分 |
| content | TEXT | content | 评价内容 |
| images | JSON | images (array) | 评价图片 |
| create_time | DATETIME | createTime | 评价时间 |

---

## 7. chat_messages — 聊天消息表

**原集合**: `chat_messages` | **来源**: `adminApi` 云函数 / `pages/kefu`

### MySQL DDL

```sql
CREATE TABLE chat_messages (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(64)     NOT NULL COMMENT '会话ID（用户openid）',
    from_user_id VARCHAR(64)    NOT NULL COMMENT '发送者ID',
    to_user_id  VARCHAR(64)     NOT NULL COMMENT '接收者ID',
    content     TEXT            NOT NULL COMMENT '消息内容',
    type        VARCHAR(20)     DEFAULT 'text' COMMENT '消息类型: text/image',
    is_read     TINYINT(1)      DEFAULT 0 COMMENT '是否已读',
    create_time DATETIME        NOT NULL COMMENT '消息时间（精确到毫秒用于排序）',

    INDEX idx_session_time (session_id, create_time),
    INDEX idx_from_user (from_user_id),
    INDEX idx_to_user (to_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';
```

### 字段说明

| 字段 | 类型 | 原字段 | 说明 |
|------|------|--------|------|
| id | BIGINT | _id | 主键 |
| session_id | VARCHAR(64) | sessionId | 会话ID（等于用户的 openid） |
| from_user_id | VARCHAR(64) | fromUserId | 发送者（用户 openid 或 'admin'） |
| to_user_id | VARCHAR(64) | toUserId | 接收者（'admin' 或 用户 openid） |
| content | TEXT | content | 消息内容 |
| type | VARCHAR(20) | type | 消息类型（text/image） |
| is_read | TINYINT | isRead (bool) | 管理员是否已读 |
| create_time | DATETIME | createTime (Date) | 消息时间 |

> **注意**: 原项目使用 `sessionId` 作为 `_openid` 字段实现权限控制。迁移后由服务端根据 JWT 中的用户信息进行权限校验。

---

## 8. config — 系统配置表

**原集合**: `config` | **来源**: `adminApi` 云函数 / `initDB` 云函数

### MySQL DDL

```sql
CREATE TABLE config (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `key`       VARCHAR(50)     NOT NULL COMMENT '配置键',
    `value`     TEXT            DEFAULT NULL COMMENT '配置值（支持 JSON）',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE INDEX idx_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
```

### 种子数据

| key | value | 说明 |
|-----|-------|------|
| statsEnabled | `true` | 是否启用统计 |
| appVersion | `1.0.0` | 应用版本号 |
| contactPhone | `400-123-4567` | 联系电话 |
| serviceTime | `9:00-18:00` | 客服时间 |

---

## 9. admin_users — 管理员表（新增）

原项目没有管理员表，admin panel 使用 CloudBase 内置认证。迁移后需要自建。

### MySQL DDL

```sql
CREATE TABLE admin_users (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)     NOT NULL COMMENT '用户名',
    password    VARCHAR(255)    NOT NULL COMMENT '密码哈希（bcrypt）',
    role        VARCHAR(20)     DEFAULT 'admin' COMMENT '角色: admin/superadmin',
    status      TINYINT(1)      DEFAULT 1 COMMENT '状态: 1启用 0禁用',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    UNIQUE INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';
```

---

## 10. 文件存储方案

原项目使用腾讯云存储（`cloud://` 格式的 fileID）。迁移后建议：

### 方案一：本地存储 + Nginx（推荐简单部署）

```
/uploads/
  activities/     # 活动图片
  avatars/        # 用户头像
  themes/         # 主题封面
  reviews/        # 评价图片
  chat/           # 聊天图片
```

文件通过 Nginx 直接提供静态文件访问：`http://<host>/uploads/activities/xxx.jpg`

### 方案二：MinIO / OSS 对象存储（推荐生产环境）

使用 MinIO（Docker 部署）或阿里云 OSS / AWS S3 存储文件，通过 SDK 上传获取 URL。

---

## 11. ER 关系图

```
┌──────────────┐       ┌──────────────────┐
│  admin_users │       │     config       │
│  (新增)      │       │  (key-value)     │
└──────────────┘       └──────────────────┘

┌──────────────┐       ┌──────────────────┐
│    users     │       │    categories    │
│  用户表      │       │    分类表        │
└──────┬───────┘       └──────────────────┘
       │
       │ openid (session_id)
       │
┌──────┴──────────────────────────────────┐
│              chat_messages              │
│              聊天消息                    │
└─────────────────────────────────────────┘

┌──────────────┐       ┌──────────────────┐
│   themes     │       │   activities     │
│   主题表     │◄──────│   活动表         │
└──────────────┘theme_id└────────┬─────────┘
                                 │
                                 │ activity_id
                                 │
                      ┌──────────┴─────────┐
                      │      orders        │
                      │      订单表        │
                      └──────────┬─────────┘
                                 │
                                 │ user_id
                                 │
                      ┌──────────┴─────────┐
               ┌──────┤      users         │
               │      └────────────────────┘
               │
               │ activity_id
               │
      ┌────────┴──────────┐
      │     reviews       │
      │     评价表        │
      └────────┬──────────┘
               │
               │ user_id
               │
      ┌────────┴──────────┐
      │      users        │
      └───────────────────┘
```

---

## 12. 迁移注意事项

### 12.1 数据迁移

1. 从腾讯云开发导出原 NoSQL 数据（使用 `wx.cloud.database().collection().get()` 遍历导出）
2. 将数据转换后导入 MySQL（注意 `_id` → `id` 的映射和 JSON 字段的序列化）
3. 原 `_openid` 权限控制字段在 MySQL 中移除，由应用层 JWT 鉴权替代

### 12.2 前端改动

| 原写法 | 迁移后写法 | 说明 |
|--------|-----------|------|
| `wx.cloud.database().collection('xxx')` | `wx.request({ url: '/api/xxx' })` | 所有数据库直读改为 API 调用 |
| `wx.cloud.callFunction({ name: 'userLogin' })` | `wx.request({ url: '/api/auth/login' })` | 登录改为 API |
| `wx.cloud.callFunction({ name: 'wxPay' })` | `wx.request({ url: '/api/orders' })` | 支付改为 API |
| `db.collection('chat_messages').watch()` | `wx.connectSocket({ url: 'ws://...' })` | 聊天改为 WebSocket |
| `cloud://` 文件ID | `http://host/uploads/...` | 文件访问改为 HTTP URL |
| `wx.cloud.uploadFile()` | `wx.uploadFile({ url: '/api/upload' })` | 文件上传改为 HTTP |

### 12.3 微信能力保留

以下微信能力不受迁移影响（仍通过微信原生 API 调用）：
- `wx.login()` — 获取临时 code
- `wx.getUserInfo()` — 获取用户信息
- `wx.requestPayment()` — 调起微信支付
- `wx.chooseImage()` — 选择图片

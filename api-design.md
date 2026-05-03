# API 接口设计文档

> 本文档列出将小程序从腾讯云开发迁移到 Docker 自建后端所需的所有 API 接口。
> 原项目通过 `wx.cloud.callFunction()` 和 `wx.cloud.database()` 直接操作数据库，迁移后需改为 RESTful API。

---

## 基础约定

- **Base URL**: `http://<host>:<port>/api`
- **认证方式**: JWT（Header: `Authorization: Bearer <token>`）
- **Content-Type**: `application/json`
- **响应格式**:
  ```json
  { "success": true, "data": {} }
  // 或
  { "success": false, "error": "错误信息" }
  ```

---

## 一、认证接口

### 1.1 微信小程序登录（替代 `userLogin` 云函数）

原逻辑：`app.js` 调用 `wx.cloud.callFunction({ name: 'userLogin' })` 获取 openid 并创建/更新用户。

**接口**: `POST /api/auth/login`

**请求**:
```json
{
  "code": "wx.login() 返回的临时 code"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "jwt-token-string",
    "user": {
      "id": "用户ID",
      "openid": "微信openid",
      "nickName": "微信用户",
      "avatarUrl": "/images/avatar.png",
      "phone": "",
      "points": 0,
      "coupons": [],
      "createTime": "2025-01-01T00:00:00Z"
    },
    "isNew": false
  }
}
```

**后端实现要点**:
- 通过 `code` 调用微信 `jscode2session` 接口换取 `openid` 和 `session_key`
- 在 `users` 表中查找 `openid`，不存在则创建新用户
- 存在则更新 `lastLoginTime`
- 生成 JWT token 返回给前端（前端存 `wx.setStorageSync('token', token)`）

> **前端改动**: `app.js` 的 `login()` 方法需从 `wx.cloud.callFunction` 改为 `wx.request` 调用本接口。

---

## 二、活动接口（替代 `activities` 集合直读）

### 2.1 首页活动列表

**原调用**: `pages/home/index.js` → `db.collection('activities').where({ status: '上架' }).limit(20).get()`

**接口**: `GET /api/activities?status=上架&limit=20`

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态过滤，默认 `上架` |
| limit | number | 否 | 返回数量，默认 20 |
| page | number | 否 | 页码，默认 1 |

**响应**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "_id": "活动ID",
        "title": "活动标题",
        "price": 298,
        "images": ["封面图URL数组"],
        "category": "户外徒步",
        "timeCategory": "单日活动",
        "groupCategory": "情侣闺蜜好友",
        "location": "浙江 · 临安",
        "duration": "8 小时",
        "difficulty": "中等强度",
        "minPeople": 4,
        "maxPeople": 12,
        "club": {
          "name": "俱乐部名称",
          "logo": "logo图片URL",
          "location": "俱乐部地址"
        },
        "tags": ["热门推荐", "户外徒步"],
        "displayType": "large",
        "isNew": false,
        "rating": 4.9,
        "ratingCount": 128,
        "soldCount": 356,
        "themeId": "主题ID"
      }
    ],
    "total": 100
  }
}
```

### 2.2 活动详情

**原调用**: `pages/active-detail/index.js` → `db.collection('activities').doc(id).get()`

**接口**: `GET /api/activities/:id`

**响应**:
```json
{
  "success": true,
  "data": {
    "_id": "活动ID",
    "title": "活动标题",
    "price": 298,
    "images": ["图片URL数组"],
    "detailImages": ["详情图片URL数组"],
    "category": "户外徒步",
    "timeCategory": "单日活动",
    "groupCategory": "情侣闺蜜好友",
    "location": "浙江 · 临安",
    "duration": "8 小时",
    "difficulty": "中等强度",
    "minPeople": 4,
    "maxPeople": 12,
    "club": {
      "name": "俱乐部名称",
      "logo": "logoURL",
      "location": "俱乐部地址"
    },
    "tags": ["标签数组"],
    "detail": "活动详细介绍（Markdown格式）",
    "displayType": "large",
    "isNew": false,
    "rating": 4.9,
    "ratingCount": 128,
    "soldCount": 356,
    "themeId": "主题ID",
    "status": "上架",
    "createTime": "2025-01-01T00:00:00Z",
    "updateTime": "2025-01-01T00:00:00Z"
  }
}
```

### 2.3 按分类筛选活动

**原调用**: `pages/activity-category/index.js` → `db.collection('activities').where({ status:'上架', category: catName }).limit(20).get()`

**接口**: `GET /api/activities?category=户外徒步&status=上架&limit=20`

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 是 | 活动分类名 |
| status | string | 否 | 默认 `上架` |
| page | number | 否 | 分页 |

### 2.4 按时长类型筛选

**原调用**: `pages/time-category/index.js` → `db.collection('activities').where({ status:'上架', timeCategory: val }).limit(10).get()`

**接口**: `GET /api/activities?timeCategory=单日活动&status=上架&limit=10`

### 2.5 按人群类型筛选

**原调用**: `pages/group-category/index.js` → `db.collection('activities').where({ status:'上架', groupCategory: val }).limit(10).get()`

**接口**: `GET /api/activities?groupCategory=家庭&status=上架&limit=10`

### 2.6 购物车页活动列表

**原调用**: `pages/shopping/index.js` → `db.collection('activities').where({ status:'上架' }).limit(10).get()`

**接口**: `GET /api/activities?status=上架&limit=10`

### 2.7 活动列表页

**原调用**: `pages/activity-list/index.js` → `db.collection('activities').where({ status:'上架' }).limit(20).get()`

**接口**: `GET /api/activities?status=上架&limit=20`

---

## 三、主题接口（替代 `themes` 集合直读）

### 3.1 首页主题列表

**原调用**: `pages/home/index.js` → `db.collection('themes').where({ status:'显示' }).orderBy('sort','asc').get()`

**接口**: `GET /api/themes`

**响应**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "_id": "主题ID",
        "name": "春天单日户外",
        "coverImage": "封面图URL",
        "description": "春日限定，一天时间感受自然的气息",
        "sort": 1,
        "status": "显示"
      }
    ]
  }
}
```

---

## 四、订单接口

### 4.1 订单详情

**原调用**: `pages/order-detail/index.js` → `db.collection('orders').doc(id).get()`

**接口**: `GET /api/orders/:id`

**说明**: 需要验证当前用户只能查看自己的订单。

### 4.2 创建订单 / 发起支付（替代 `wxPay` 云函数 `pay` action）

**原调用**: `cloudfunctions/wxPay/index.js` → `action='pay'`

**接口**: `POST /api/orders`

**请求**:
```json
{
  "activityId": "活动ID",
  "quantity": 1,
  "totalAmount": 298,
  "contactName": "联系人",
  "contactPhone": "13800138000",
  "remark": "备注"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "orderId": "订单ID",
    "paymentParams": {
      // 微信支付参数（如 timeStamp、nonceStr、package、signType、paySign）
    }
  }
}
```

**后端实现要点**:
- 创建订单记录（status = `待付款`）
- 调用微信支付统一下单接口
- 返回支付参数给前端调起微信支付
- 支付成功后通过回调更新订单状态为 `已付款`，并递增活动的 `soldCount`

### 4.3 支付回调

**接口**: `POST /api/orders/pay-callback`（微信支付结果通知回调）

**后端实现**:
- 验证微信支付签名
- 更新订单 `status` 为 `已付款`，记录 `payTime` 和 `payMethod`
- 递增活动 `soldCount`

### 4.4 退款（替代 `wxPay` 云函数 `refund` action）

**原调用**: `cloudfunctions/wxPay/index.js` → `action='refund'`

**接口**: `POST /api/orders/:id/refund`

**后端实现**:
- 验证订单状态为 `已付款`
- 调用微信支付退款接口
- 更新订单状态为 `已退款`

### 4.5 我的订单列表

**接口**: `GET /api/orders?status=已付款&page=1&pageSize=20`

**说明**: 根据当前登录用户过滤。

---

## 五、评价接口（替代 `reviews` 集合直读）

### 5.1 活动评价列表

**原调用**: `pages/reviews/index.js` → `db.collection('reviews').where({ activityId }).limit(20).get()`

**接口**: `GET /api/reviews?activityId=xxx&page=1&pageSize=20`

**响应**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "_id": "评价ID",
        "activityId": "活动ID",
        "userId": "用户ID",
        "userName": "用户昵称",
        "avatarUrl": "头像URL",
        "rating": 5,
        "content": "评价内容",
        "images": ["评价图片URL数组"],
        "createTime": "2025-01-01T00:00:00Z"
      }
    ],
    "total": 50
  }
}
```

### 5.2 提交评价

**接口**: `POST /api/reviews`

**请求**:
```json
{
  "activityId": "活动ID",
  "rating": 5,
  "content": "评价内容",
  "images": ["图片URL数组"]
}
```

---

## 六、聊天客服接口（替代 `chat_messages` 集合直读/直写）

### 6.1 获取聊天消息

**原调用**: `pages/kefu/index.js` → `db.collection('chat_messages').where({ sessionId }).watch()`（实时监听）

**接口**: `GET /api/chat/messages?sessionId=xxx`

**响应**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "_id": "消息ID",
        "sessionId": "会话ID（即用户openid）",
        "fromUserId": "发送者ID",
        "toUserId": "接收者ID",
        "content": "消息内容",
        "type": "text",
        "isRead": false,
        "createTime": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

> **重要**: 原项目使用 `db.collection(...).watch()` 实现实时聊天。迁移后需用 **WebSocket** 替代轮询实现实时消息推送。

### 6.2 WebSocket 实时通信

**连接**: `ws://<host>:<port>/ws/chat?token=<jwt>`

**发送消息** (客户端 → 服务端):
```json
{
  "type": "message",
  "data": {
    "content": "消息内容",
    "msgType": "text"
  }
}
```

**接收消息** (服务端 → 客户端):
```json
{
  "type": "message",
  "data": {
    "_id": "消息ID",
    "sessionId": "会话ID",
    "fromUserId": "admin",
    "toUserId": "用户openid",
    "content": "消息内容",
    "type": "text",
    "isRead": true,
    "createTime": "2025-01-01T00:00:00Z"
  }
}
```

### 6.3 发送消息（HTTP 备选方案）

**接口**: `POST /api/chat/messages`

**请求**:
```json
{
  "content": "消息内容",
  "type": "text"
}
```

> sessionId 由服务端根据当前登录用户的 openid 自动生成。

---

## 七、文件上传接口（替代云存储上传）

### 7.1 上传文件

**原调用**: `admin/js/api.js` → `tcbApp.uploadFile({ cloudPath, filePath })`

**接口**: `POST /api/upload`

**请求**: `multipart/form-data`
- `file`: 文件
- `category`: 上传分类（如 `activities`、`avatars`）

**响应**:
```json
{
  "success": true,
  "data": {
    "fileId": "文件ID",
    "url": "文件访问URL"
  }
}
```

### 7.2 批量上传

**接口**: `POST /api/upload/batch`

**请求**: `multipart/form-data`（多文件）

### 7.3 删除文件

**接口**: `DELETE /api/upload/:fileId`

---

## 八、管理员接口（替代 `adminApi` 云函数）

> 以下接口需要管理员权限（admin role），通过 JWT 中的角色字段判断。

### 8.1 仪表盘

**原调用**: `adminApi` → `action=dashboard`

**接口**: `GET /api/admin/dashboard`

**响应**:
```json
{
  "success": true,
  "data": {
    "stats": {
      "activityCount": 20,
      "orderCount": 150,
      "paidOrderCount": 120,
      "userCount": 500,
      "reviewCount": 80,
      "themeCount": 5,
      "totalRevenue": 50000
    }
  }
}
```

### 8.2 活动管理（CRUD）

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listActivities | 活动列表 | GET | `/api/admin/activities?page=&pageSize=&category=&status=` |
| getActivity | 活动详情 | GET | `/api/admin/activities/:id` |
| createActivity | 创建活动 | POST | `/api/admin/activities` |
| updateActivity | 更新活动 | PUT | `/api/admin/activities/:id` |
| deleteActivity | 删除活动 | DELETE | `/api/admin/activities/:id` |
| deleteImage | 删除图片 | DELETE | `/api/admin/activities/:id/images?imageType=cover&fileID=xxx` |

### 8.3 主题管理（CRUD）

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listThemes | 主题列表 | GET | `/api/admin/themes` |
| createTheme | 创建主题 | POST | `/api/admin/themes` |
| updateTheme | 更新主题 | PUT | `/api/admin/themes/:id` |
| deleteTheme | 删除主题 | DELETE | `/api/admin/themes/:id` |

### 8.4 订单管理

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listOrders | 订单列表 | GET | `/api/admin/orders?page=&pageSize=&status=` |
| updateOrderStatus | 更新订单状态 | PUT | `/api/admin/orders/:id/status` |

### 8.5 评价管理

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listReviews | 评价列表 | GET | `/api/admin/reviews?page=&pageSize=&activityId=` |
| deleteReview | 删除评价 | DELETE | `/api/admin/reviews/:id` |

### 8.6 聊天管理

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listChatSessions | 会话列表 | GET | `/api/admin/chat/sessions` |
| getChatMessages | 消息列表 | GET | `/api/admin/chat/sessions/:sessionId/messages` |
| sendAdminMessage | 发送消息 | POST | `/api/admin/chat/messages` |

### 8.7 配置管理

| 原 action | 新接口 | 方法 | 路径 |
|-----------|--------|------|------|
| listConfig | 配置列表 | GET | `/api/admin/config` |
| getConfig | 获取配置 | GET | `/api/admin/config/:key` |
| updateConfig | 更新配置 | PUT | `/api/admin/config/:key` |

### 8.8 管理员登录

**接口**: `POST /api/admin/auth/login`

**请求**:
```json
{
  "username": "admin",
  "password": "password"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "token": "jwt-admin-token"
  }
}
```

---

## 九、分类数据接口

### 9.1 获取分类列表

**原数据来源**: `initDB` 云函数预置到 `categories` 集合

**接口**: `GET /api/categories`

**响应**:
```json
{
  "success": true,
  "data": {
    "list": [
      { "_id": "xxx", "name": "户外徒步", "icon": "hiking", "type": "activity", "sort": 1 },
      { "_id": "xxx", "name": "单日活动", "icon": "today", "type": "time", "sort": 1 },
      { "_id": "xxx", "name": "家庭", "icon": "family_restroom", "type": "group", "sort": 1 }
    ]
  }
}
```

---

## 十、系统配置接口

### 10.1 获取公开配置

**接口**: `GET /api/config/public`

用于小程序端获取联系方式、服务时间等公开信息。

**响应**:
```json
{
  "success": true,
  "data": {
    "contactPhone": "400-123-4567",
    "serviceTime": "9:00-18:00",
    "appVersion": "1.0.0"
  }
}
```

---

## 接口汇总表

| 序号 | 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|------|
| 1 | POST | `/api/auth/login` | 微信登录 | 否 |
| 2 | GET | `/api/activities` | 活动列表（支持多条件筛选） | 否 |
| 3 | GET | `/api/activities/:id` | 活动详情 | 否 |
| 4 | GET | `/api/themes` | 主题列表 | 否 |
| 5 | GET | `/api/categories` | 分类列表 | 否 |
| 6 | GET | `/api/config/public` | 公开配置 | 否 |
| 7 | GET | `/api/reviews` | 评价列表 | 否 |
| 8 | POST | `/api/reviews` | 提交评价 | 是 |
| 9 | GET | `/api/orders` | 我的订单列表 | 是 |
| 10 | GET | `/api/orders/:id` | 订单详情 | 是 |
| 11 | POST | `/api/orders` | 创建订单 | 是 |
| 12 | POST | `/api/orders/pay-callback` | 支付回调 | 否(微信签名) |
| 13 | POST | `/api/orders/:id/refund` | 退款 | 是 |
| 14 | GET | `/api/chat/messages` | 获取聊天消息 | 是 |
| 15 | POST | `/api/chat/messages` | 发送消息 | 是 |
| 16 | WS | `/ws/chat` | 实时聊天 | 是 |
| 17 | POST | `/api/upload` | 文件上传 | 是 |
| 18 | POST | `/api/upload/batch` | 批量上传 | 是 |
| 19 | DELETE | `/api/upload/:fileId` | 删除文件 | 是 |
| 20 | POST | `/api/admin/auth/login` | 管理员登录 | 否 |
| 21 | GET | `/api/admin/dashboard` | 仪表盘统计 | 管理员 |
| 22 | GET | `/api/admin/activities` | 活动管理列表 | 管理员 |
| 23 | GET | `/api/admin/activities/:id` | 活动详情（管理） | 管理员 |
| 24 | POST | `/api/admin/activities` | 创建活动 | 管理员 |
| 25 | PUT | `/api/admin/activities/:id` | 更新活动 | 管理员 |
| 26 | DELETE | `/api/admin/activities/:id` | 删除活动 | 管理员 |
| 27 | DELETE | `/api/admin/activities/:id/images` | 删除活动图片 | 管理员 |
| 28 | GET | `/api/admin/themes` | 主题管理列表 | 管理员 |
| 29 | POST | `/api/admin/themes` | 创建主题 | 管理员 |
| 30 | PUT | `/api/admin/themes/:id` | 更新主题 | 管理员 |
| 31 | DELETE | `/api/admin/themes/:id` | 删除主题 | 管理员 |
| 32 | GET | `/api/admin/orders` | 订单管理列表 | 管理员 |
| 33 | PUT | `/api/admin/orders/:id/status` | 更新订单状态 | 管理员 |
| 34 | GET | `/api/admin/reviews` | 评价管理列表 | 管理员 |
| 35 | DELETE | `/api/admin/reviews/:id` | 删除评价 | 管理员 |
| 36 | GET | `/api/admin/chat/sessions` | 聊天会话列表 | 管理员 |
| 37 | GET | `/api/admin/chat/sessions/:id/messages` | 会话消息列表 | 管理员 |
| 38 | POST | `/api/admin/chat/messages` | 管理员发送消息 | 管理员 |
| 39 | GET | `/api/admin/config` | 配置列表 | 管理员 |
| 40 | GET | `/api/admin/config/:key` | 获取配置详情 | 管理员 |
| 41 | PUT | `/api/admin/config/:key` | 更新配置 | 管理员 |

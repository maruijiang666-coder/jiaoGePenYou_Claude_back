from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from ninja import NinjaAPI

api = NinjaAPI(
    title="交个朋友 API",
    version="1.0.0",
    docs_url=None,  # disabled built-in, use custom Swagger below
)

# Global exception handler
from core.exceptions import register_exception_handlers
register_exception_handlers(api)

# Public routes
from apps.auth_app.routers import router as auth_router
from apps.activity.routers import router as activity_router
from apps.theme.routers import router as theme_router
from apps.category.routers import router as category_router
from apps.config_app.routers import router as config_router

api.add_router("/auth", auth_router, tags=["认证"])
api.add_router("/activities", activity_router, tags=["活动"])
api.add_router("/themes", theme_router, tags=["主题"])
api.add_router("/categories", category_router, tags=["分类"])
api.add_router("/config", config_router, tags=["配置"])

# Auth-protected routes
from apps.order.routers import router as order_router
from apps.review.routers import router as review_router
from apps.upload.routers import router as upload_router

api.add_router("/orders", order_router, tags=["订单"])
api.add_router("/reviews", review_router, tags=["评价"])
api.add_router("/upload", upload_router, tags=["上传"])


def swagger_ui(request):
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>交个朋友 API 文档</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        html { box-sizing: border-box; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin: 0; background: #fafafa; }
        .topbar { display: none; }
    </style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
<script>
    SwaggerUIBundle({
        url: "/api/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        defaultModelsExpandDepth: -1,
    });
</script>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def docs_redirect(request):
    return redirect("/api/docs/")


urlpatterns = [
    path("api/docs", docs_redirect),
    path("api/docs/", swagger_ui),
    path("api/", api.urls),
]

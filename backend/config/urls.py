from django.urls import path
from django.shortcuts import redirect
from ninja import NinjaAPI

api = NinjaAPI(
    title="交个朋友 API",
    version="1.0.0",
    docs_url="/api/docs",
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


def docs_redirect(request):
    return redirect("/api/docs/")


urlpatterns = [
    path("api/docs", docs_redirect),
    path("api/", api.urls),
]

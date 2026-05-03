from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(
    title="交个朋友 API",
    version="1.0.0",
    docs_url="/api/docs",
)

# Routers will be added in later tasks:
# from apps.auth_app.routers import router as auth_router
# api.add_router("/auth", auth_router, tags=["认证"])
# ...

urlpatterns = [
    path("api/", api.urls),
]

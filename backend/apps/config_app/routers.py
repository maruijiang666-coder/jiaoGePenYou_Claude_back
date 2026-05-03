from ninja import Router
from .models import Config

router = Router()

PUBLIC_KEYS = ["contactPhone", "serviceTime", "appVersion"]


@router.get("/public", response=dict, summary="公开配置", description="获取公开的系统配置（联系电话、服务时间、版本号）")
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

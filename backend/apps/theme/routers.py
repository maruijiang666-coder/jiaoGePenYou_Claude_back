from ninja import Router
from .models import Theme

router = Router()


@router.get("", response=dict, summary="主题列表", description="获取所有显示中的主题，按排序值升序排列")
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

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

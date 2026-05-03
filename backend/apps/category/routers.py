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

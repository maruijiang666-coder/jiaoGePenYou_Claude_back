from ninja import Router, Query
from core.pagination import PaginationParams
from .models import Activity
from .schemas import ActivityBrief, ActivityDetail

router = Router()


def activity_to_brief(a: Activity) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "price": float(a.price),
        "images": a.images or [],
        "category": a.category,
        "time_category": a.time_category,
        "group_category": a.group_category,
        "location": a.location,
        "duration": a.duration,
        "difficulty": a.difficulty,
        "min_people": a.min_people,
        "max_people": a.max_people,
        "club": a.club or {},
        "tags": a.tags or [],
        "display_type": a.display_type,
        "is_new": a.is_new,
        "rating": float(a.rating),
        "rating_count": a.rating_count,
        "sold_count": a.sold_count,
        "theme_id": a.theme_id,
    }


def activity_to_detail(a: Activity) -> dict:
    base = activity_to_brief(a)
    base.update({
        "detail_images": a.detail_images or [],
        "detail": a.detail,
        "status": a.status,
        "created_time": a.created_time.isoformat() if a.created_time else None,
        "updated_time": a.updated_time.isoformat() if a.updated_time else None,
    })
    return base


@router.get("", response=dict, summary="活动列表", description="按状态和分类筛选活动列表，支持分页")
def list_activities(
    request,
    pagination: PaginationParams = Query(...),
    status: str = "上架",
    category: str | None = None,
    time_category: str | None = None,
    group_category: str | None = None,
):
    qs = Activity.objects.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if time_category:
        qs = qs.filter(time_category=time_category)
    if group_category:
        qs = qs.filter(group_category=group_category)

    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    activities = qs.order_by("-created_time")[offset:offset + pagination.page_size]

    return {
        "success": True,
        "data": {
            "list": [activity_to_brief(a) for a in activities],
            "total": total,
        },
    }


@router.get("/{activity_id}", response=dict, summary="活动详情", description="根据活动ID获取活动详细信息")
def get_activity(request, activity_id: int):
    try:
        a = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return {"success": False, "error": "活动不存在"}
    return {"success": True, "data": activity_to_detail(a)}

from ninja import Router, Query
from django.db import IntegrityError
from core.auth import BearerAuth
from core.pagination import PaginationParams
from .models import Review
from .schemas import CreateReviewRequest

router = Router()


@router.get("", response=dict, summary="评价列表", description="根据活动ID获取评价列表，支持分页")
def list_reviews(request, activity_id: int, pagination: PaginationParams = Query(...)):
    qs = Review.objects.filter(activity_id=activity_id).order_by("-created_time")
    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    reviews = qs[offset:offset + pagination.page_size]

    return {
        "success": True,
        "data": {
            "list": [
                {
                    "id": r.id, "activity_id": r.activity_id, "user_id": r.user_id,
                    "user_name": r.user.nick_name, "avatar_url": r.user.avatar_url,
                    "rating": r.rating, "content": r.content,
                    "images": r.images or [],
                    "created_time": r.created_time.isoformat() if r.created_time else None,
                }
                for r in reviews
            ],
            "total": total,
        },
    }


@router.post("", response=dict, auth=BearerAuth(), summary="提交评价", description="对活动提交评价，一个订单仅可评价一次")
def create_review(request, body: CreateReviewRequest):
    payload = request.auth
    try:
        review = Review.objects.create(
            activity_id=body.activity_id,
            user_id=payload["user_id"],
            order_id=body.order_id,
            rating=body.rating,
            content=body.content,
            images=body.images,
        )
    except IntegrityError:
        return {"success": False, "error": "该订单已评价"}

    return {
        "success": True,
        "data": {
            "id": review.id, "activity_id": review.activity_id,
            "user_id": review.user_id, "rating": review.rating,
            "content": review.content, "images": review.images or [],
            "created_time": review.created_time.isoformat(),
        },
    }

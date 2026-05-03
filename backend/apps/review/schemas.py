from ninja import Schema
from datetime import datetime


class CreateReviewRequest(Schema):
    activity_id: int
    rating: int
    content: str = ""
    images: list = []
    order_id: int | None = None


class ReviewOut(Schema):
    id: int
    activity_id: int
    user_id: int
    user_name: str = ""
    avatar_url: str = ""
    rating: int
    content: str = ""
    images: list = []
    created_time: datetime | None = None

from ninja import Schema, Field
from datetime import datetime


class CreateReviewRequest(Schema):
    activity_id: int = Field(..., description="活动ID")
    rating: int = Field(..., description="评分（1-5）")
    content: str = Field(default="", description="评价内容")
    images: list = Field(default=[], description="评价图片列表")
    order_id: int | None = Field(default=None, description="关联订单ID")


class ReviewOut(Schema):
    id: int = Field(..., description="评价ID")
    activity_id: int = Field(..., description="活动ID")
    user_id: int = Field(..., description="用户ID")
    user_name: str = Field(default="", description="用户名")
    avatar_url: str = Field(default="", description="头像URL")
    rating: int = Field(..., description="评分（1-5）")
    content: str = Field(default="", description="评价内容")
    images: list = Field(default=[], description="评价图片列表")
    created_time: datetime | None = Field(default=None, description="评价时间")

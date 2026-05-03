from ninja import Schema, Field
from datetime import datetime


class ClubSchema(Schema):
    name: str = Field(default="", description="俱乐部名称")
    logo: str = Field(default="", description="俱乐部Logo")
    location: str = Field(default="", description="俱乐部地址")


class ActivityBrief(Schema):
    id: int = Field(..., description="活动ID")
    title: str = Field(..., description="活动标题")
    price: float = Field(..., description="价格")
    images: list = Field(default=[], description="封面图片列表")
    category: str = Field(default="", description="活动分类")
    time_category: str = Field(default="", description="时间分类（上午/下午/晚上/全天）")
    group_category: str = Field(default="", description="组队分类（单人/双人/多人）")
    location: str = Field(default="", description="活动地点")
    duration: str = Field(default="", description="时长")
    difficulty: str = Field(default="", description="难度")
    min_people: int = Field(default=2, description="最少人数")
    max_people: int = Field(default=20, description="最多人数")
    club: ClubSchema | None = Field(default=None, description="所属俱乐部")
    tags: list = Field(default=[], description="标签列表")
    display_type: str = Field(default="small", description="展示类型（small/large）")
    is_new: bool = Field(default=False, description="是否新品")
    rating: float = Field(default=5.0, description="评分")
    rating_count: int = Field(default=0, description="评价数量")
    sold_count: int = Field(default=0, description="已售数量")
    theme_id: int | None = Field(default=None, description="所属主题ID")


class ActivityDetail(ActivityBrief):
    detail_images: list = Field(default=[], description="详情图片列表")
    detail: str = Field(default="", description="详情描述（HTML）")
    status: str = Field(default="", description="状态（上架/下架）")
    created_time: datetime | None = Field(default=None, description="创建时间")
    updated_time: datetime | None = Field(default=None, description="更新时间")

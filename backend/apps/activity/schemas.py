from ninja import Schema
from datetime import datetime


class ClubSchema(Schema):
    name: str = ""
    logo: str = ""
    location: str = ""


class ActivityBrief(Schema):
    id: int
    title: str
    price: float
    images: list = []
    category: str = ""
    time_category: str = ""
    group_category: str = ""
    location: str = ""
    duration: str = ""
    difficulty: str = ""
    min_people: int = 2
    max_people: int = 20
    club: ClubSchema | None = None
    tags: list = []
    display_type: str = "small"
    is_new: bool = False
    rating: float = 5.0
    rating_count: int = 0
    sold_count: int = 0
    theme_id: int | None = None


class ActivityDetail(ActivityBrief):
    detail_images: list = []
    detail: str = ""
    status: str = ""
    created_time: datetime | None = None
    updated_time: datetime | None = None

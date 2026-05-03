from ninja import Schema
from datetime import datetime


class LoginRequest(Schema):
    code: str


class UserOut(Schema):
    id: int
    openid: str
    nick_name: str
    avatar_url: str
    phone: str
    points: int
    coupons: list = []
    created_time: datetime


class LoginResponse(Schema):
    token: str
    user: UserOut
    is_new: bool = False

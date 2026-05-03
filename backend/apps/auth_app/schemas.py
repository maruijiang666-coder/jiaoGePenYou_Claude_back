from ninja import Schema, Field
from datetime import datetime


class LoginRequest(Schema):
    code: str = Field(..., description="微信登录凭证 wx.login() 返回的 code")


class UserOut(Schema):
    id: int = Field(..., description="用户ID")
    openid: str = Field(..., description="微信 openid")
    nick_name: str = Field(..., description="用户昵称")
    avatar_url: str = Field(..., description="头像URL")
    phone: str = Field(..., description="手机号")
    points: int = Field(..., description="积分")
    coupons: list = Field(default=[], description="优惠券列表")
    created_time: datetime = Field(..., description="注册时间")


class LoginResponse(Schema):
    token: str = Field(..., description="JWT 认证令牌")
    user: UserOut = Field(..., description="用户信息")
    is_new: bool = Field(default=False, description="是否新用户")

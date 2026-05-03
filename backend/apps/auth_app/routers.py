from ninja import Router
from core.auth import create_token
from .schemas import LoginRequest
from .services import login_with_code

router = Router()


@router.post("/login", response={200: dict, 400: dict}, summary="微信登录", description="使用微信小程序 code 换取用户信息和 JWT 令牌")
def login(request, body: LoginRequest):
    user, is_new = login_with_code(body.code)
    token = create_token(user.id, user.openid)
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "openid": user.openid,
                "nick_name": user.nick_name,
                "avatar_url": user.avatar_url,
                "phone": user.phone,
                "points": user.points,
                "coupons": user.coupons or [],
                "created_time": user.created_time.isoformat(),
            },
            "is_new": is_new,
        },
    }

import os
import requests
from .models import User

WX_APPID = os.environ.get("WX_APPID", "")
WX_SECRET = os.environ.get("WX_SECRET", "")
WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


def get_openid_from_wx(code: str) -> str | None:
    resp = requests.get(WX_CODE2SESSION_URL, params={
        "appid": WX_APPID,
        "secret": WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }, timeout=10)
    data = resp.json()
    if "openid" in data:
        return data["openid"]
    return None


def login_with_code(code: str) -> tuple[User, bool]:
    openid = get_openid_from_wx(code)
    if not openid:
        raise Exception("微信登录失败: invalid code")

    from django.utils import timezone
    user, is_new = User.objects.get_or_create(
        openid=openid,
        defaults={"last_login_time": timezone.now()},
    )
    if not is_new:
        user.last_login_time = timezone.now()
        user.save(update_fields=["last_login_time"])
    return user, is_new

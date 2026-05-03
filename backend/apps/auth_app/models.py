from django.db import models


class User(models.Model):
    openid = models.CharField(max_length=64, unique=True)
    nick_name = models.CharField(max_length=100, default="微信用户")
    avatar_url = models.CharField(max_length=500, default="/images/avatar.png")
    phone = models.CharField(max_length=20, blank=True, default="")
    points = models.IntegerField(default=0)
    coupons = models.JSONField(default=list, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

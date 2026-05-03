from django.db import models
from apps.auth_app.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ("待付款", "待付款"),
        ("已付款", "已付款"),
        ("已退款", "已退款"),
        ("已取消", "已取消"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    openid = models.CharField(max_length=64)
    activity_id = models.BigIntegerField()
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="待付款", choices=STATUS_CHOICES)
    contact_name = models.CharField(max_length=50, blank=True, default="")
    contact_phone = models.CharField(max_length=20, blank=True, default="")
    remark = models.CharField(max_length=500, blank=True, default="")
    pay_time = models.DateTimeField(null=True, blank=True)
    pay_method = models.CharField(max_length=50, blank=True, default="")
    refund_time = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=64, blank=True, default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["openid"]),
            models.Index(fields=["activity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_time"]),
        ]

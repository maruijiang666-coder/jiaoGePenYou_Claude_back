from django.db import models
from apps.auth_app.models import User


class Review(models.Model):
    activity_id = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    order_id = models.BigIntegerField(null=True, blank=True)
    rating = models.SmallIntegerField()
    content = models.TextField(blank=True, default="")
    images = models.JSONField(default=list, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        indexes = [
            models.Index(fields=["activity_id"]),
            models.Index(fields=["user"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "user"], name="unique_order_user_review"
            ),
        ]

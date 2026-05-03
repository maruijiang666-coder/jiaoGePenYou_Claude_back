from django.db import models


class Activity(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.JSONField(default=list, blank=True)
    detail_images = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=50, blank=True, default="")
    time_category = models.CharField(max_length=50, blank=True, default="")
    group_category = models.CharField(max_length=50, blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")
    duration = models.CharField(max_length=50, blank=True, default="")
    difficulty = models.CharField(max_length=50, blank=True, default="")
    min_people = models.IntegerField(default=2)
    max_people = models.IntegerField(default=20)
    club = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    detail = models.TextField(blank=True, default="")
    display_type = models.CharField(max_length=20, default="small")
    is_new = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="上架")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    rating_count = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    theme_id = models.BigIntegerField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activities"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["time_category"]),
            models.Index(fields=["group_category"]),
            models.Index(fields=["status"]),
        ]

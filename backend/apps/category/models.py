from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, default="")
    type = models.CharField(max_length=20)
    sort = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["type", "sort"]),
        ]

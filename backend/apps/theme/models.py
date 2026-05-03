from django.db import models


class Theme(models.Model):
    name = models.CharField(max_length=100)
    cover_image = models.CharField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    sort = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="显示")
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "themes"
        indexes = [models.Index(fields=["status", "sort"])]

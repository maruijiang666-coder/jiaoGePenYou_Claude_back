from django.db import models


class Config(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField(blank=True, default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "config"

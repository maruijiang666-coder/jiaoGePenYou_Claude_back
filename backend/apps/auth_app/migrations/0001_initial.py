# Generated migration for auth_app
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("openid", models.CharField(max_length=64, unique=True)),
                ("nick_name", models.CharField(default="微信用户", max_length=100)),
                ("avatar_url", models.CharField(default="/images/avatar.png", max_length=500)),
                ("phone", models.CharField(blank=True, default="", max_length=20)),
                ("points", models.IntegerField(default=0)),
                ("coupons", models.JSONField(blank=True, default=list)),
                ("last_login_time", models.DateTimeField(blank=True, null=True)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "users"},
        ),
    ]

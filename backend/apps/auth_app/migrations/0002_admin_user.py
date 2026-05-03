from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="AdminUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=50, unique=True)),
                ("password", models.CharField(max_length=255)),
                ("role", models.CharField(default="admin", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "admin_users"},
        ),
    ]

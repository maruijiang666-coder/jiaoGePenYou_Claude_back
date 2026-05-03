from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Theme",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("cover_image", models.CharField(blank=True, default="", max_length=500)),
                ("description", models.TextField(blank=True, default="")),
                ("sort", models.IntegerField(default=0)),
                ("status", models.CharField(default="显示", max_length=20)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "themes"},
        ),
        migrations.AddIndex(
            model_name="theme",
            index=models.Index(fields=["status", "sort"], name="themes_status_sort_idx"),
        ),
    ]

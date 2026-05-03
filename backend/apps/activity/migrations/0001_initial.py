from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("images", models.JSONField(blank=True, default=list)),
                ("detail_images", models.JSONField(blank=True, default=list)),
                ("category", models.CharField(blank=True, default="", max_length=50)),
                ("time_category", models.CharField(blank=True, default="", max_length=50)),
                ("group_category", models.CharField(blank=True, default="", max_length=50)),
                ("location", models.CharField(blank=True, default="", max_length=200)),
                ("duration", models.CharField(blank=True, default="", max_length=50)),
                ("difficulty", models.CharField(blank=True, default="", max_length=50)),
                ("min_people", models.IntegerField(default=2)),
                ("max_people", models.IntegerField(default=20)),
                ("club", models.JSONField(blank=True, default=dict)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("detail", models.TextField(blank=True, default="")),
                ("display_type", models.CharField(default="small", max_length=20)),
                ("is_new", models.BooleanField(default=False)),
                ("status", models.CharField(default="上架", max_length=20)),
                ("rating", models.DecimalField(decimal_places=1, default=5.0, max_digits=2)),
                ("rating_count", models.IntegerField(default=0)),
                ("sold_count", models.IntegerField(default=0)),
                ("theme_id", models.BigIntegerField(blank=True, null=True)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "activities"},
        ),
        migrations.AddIndex(
            model_name="activity",
            index=models.Index(fields=["category"], name="activities_category_idx"),
        ),
        migrations.AddIndex(
            model_name="activity",
            index=models.Index(fields=["time_category"], name="activities_time_cat_idx"),
        ),
        migrations.AddIndex(
            model_name="activity",
            index=models.Index(fields=["group_category"], name="activities_group_cat_idx"),
        ),
        migrations.AddIndex(
            model_name="activity",
            index=models.Index(fields=["status"], name="activities_status_idx"),
        ),
    ]

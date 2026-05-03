from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50)),
                ("icon", models.CharField(blank=True, default="", max_length=50)),
                ("type", models.CharField(max_length=20)),
                ("sort", models.IntegerField(default=0)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "categories"},
        ),
        migrations.AddIndex(
            model_name="category",
            index=models.Index(fields=["type"], name="categories_type_idx"),
        ),
        migrations.AddIndex(
            model_name="category",
            index=models.Index(fields=["type", "sort"], name="categories_type_sort_idx"),
        ),
    ]

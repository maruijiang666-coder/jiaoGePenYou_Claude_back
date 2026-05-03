from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth_app", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_id", models.BigIntegerField()),
                ("order_id", models.BigIntegerField(blank=True, null=True)),
                ("rating", models.SmallIntegerField()),
                ("content", models.TextField(blank=True, default="")),
                ("images", models.JSONField(blank=True, default=list)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="auth_app.user")),
            ],
            options={"db_table": "reviews"},
        ),
        migrations.AddIndex(model_name="review", index=models.Index(fields=["activity_id"], name="reviews_activity_idx")),
        migrations.AddIndex(model_name="review", index=models.Index(fields=["user"], name="reviews_user_idx")),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(fields=["order_id", "user"], name="unique_order_user_review"),
        ),
    ]

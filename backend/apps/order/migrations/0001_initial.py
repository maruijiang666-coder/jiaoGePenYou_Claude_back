from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth_app", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("openid", models.CharField(max_length=64)),
                ("activity_id", models.BigIntegerField()),
                ("quantity", models.IntegerField(default=1)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("待付款", "待付款"), ("已付款", "已付款"), ("已退款", "已退款"), ("已取消", "已取消")], default="待付款", max_length=20)),
                ("contact_name", models.CharField(blank=True, default="", max_length=50)),
                ("contact_phone", models.CharField(blank=True, default="", max_length=20)),
                ("remark", models.CharField(blank=True, default="", max_length=500)),
                ("pay_time", models.DateTimeField(blank=True, null=True)),
                ("pay_method", models.CharField(blank=True, default="", max_length=50)),
                ("refund_time", models.DateTimeField(blank=True, null=True)),
                ("transaction_id", models.CharField(blank=True, default="", max_length=64)),
                ("created_time", models.DateTimeField(auto_now_add=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="orders", to="auth_app.user")),
            ],
            options={"db_table": "orders"},
        ),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["user"], name="orders_user_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["openid"], name="orders_openid_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["activity_id"], name="orders_activity_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["status"], name="orders_status_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["created_time"], name="orders_created_idx")),
    ]

from django.db import migrations

SEED_DATA = [
    {"name": "户外徒步", "icon": "hiking", "type": "activity", "sort": 1},
    {"name": "民俗体验", "icon": "festival", "type": "activity", "sort": 2},
    {"name": "手作艺术", "icon": "palette", "type": "activity", "sort": 3},
    {"name": "地道美食", "icon": "restaurant", "type": "activity", "sort": 4},
    {"name": "露营时光", "icon": "camping", "type": "activity", "sort": 5},
    {"name": "亲子研学", "icon": "child_care", "type": "activity", "sort": 6},
    {"name": "艺术沙龙", "icon": "theater_comedy", "type": "activity", "sort": 7},
    {"name": "山野寻踪", "icon": "landscape", "type": "activity", "sort": 8},
    {"name": "单日活动", "icon": "today", "type": "time", "sort": 1},
    {"name": "多日进阶", "icon": "date_range", "type": "time", "sort": 2},
    {"name": "儿童", "icon": "child_friendly", "type": "group", "sort": 1},
    {"name": "家庭", "icon": "family_restroom", "type": "group", "sort": 2},
    {"name": "情侣闺蜜好友", "icon": "group", "type": "group", "sort": 3},
]


def insert_seed(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    for item in SEED_DATA:
        Category.objects.get_or_create(
            name=item["name"],
            type=item["type"],
            defaults={"icon": item["icon"], "sort": item["sort"]},
        )


def remove_seed(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    for item in SEED_DATA:
        Category.objects.filter(name=item["name"], type=item["type"]).delete()


class Migration(migrations.Migration):
    dependencies = [("category", "0001_initial")]
    operations = [migrations.RunPython(insert_seed, remove_seed)]

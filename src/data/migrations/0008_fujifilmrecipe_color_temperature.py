from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0007_populate_and_remove_recipe_fields_from_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="fujifilmrecipe",
            name="color_temperature",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]

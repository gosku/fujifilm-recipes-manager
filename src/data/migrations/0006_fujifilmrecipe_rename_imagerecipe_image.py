# Generated manually on 2026-03-12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0005_add_new_fujifilm_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="FujifilmRecipe",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, default="", max_length=255)),
                ("film_simulation", models.CharField(blank=True, default="", max_length=100)),
                ("dynamic_range", models.CharField(blank=True, default="", max_length=100)),
                ("dynamic_range_setting", models.CharField(blank=True, default="", max_length=100)),
                ("development_dynamic_range", models.CharField(blank=True, default="", max_length=50)),
                ("white_balance", models.CharField(blank=True, default="", max_length=100)),
                ("white_balance_fine_tune", models.CharField(blank=True, default="", max_length=200)),
                ("highlight_tone", models.CharField(blank=True, default="", max_length=100)),
                ("shadow_tone", models.CharField(blank=True, default="", max_length=100)),
                ("color", models.CharField(blank=True, default="", max_length=100)),
                ("sharpness", models.CharField(blank=True, default="", max_length=100)),
                ("noise_reduction", models.CharField(blank=True, default="", max_length=100)),
                ("clarity", models.CharField(blank=True, default="", max_length=100)),
                ("color_chrome_effect", models.CharField(blank=True, default="", max_length=100)),
                ("color_chrome_fx_blue", models.CharField(blank=True, default="", max_length=100)),
                ("grain_effect_roughness", models.CharField(blank=True, default="", max_length=100)),
                ("grain_effect_size", models.CharField(blank=True, default="", max_length=100)),
            ],
        ),
        migrations.RenameModel(
            old_name="ImageRecipe",
            new_name="Image",
        ),
        migrations.AddField(
            model_name="image",
            name="recipe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="images",
                to="data.fujifilmrecipe",
            ),
        ),
    ]

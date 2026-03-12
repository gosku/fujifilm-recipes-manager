# Generated manually on 2026-03-12

from django.db import migrations

_RECIPE_FIELDS = [
    "film_simulation",
    "dynamic_range",
    "dynamic_range_setting",
    "development_dynamic_range",
    "white_balance",
    "white_balance_fine_tune",
    "highlight_tone",
    "shadow_tone",
    "color",
    "sharpness",
    "noise_reduction",
    "clarity",
    "color_chrome_effect",
    "color_chrome_fx_blue",
    "grain_effect_roughness",
    "grain_effect_size",
]


def populate_recipes(apps, schema_editor):
    Image = apps.get_model("data", "Image")
    FujifilmRecipe = apps.get_model("data", "FujifilmRecipe")
    for combo in Image.objects.values(*_RECIPE_FIELDS).distinct():
        recipe, _ = FujifilmRecipe.objects.get_or_create(**combo)
        Image.objects.filter(**combo, recipe__isnull=True).update(recipe=recipe)


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0006_fujifilmrecipe_rename_imagerecipe_image"),
    ]

    operations = [
        migrations.RunPython(populate_recipes, migrations.RunPython.noop),
        migrations.RemoveField(model_name="image", name="film_simulation"),
        migrations.RemoveField(model_name="image", name="dynamic_range"),
        migrations.RemoveField(model_name="image", name="dynamic_range_setting"),
        migrations.RemoveField(model_name="image", name="development_dynamic_range"),
        migrations.RemoveField(model_name="image", name="white_balance"),
        migrations.RemoveField(model_name="image", name="white_balance_fine_tune"),
        migrations.RemoveField(model_name="image", name="highlight_tone"),
        migrations.RemoveField(model_name="image", name="shadow_tone"),
        migrations.RemoveField(model_name="image", name="color"),
        migrations.RemoveField(model_name="image", name="sharpness"),
        migrations.RemoveField(model_name="image", name="noise_reduction"),
        migrations.RemoveField(model_name="image", name="clarity"),
        migrations.RemoveField(model_name="image", name="color_chrome_effect"),
        migrations.RemoveField(model_name="image", name="color_chrome_fx_blue"),
        migrations.RemoveField(model_name="image", name="grain_effect_roughness"),
        migrations.RemoveField(model_name="image", name="grain_effect_size"),
    ]

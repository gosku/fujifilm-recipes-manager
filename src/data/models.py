from django.db import models

RECIPE_FIELDS = [
    "film_simulation",
    "dynamic_range",
    "dynamic_range_setting",
    "development_dynamic_range",
    "white_balance",
    "white_balance_fine_tune",
    "color_temperature",
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


class FujifilmRecipe(models.Model):
    name = models.CharField(max_length=255, blank=True, default="")

    film_simulation = models.CharField(max_length=100, blank=True, default="")
    dynamic_range = models.CharField(max_length=100, blank=True, default="")
    dynamic_range_setting = models.CharField(max_length=100, blank=True, default="")
    development_dynamic_range = models.CharField(max_length=50, blank=True, default="")
    white_balance = models.CharField(max_length=100, blank=True, default="")
    white_balance_fine_tune = models.CharField(max_length=200, blank=True, default="")
    color_temperature = models.CharField(max_length=50, blank=True, default="")
    highlight_tone = models.CharField(max_length=100, blank=True, default="")
    shadow_tone = models.CharField(max_length=100, blank=True, default="")
    color = models.CharField(max_length=100, blank=True, default="")
    sharpness = models.CharField(max_length=100, blank=True, default="")
    noise_reduction = models.CharField(max_length=100, blank=True, default="")
    clarity = models.CharField(max_length=100, blank=True, default="")
    color_chrome_effect = models.CharField(max_length=100, blank=True, default="")
    color_chrome_fx_blue = models.CharField(max_length=100, blank=True, default="")
    grain_effect_roughness = models.CharField(max_length=100, blank=True, default="")
    grain_effect_size = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        if self.name:
            return self.name
        return self.film_simulation or "Unknown recipe"


class Image(models.Model):
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=1024, unique=True)

    # Camera info
    camera_make = models.CharField(max_length=100, blank=True, default="")
    camera_model = models.CharField(max_length=100, blank=True, default="")

    # Shooting settings
    quality = models.CharField(max_length=50, blank=True, default="")
    flash_mode = models.CharField(max_length=100, blank=True, default="")
    flash_exposure_comp = models.CharField(max_length=50, blank=True, default="")
    focus_mode = models.CharField(max_length=100, blank=True, default="")
    shutter_type = models.CharField(max_length=100, blank=True, default="")
    lens_modulation_optimizer = models.CharField(max_length=50, blank=True, default="")
    picture_mode = models.CharField(max_length=100, blank=True, default="")
    drive_mode = models.CharField(max_length=100, blank=True, default="")
    image_stabilization = models.CharField(max_length=200, blank=True, default="")

    # Exposure info
    iso = models.CharField(max_length=50, blank=True, default="")
    exposure_compensation = models.CharField(max_length=50, blank=True, default="")

    # Date
    date_taken = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    recipe = models.ForeignKey(
        FujifilmRecipe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="images",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.filename

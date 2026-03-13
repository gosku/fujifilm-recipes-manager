# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_alter_fujifilmrecipe_id'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FujifilmRecipe',
            new_name='FujifilmExif',
        ),
        # Creative / recipe
        migrations.AddField(
            model_name='fujifilmexif',
            name='bw_adjustment',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='bw_magenta_green',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='d_range_priority',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='d_range_priority_auto',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='auto_dynamic_range',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        # Autofocus
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_mode',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='focus_pixel',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_s_priority',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_c_priority',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='focus_mode_2',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='pre_af',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_area_mode',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_area_point_size',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_area_zone_size',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_c_setting',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_c_tracking_sensitivity',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_c_speed_tracking_sensitivity',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='af_c_zone_area_switching',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        # Drive / flash / stabilization
        migrations.AddField(
            model_name='fujifilmexif',
            name='slow_sync',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='auto_bracketing',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='drive_speed',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='crop_mode',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='flicker_reduction',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        # Shot metadata
        migrations.AddField(
            model_name='fujifilmexif',
            name='sequence_number',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='exposure_count',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='image_generation',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='image_count',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='scene_recognition',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        # Warnings / status
        migrations.AddField(
            model_name='fujifilmexif',
            name='blur_warning',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='focus_warning',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='exposure_warning',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        # Lens info
        migrations.AddField(
            model_name='fujifilmexif',
            name='min_focal_length',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='max_focal_length',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='max_aperture_at_min_focal',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='max_aperture_at_max_focal',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        # Camera hardware info
        migrations.AddField(
            model_name='fujifilmexif',
            name='version',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='internal_serial_number',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='fuji_model',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='fuji_model_2',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        # Face detection
        migrations.AddField(
            model_name='fujifilmexif',
            name='faces_detected',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='num_face_elements',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='face_element_positions',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='face_element_selected',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='face_element_types',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='fujifilmexif',
            name='face_positions',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]

# Generated by Django 3.2.7 on 2021-09-28 22:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0012_alter_siae_nature"),
    ]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="geo_range",
            field=models.CharField(
                blank=True,
                choices=[
                    ("COUNTRY", "France entière"),
                    ("REGION", "Région"),
                    ("DEPARTMENT", "Département"),
                    ("CUSTOM", "Distance en kilomètres"),
                ],
                max_length=20,
                null=True,
                verbose_name="Périmètre d'intervention",
            ),
        ),
        migrations.AddField(
            model_name="siae",
            name="geo_range_custom_distance",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Distance en kilomètres (périmètre d'intervention)"
            ),
        ),
    ]

# Generated by Django 4.0.4 on 2022-04-13 09:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0054_alter_siae_presta_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siae",
            name="is_active",
            field=models.BooleanField(
                default=True, help_text="Convention active (C1) ou import", verbose_name="Active"
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="is_delisted",
            field=models.BooleanField(
                default=False, help_text="La structure n'apparaîtra plus dans les résultats", verbose_name="Masquée"
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="is_first_page",
            field=models.BooleanField(
                default=False, help_text="La structure apparaîtra sur la page principale", verbose_name="A la une"
            ),
        ),
    ]

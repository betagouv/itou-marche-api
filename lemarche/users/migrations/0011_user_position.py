# Generated by Django 3.2.8 on 2021-11-08 18:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_user_image_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="position",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Poste"),
        ),
    ]

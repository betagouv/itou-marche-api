# Generated by Django 4.2.17 on 2025-02-04 13:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_shepherd", "0007_userguide_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userguide",
            name="guided_users",
            field=models.ManyToManyField(
                blank=True,
                help_text="Utilisateurs qui ont déjà été guidés",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Utilisateurs guidés",
            ),
        ),
    ]

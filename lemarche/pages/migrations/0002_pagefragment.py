# Generated by Django 4.1.3 on 2023-01-19 15:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageFragment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, unique=True, verbose_name="Titre")),
                ("content", models.TextField(blank=True, verbose_name="Contenu")),
                (
                    "is_live",
                    models.BooleanField(
                        default=True,
                        help_text="Laisser vide pour cacher le contenu dans l'application",
                        verbose_name="Visible",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
            ],
            options={
                "ordering": ["title"],
                "verbose_name": "Fragment de page",
                "verbose_name_plural": "Fragments de page",
            },
        ),
    ]

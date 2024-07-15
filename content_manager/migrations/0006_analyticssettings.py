# Generated by Django 4.1.9 on 2023-07-07 13:56

import django.db.models.deletion
from django.db import migrations, models

import content_manager.models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0078_referenceindex"),
        ("content_manager", "0005_alter_contentpage_body"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnalyticsSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "head_scripts",
                    content_manager.models.MonospaceField(
                        blank=True,
                        help_text="Ajoutez des scripts de suivi entre les balises <head>.",
                        null=True,
                        verbose_name="Scripts de suivi <head>",
                    ),
                ),
                (
                    "body_scripts",
                    content_manager.models.MonospaceField(
                        blank=True,
                        help_text="Ajoutez des scripts de suivi vers la fermeture de la balise <body>.",
                        null=True,
                        verbose_name="Scripts de suivi <body>",
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False, on_delete=django.db.models.deletion.CASCADE, to="wagtailcore.site"
                    ),
                ),
            ],
            options={
                "verbose_name": "Scripts de suivi",
            },
        ),
    ]

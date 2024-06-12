# Generated by Django 4.2.13 on 2024-06-10 15:00

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("sectors", "0003_sector_sectorgroup_ordering"),
        ("siaes", "0075_historicalsiae"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiaeActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "presta_type",
                    lemarche.utils.fields.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("DISP", "Mise à disposition - Interim"),
                                ("PREST", "Prestation de service"),
                                ("BUILD", "Fabrication et commercialisation de biens"),
                            ],
                            max_length=20,
                        ),
                        blank=True,
                        db_index=True,
                        null=True,
                        size=None,
                        verbose_name="Type de prestation",
                    ),
                ),
                (
                    "geo_range",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("COUNTRY", "France entière"),
                            ("REGION", "Région"),
                            ("DEPARTMENT", "Département"),
                            ("CUSTOM", "Distance en kilomètres"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Périmètre d'intervention",
                    ),
                ),
                (
                    "geo_range_custom_distance",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Distance en kilomètres (périmètre d'intervention)"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                (
                    "sectors",
                    models.ManyToManyField(
                        blank=True,
                        related_name="siae_activities",
                        to="sectors.sector",
                        verbose_name="Secteurs d'activité",
                    ),
                ),
                (
                    "siae",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="siaes.siae",
                        verbose_name="Structure",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="siae_activities_location",
                        to="perimeters.perimeter",
                        verbose_name="Localisation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Activité",
                "verbose_name_plural": "Activités",
                "ordering": ["-created_at"],
            },
        ),
    ]

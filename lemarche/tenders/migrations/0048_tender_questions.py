# Generated by Django 4.1.7 on 2023-05-04 14:51

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0047_tender_import_raw_object"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tender",
            options={
                "ordering": ["-created_at", "deadline_date"],
                "verbose_name": "Besoin d'achat",
                "verbose_name_plural": "Besoins d'achat",
            },
        ),
        migrations.AlterField(
            model_name="tendersiae",
            name="tender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tenders.tender", verbose_name="Besoin d'achat"
            ),
        ),
        migrations.CreateModel(
            name="TenderQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(verbose_name="Intitulé de la question")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                (
                    "tender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="tenders.tender",
                        verbose_name="Besoin d'achat",
                    ),
                ),
            ],
            options={
                "verbose_name": "Question de l'acheteur",
                "verbose_name_plural": "Questions de l'acheteur",
            },
        ),
    ]

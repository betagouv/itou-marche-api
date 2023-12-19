# Generated by Django 4.2.2 on 2023-12-14 09:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0011_conversation_sender_siae_encoded_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="TemplateTransactional",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Nom")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                (
                    "mailjet_id",
                    models.IntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        unique=True,
                        verbose_name="Identifiant Mailjet",
                    ),
                ),
                (
                    "brevo_id",
                    models.IntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        unique=True,
                        verbose_name="Identifiant Brevo",
                    ),
                ),
                ("is_active", models.BooleanField(default=False, verbose_name="Actif")),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        choices=[("MAILJET", "Mailjet"), ("BREVO", "Brevo")],
                        max_length=20,
                        verbose_name="Source",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
            ],
            options={
                "verbose_name": "Template transactionnel",
                "verbose_name_plural": "Templates transactionnels",
            },
        ),
    ]

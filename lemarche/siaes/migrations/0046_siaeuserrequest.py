# Generated by Django 4.0.2 on 2022-02-15 11:31

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("siaes", "0045_siae_signup_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiaeUserRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                (
                    "assignee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="siaeuserrequest_assignee",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Responsable",
                    ),
                ),
                (
                    "siae",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="siaes.siae", verbose_name="Structure"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
                (
                    "response",
                    models.BooleanField(blank=True, null=True, verbose_name="Réponse"),
                ),
                (
                    "response_date",
                    models.DateTimeField(blank=True, null=True, verbose_name="Date de la réponse"),
                ),
                (
                    "logs",
                    models.JSONField(editable=False, null=True, verbose_name="Logs des échanges"),
                ),
            ],
            options={
                "verbose_name": "Demande de rattachement",
                "verbose_name_plural": "Demandes de rattachement",
                "ordering": ["-created_at"],
            },
        ),
    ]

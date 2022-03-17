# Generated by Django 4.0.2 on 2022-03-17 10:42

import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("perimeters", "0004_alter_perimeter_post_codes"),
        ("sectors", "0003_sector_sectorgroup_ordering"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tender",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "kind",
                    models.CharField(
                        choices=[("TENDER", "Appel d'offre"), ("QUOTE", "Devis")],
                        default="TENDER",
                        max_length=6,
                        verbose_name="Type de besoin",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Titre du besoin")),
                ("description", models.TextField(blank=True, verbose_name="Description du besoin")),
                ("constraints", models.TextField(blank=True, verbose_name="Contraintes techniques spécifiques")),
                ("external_link", models.URLField(blank=True, verbose_name="Lien vers l’appel d’offre")),
                ("deadline_date", models.DateField(verbose_name="Date de clôture des réponses")),
                (
                    "start_working_date",
                    models.DateField(blank=True, null=True, verbose_name="Date idéale de début des prestations"),
                ),
                ("contact_first_name", models.CharField(blank=True, max_length=255, verbose_name="Prénom du contact")),
                (
                    "contact_last_name",
                    models.CharField(blank=True, max_length=255, verbose_name="Nom de famille du contact"),
                ),
                ("contact_email", models.EmailField(blank=True, max_length=254, verbose_name="Email du contact")),
                ("contact_phone", models.CharField(blank=True, max_length=20, verbose_name="Téléphone du contact")),
                ("amount", models.PositiveIntegerField(blank=True, null=True, verbose_name="Montant du marché")),
                (
                    "response_kind",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[("EMAIL", "Email"), ("TEL", "Téléphone"), ("EXTERN", "Lien externe")],
                            max_length=6,
                        ),
                        size=None,
                        verbose_name="Comment souhaitez-vous être contacté ?",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
                ("slug", models.SlugField(max_length=255, unique=True, verbose_name="Slug")),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tenders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "perimeters",
                    models.ManyToManyField(
                        related_name="tenders", to="perimeters.Perimeter", verbose_name="Lieux d'exécutions"
                    ),
                ),
                (
                    "sectors",
                    models.ManyToManyField(
                        related_name="tenders", to="sectors.Sector", verbose_name="Secteurs d'activités"
                    ),
                ),
            ],
            options={
                "verbose_name": "Besoin d'acheteur",
                "verbose_name_plural": "Besoins des acheteurs",
                "ordering": ["-updated_at", "deadline_date"],
            },
        ),
    ]

# Generated by Django 4.0.7 on 2022-09-06 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatsUser",
            fields=[
                (
                    "id",
                    models.PositiveIntegerField(
                        db_index=True, primary_key=True, serialize=False, verbose_name="ID app leMarche"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="Adresse e-mail")),
                ("first_name", models.CharField(max_length=150, verbose_name="Prénom")),
                ("last_name", models.CharField(max_length=150, verbose_name="Nom")),
                ("kind", models.CharField(blank=True, max_length=20, verbose_name="Type d'utilisateur")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="Téléphone")),
                ("company_name", models.CharField(blank=True, max_length=255, verbose_name="Nom de l'entreprise")),
                ("position", models.CharField(blank=True, max_length=255, verbose_name="Poste")),
                ("partner_kind", models.CharField(blank=True, max_length=20, verbose_name="Type de partenaire")),
            ],
            options={
                "db_table": "stats_user",
            },
        ),
    ]

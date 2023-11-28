# Generated by Django 4.2.2 on 2023-07-06 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0006_tracker_siae_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="tracker",
            name="siae_contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="tracker",
            name="siae_kind",
            field=models.CharField(
                blank=True,
                choices=[
                    ("EI", "Entreprise d'insertion (EI)"),
                    ("AI", "Association intermédiaire (AI)"),
                    ("ACI", "Atelier chantier d'insertion (ACI)"),
                    ("ETTI", "Entreprise de travail temporaire d'insertion (ETTI)"),
                    ("EITI", "Entreprise d'insertion par le travail indépendant (EITI)"),
                    ("GEIQ", "Groupement d'employeurs pour l'insertion et la qualification (GEIQ)"),
                    ("SEP", "Produits et services réalisés en prison"),
                    ("EA", "Entreprise adaptée (EA)"),
                    ("EATT", "Entreprise adaptée de travail temporaire (EATT)"),
                    ("ESAT", "Etablissement et service d'aide par le travail (ESAT)"),
                ],
                max_length=6,
            ),
        ),
    ]

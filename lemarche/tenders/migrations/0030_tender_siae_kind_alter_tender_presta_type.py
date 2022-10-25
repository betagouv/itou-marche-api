# Generated by Django 4.1.2 on 2022-10-25 15:25

from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0029_alter_tendersiae_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="siae_kind",
            field=lemarche.utils.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("EI", "Entreprise d'insertion"),
                        ("AI", "Association intermédiaire"),
                        ("ACI", "Atelier chantier d'insertion"),
                        ("ETTI", "Entreprise de travail temporaire d'insertion"),
                        ("EITI", "Entreprise d'insertion par le travail indépendant"),
                        ("GEIQ", "Groupement d'employeurs pour l'insertion et la qualification"),
                        ("EA", "Entreprise adaptée"),
                        ("EATT", "Entreprise adaptée de travail temporaire"),
                        ("ESAT", "Etablissement et service d'aide par le travail"),
                        ("SEP", "Produits et services réalisés en prison"),
                    ],
                    max_length=20,
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Type de structure",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="presta_type",
            field=lemarche.utils.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("DISP", "Mise à disposition - Interim"),
                        ("PREST", "Prestation de service"),
                        ("BUILD", "Fabrication et commercialisation de biens"),
                    ],
                    max_length=20,
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Type de prestation",
            ),
        ),
    ]

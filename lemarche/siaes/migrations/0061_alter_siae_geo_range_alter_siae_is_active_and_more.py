# Generated by Django 4.1.9 on 2023-06-21 16:19

from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0060_siae_labels_m2m"),
    ]

    operations = [
        migrations.AlterField(
            model_name="siae",
            name="geo_range",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="siae",
            name="is_active",
            field=models.BooleanField(
                db_index=True, default=True, help_text="Convention active (C1) ou import", verbose_name="Active"
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="is_delisted",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="La structure n'apparaîtra plus dans les résultats",
                verbose_name="Masquée",
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="is_qpv",
            field=models.BooleanField(
                db_index=True, default=False, verbose_name="Quartier prioritaire de la politique de la ville (API QPV)"
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="is_zrr",
            field=models.BooleanField(
                db_index=True, default=False, verbose_name="Zone de revitalisation rurale (API ZRR)"
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="kind",
            field=models.CharField(
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
                db_index=True,
                default="EI",
                max_length=6,
                verbose_name="Type de structure",
            ),
        ),
        migrations.AlterField(
            model_name="siae",
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
                db_index=True,
                null=True,
                size=None,
                verbose_name="Type de prestation",
            ),
        ),
        migrations.AlterField(
            model_name="siaegroup",
            name="contact_email",
            field=models.EmailField(blank=True, db_index=True, max_length=254, verbose_name="E-mail"),
        ),
        migrations.AlterField(
            model_name="siaegroup",
            name="siret",
            field=models.CharField(blank=True, db_index=True, max_length=14, verbose_name="Siret"),
        ),
    ]

# Generated by Django 4.1.9 on 2023-07-11 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0049_tender_amount_exact"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="source",
            field=models.CharField(
                choices=[
                    ("FORM", "Formulaire"),
                    ("FORM_CSRF", "Formulaire (erreur CSRF)"),
                    ("STAFF_C4_CREATED", "Staff Marché (via l'Admin)"),
                    ("API", "API"),
                    ("TALLY", "TALLY"),
                ],
                default="FORM",
                max_length=20,
                verbose_name="Source",
            ),
        ),
    ]

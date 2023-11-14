# Generated by Django 4.1.7 on 2023-04-17 15:37

from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("tenders", "0044_alter_tender_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="deadline_date",
            field=models.DateField(
                blank=True,
                help_text="Sélectionnez la date jusqu'à laquelle vous acceptez des réponses",
                null=True,
                verbose_name="Date de clôture des réponses",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="response_kind",
            field=lemarche.utils.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[("EMAIL", "E-mail"), ("TEL", "Téléphone"), ("EXTERN", "Lien externe")], max_length=6
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Comment souhaitez-vous être contacté ?",
            ),
        ),
    ]

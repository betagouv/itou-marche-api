# Generated by Django 4.0.4 on 2022-04-13 08:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import lemarche.utils.fields


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tenders", "0007_alter_tender_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="author",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tenders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Auteur",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="response_kind",
            field=lemarche.utils.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[("EMAIL", "E-mail"), ("TEL", "Téléphone"), ("EXTERN", "Lien externe")], max_length=6
                ),
                size=None,
                verbose_name="Comment souhaitez-vous être contacté ?",
            ),
        ),
    ]

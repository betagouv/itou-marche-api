# Generated by Django 4.1.7 on 2023-04-19 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0045_alter_tender_deadline_date_response_kind_not_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="import_raw_object",
            field=models.JSONField(editable=False, null=True, verbose_name="Données d'import"),
        ),
    ]

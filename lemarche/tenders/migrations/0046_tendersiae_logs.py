# Generated by Django 4.1.7 on 2023-04-19 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0045_alter_tender_deadline_date_response_kind_not_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="tendersiae",
            name="logs",
            field=models.JSONField(default=list, editable=False, verbose_name="Logs historiques"),
        ),
    ]

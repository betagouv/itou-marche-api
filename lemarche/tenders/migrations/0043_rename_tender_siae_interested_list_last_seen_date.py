# Generated by Django 4.1.7 on 2023-03-01 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0042_tender_why_amount_is_blank"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tender",
            old_name="siae_interested_list_last_seen_date",
            new_name="siae_list_last_seen_date",
        ),
    ]

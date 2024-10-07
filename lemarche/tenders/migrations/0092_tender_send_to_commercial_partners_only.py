# Generated by Django 4.2.15 on 2024-09-27 12:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenders", "0091_tender_is_followed_by_us_tender_is_reserved_tender_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="send_to_commercial_partners_only",
            field=models.BooleanField(default=False, verbose_name="Envoyer uniquement aux partenaires externes"),
        ),
    ]

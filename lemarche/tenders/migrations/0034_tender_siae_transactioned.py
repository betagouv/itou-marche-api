# Generated by Django 4.1.3 on 2022-11-28 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0033_tender_include_country_area"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="siae_transactioned",
            field=models.BooleanField(default=False, verbose_name="Abouti à une transaction avec une structure"),
        ),
    ]

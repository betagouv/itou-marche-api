# Generated by Django 4.0.2 on 2022-04-05 09:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0053_siae_contact_social_website_and_more"),
        ("tenders", "0004_tendersiae_tender_siaes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="siaes",
            field=models.ManyToManyField(
                blank=True,
                related_name="tenders",
                through="tenders.TenderSiae",
                to="siaes.Siae",
                verbose_name="Structures correspondantes au besoin",
            ),
        ),
        migrations.RemoveField(
            model_name="tender",
            name="siae_found_count",
        ),
    ]

# Generated by Django 4.0.7 on 2022-10-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0023_alter_partnersharetender_amount_in_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="accept_cocontracting",
            field=models.BooleanField(
                default=False,
                help_text="Ce besoin peut-être répondu par plusieurs prestataires (co-traitance ou sous-traitance)",
                verbose_name="Ouvert à la co-traitance",
            ),
        ),
    ]

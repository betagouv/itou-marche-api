# Generated by Django 4.2.2 on 2023-07-25 00:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="kind",
            field=models.CharField(
                choices=[("SEARCH", "Recherche"), ("TENDER", "Dépôt de besoin")],
                db_index=True,
                default="SEARCH",
                max_length=10,
                verbose_name="Type de conversation",
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="siae",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="conversations",
                to="siaes.siae",
                verbose_name="Structure",
            ),
        ),
        migrations.AlterField(
            model_name="conversation",
            name="version",
            field=models.PositiveIntegerField(default=0, verbose_name="Version"),
        ),
    ]

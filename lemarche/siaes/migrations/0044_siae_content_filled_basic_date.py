# Generated by Django 4.0.2 on 2022-02-10 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("siaes", "0043_siae_c2_etp_count_siae_c2_etp_count_date_saisie_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="content_filled_basic_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date de remplissage (basique) de la fiche"
            ),
        ),
    ]

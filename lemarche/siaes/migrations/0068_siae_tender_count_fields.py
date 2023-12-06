# Generated by Django 4.2.2 on 2023-12-04 15:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0067_siae_completion_rate"),
    ]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="tender_count",
            field=models.IntegerField(
                default=0,
                help_text="Champ recalculé à intervalles réguliers",
                verbose_name="Nombre de besoins concernés",
            ),
        ),
        migrations.AddField(
            model_name="siae",
            name="tender_detail_contact_click_count",
            field=models.IntegerField(
                default=0,
                help_text="Champ recalculé à intervalles réguliers",
                verbose_name="Nombre de besoins intéressés",
            ),
        ),
        migrations.AddField(
            model_name="siae",
            name="tender_detail_display_count",
            field=models.IntegerField(
                default=0, help_text="Champ recalculé à intervalles réguliers", verbose_name="Nombre de besoins vus"
            ),
        ),
        migrations.AddField(
            model_name="siae",
            name="tender_email_link_click_count",
            field=models.IntegerField(
                default=0,
                help_text="Champ recalculé à intervalles réguliers",
                verbose_name="Nombre de besoins cliqués",
            ),
        ),
        migrations.AddField(
            model_name="siae",
            name="tender_email_send_count",
            field=models.IntegerField(
                default=0, help_text="Champ recalculé à intervalles réguliers", verbose_name="Nombre de besoins reçus"
            ),
        ),
    ]

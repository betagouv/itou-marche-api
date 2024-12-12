# Generated by Django 4.2.15 on 2024-12-26 18:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenders", "0094_add_templatetransactional_tender_author_commercial_partners"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="changes_information",
            field=models.TextField(
                blank=True, verbose_name="Informations complémentaires sur les modifications requises"
            ),
        ),
        migrations.AddField(
            model_name="tender",
            name="email_sent_for_modification",
            field=models.BooleanField(
                default=False,
                help_text="Envoyer un e-mail pour demander des modifications",
                verbose_name="Modifications requises",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="status",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Brouillon"),
                    ("PUBLISHED", "Publié"),
                    ("VALIDATED", "Validé"),
                    ("SENT", "Envoyé"),
                    ("REJECTED", "Rejeté"),
                ],
                default="DRAFT",
                max_length=10,
                verbose_name="Statut",
            ),
        ),
    ]

# Generated by Django 4.2.15 on 2025-01-03 10:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenders", "0094_add_templatetransactional_tender_author_commercial_partners"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tender",
            old_name="accept_cocontracting",
            new_name="_accept_cocontracting",
        ),
        migrations.RenameField(
            model_name="tender",
            old_name="siae_detail_cocontracting_click_count",
            new_name="_siae_detail_cocontracting_click_count",
        ),
        migrations.RenameField(
            model_name="tendersiae",
            old_name="detail_cocontracting_click_date",
            new_name="_detail_cocontracting_click_date",
        ),
        migrations.AlterField(
            model_name="tender",
            name="_accept_cocontracting",
            field=models.BooleanField(default=False, verbose_name="Ouvert à la co-traitance (Archivé)"),
        ),
        migrations.AlterField(
            model_name="tender",
            name="_siae_detail_cocontracting_click_count",
            field=models.IntegerField(
                default=0, verbose_name="Nombre de structures ouvertes à la co-traitance (Archivé)"
            ),
        ),
        migrations.AlterField(
            model_name="tendersiae",
            name="_detail_cocontracting_click_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date de clic sur Répondre en co-traitance (Archivé)"
            ),
        ),
    ]

# Generated by Django 4.1.3 on 2022-11-30 10:42

from django.db import migrations, models


def set_marche_is_useful(apps, schema_editor):
    Tender = apps.get_model("tenders", "tender")

    Tender.objects.filter(is_marche_useful=True).update(scale_marche_useless="0")
    Tender.objects.filter(is_marche_useful=False).update(scale_marche_useless="3")


def set_marche_is_useful_reverse(apps, schema_editor):
    Tender = apps.get_model("tenders", "tender")

    Tender.objects.filter(scale_marche_useless__in=["0", "1"]).update(is_marche_useful=True)
    Tender.objects.filter(scale_marche_useless__in=["2", "3"]).update(is_marche_useful=False)


class Migration(migrations.Migration):

    dependencies = [
        ("tenders", "0034_tender_siae_transactioned"),
    ]

    operations = [
        migrations.AddField(
            model_name="tender",
            name="scale_marche_useless",
            field=models.CharField(
                choices=[("0", "Non"), ("1", "Peu probablement"), ("2", "Très probablement"), ("3", "Oui")],
                default="0",
                help_text="Q°1. Si le Marché de l'inclusion n'existait pas, auriez-vous fait appel à des prestataires inclusifs pour ce besoin ?",  # noqa
                max_length=2,
                verbose_name="Utilité du marché de l'inclusion",
            ),
        ),
        migrations.RunPython(set_marche_is_useful, reverse_code=set_marche_is_useful_reverse),
        migrations.RemoveField(
            model_name="tender",
            name="is_marche_useful",
        ),
    ]

# Generated by Django 4.0.2 on 2022-04-04 14:42

from django.db import migrations, models


AMOUNT_RANGE_0 = "<25K"
AMOUNT_RANGE_1 = "<100K"
AMOUNT_RANGE_2 = "<1M"
AMOUNT_RANGE_3 = "<5M"
AMOUNT_RANGE_4 = ">5M"


def update_amount(apps, schema_editor):
    Tender = apps.get_model("tenders", "Tender")
    tenders = Tender.objects.all()
    for t in tenders:
        amount = t.amount
        if amount:
            amount = int(amount)
            if amount < 25000:
                t.amount = AMOUNT_RANGE_0
            elif amount < 100000:
                t.amount = AMOUNT_RANGE_1
            elif amount < 1000000:
                t.amount = AMOUNT_RANGE_2
            elif amount < 5000000:
                t.amount = AMOUNT_RANGE_3
            else:
                t.amount = AMOUNT_RANGE_4
            t.save()


def reverse_update_amount(apps, schema_editor):
    Tender = apps.get_model("tenders", "Tender")
    tenders = Tender.objects.all()
    for t in tenders:
        amount = t.amount
        if amount:
            if amount == AMOUNT_RANGE_0:
                t.amount = 24999
            elif amount == AMOUNT_RANGE_1:
                t.amount = 99999
            elif amount == AMOUNT_RANGE_2:
                t.amount = 999999
            elif amount == AMOUNT_RANGE_3:
                t.amount = 4999999
            elif amount == AMOUNT_RANGE_4:
                t.amount = 9999999
            t.save()


class Migration(migrations.Migration):
    # atomic = False
    dependencies = [
        ("tenders", "0005_remove_tender_siae_found_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tender",
            name="amount",
            field=models.CharField(
                blank=True,
                choices=[
                    ("<25K", "0-25K €"),
                    ("<100K", "25K-100K €"),
                    ("<1M", "100K-1M €"),
                    ("<5M", "1M-5M €"),
                    (">5M", "> 5M €"),
                ],
                max_length=9,
                null=True,
                verbose_name="Montant du marché",
            ),
        ),
        migrations.RunPython(code=update_amount, reverse_code=reverse_update_amount),
    ]

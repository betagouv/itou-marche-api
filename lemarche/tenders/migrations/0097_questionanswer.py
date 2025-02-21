# Generated by Django 5.1.6 on 2025-02-21 08:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("siaes", "0084_remove_historicalsiae_presta_type_and_more"),
        ("tenders", "0096_tender_email_sent_for_modification_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer", models.TextField()),
                (
                    "question",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tenders.tenderquestion"),
                ),
                ("siae", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="siaes.siae")),
            ],
            options={
                "verbose_name": "Réponse à la question",
                "verbose_name_plural": "Réponses au questions",
            },
        ),
    ]

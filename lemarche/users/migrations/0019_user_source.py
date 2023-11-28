# Generated by Django 4.0.7 on 2022-09-21 14:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0018_user_tender_list_last_seen_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="source",
            field=models.CharField(
                choices=[
                    ("SIGNUP_FORM", "Formulaire d'inscription"),
                    ("TENDER_FORM", "Formulaire de dépôt de besoin"),
                    ("DJANGO_ADMIN", "Admin Django"),
                ],
                default="SIGNUP_FORM",
                max_length=20,
            ),
        ),
    ]

# Generated by Django 4.2.2 on 2023-08-31 09:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0007_conversation_sender_first_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="validated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Date de validation"),
        ),
    ]

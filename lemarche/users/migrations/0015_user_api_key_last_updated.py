# Generated by Django 4.0.2 on 2022-03-19 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_create_cache_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="api_key_last_updated",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date de dernière mise à jour de la clé API"
            ),
        ),
    ]

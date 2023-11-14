# Generated by Django 4.0.2 on 2022-03-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0049_siaegroup"),
    ]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="groups",
            field=models.ManyToManyField(
                blank=True, related_name="siaes", to="siaes.SiaeGroup", verbose_name="Groupements"
            ),
        ),
    ]

# Generated by Django 3.2.8 on 2021-11-04 14:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sectors", "0002_sector"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sector",
            options={
                "ordering": ["name"],
                "verbose_name": "Secteur d'activité",
                "verbose_name_plural": "Secteurs d'activité",
            },
        ),
        migrations.AlterModelOptions(
            name="sectorgroup",
            options={
                "ordering": ["name"],
                "verbose_name": "Groupe de secteurs d'activité",
                "verbose_name_plural": "Groupes de secteurs d'activité",
            },
        ),
    ]

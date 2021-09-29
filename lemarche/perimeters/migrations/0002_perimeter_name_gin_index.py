# Generated by Django 3.2.7 on 2021-09-29 12:18

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("perimeters", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="perimeter",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name"], name="perimeters_name_gin_trgm", opclasses=["gin_trgm_ops"]
            ),
        ),
    ]

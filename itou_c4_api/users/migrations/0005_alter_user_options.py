# Generated by Django 3.2.1 on 2021-06-10 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_auto_20210607_1604"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "user", "verbose_name_plural": "users"},
        ),
    ]

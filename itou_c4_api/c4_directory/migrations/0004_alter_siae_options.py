# Generated by Django 3.2.1 on 2021-06-02 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("c4_directory", "0003_alter_siae_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="siae",
            options={"ordering": ["name"], "permissions": [("access_api", "Can acces the API")]},
        ),
    ]

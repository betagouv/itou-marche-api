# Generated by Django 3.2.1 on 2021-06-07 16:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_user_api_key"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={},
        ),
        migrations.RemoveField(
            model_name="user",
            name="username",
        ),
    ]

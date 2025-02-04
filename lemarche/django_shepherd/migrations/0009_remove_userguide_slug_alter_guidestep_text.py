# Generated by Django 4.2.17 on 2025-02-04 14:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_shepherd", "0008_alter_userguide_guided_users"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userguide",
            name="slug",
        ),
        migrations.AlterField(
            model_name="guidestep",
            name="text",
            field=models.TextField(blank=True, verbose_name="Contenu text de l'étape"),
        ),
    ]

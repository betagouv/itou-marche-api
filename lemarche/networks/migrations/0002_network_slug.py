# Generated by Django 3.2.7 on 2021-09-08 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('networks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='network',
            name='slug',
            field=models.SlugField(max_length=255, null=True, verbose_name='Slug'),
        ),
    ]

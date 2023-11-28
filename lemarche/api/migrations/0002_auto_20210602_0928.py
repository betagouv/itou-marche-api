# Generated by Django 3.2.1 on 2021-06-02 09:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sector",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("lft", models.IntegerField()),
                ("lvl", models.IntegerField()),
                ("rgt", models.IntegerField()),
                ("root", models.IntegerField(blank=True, null=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to="api.sector"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AlterModelOptions(
            name="siae",
            options={"ordering": ["name"], "permissions": [("access_api", "Can acces the API")]},
        ),
        migrations.RenameField(
            model_name="siae",
            old_name="created_at",
            new_name="createdat",
        ),
        migrations.AddField(
            model_name="siae",
            name="city",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="siae",
            name="department",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="siae",
            name="email",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="siae",
            name="phone",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="siae",
            name="post_code",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="siae",
            name="region",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name="SectorString",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("locale", models.CharField(max_length=255)),
                ("slug", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "translatable",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to="api.sector"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]

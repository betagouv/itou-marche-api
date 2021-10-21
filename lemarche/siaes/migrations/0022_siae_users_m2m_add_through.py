# Generated by Django 3.2.8 on 2021-10-21 06:57

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("siaes", "0021_siae_image_name"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="SiaeUser",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                            ),
                        ),
                        (
                            "siae",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE, to="siaes.siae", verbose_name="Structure"
                            ),
                        ),
                        (
                            "user",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to=settings.AUTH_USER_MODEL,
                                verbose_name="Utilisateur",
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name="siae",
                    name="users",
                    field=models.ManyToManyField(
                        blank=True,
                        related_name="siaes",
                        through="siaes.SiaeUser",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Gestionnaires",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE siaes_siae_users RENAME TO siaes_siaeuser",
                    reverse_sql="ALTER TABLE siaes_siaeuser RENAME TO siaes_siae_users",
                ),
                migrations.RunSQL(
                    sql="ALTER SEQUENCE siaes_siae_users_id_seq RENAME TO siaes_siaeuser_id_seq",
                    reverse_sql="ALTER SEQUENCE siaes_siaeuser_id_seq RENAME TO siaes_siae_users_id_seq",
                ),
            ],
        )
    ]

# Generated by Django 3.2.8 on 2021-11-19 10:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_user_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="c4_naf",
            field=models.CharField(blank=True, default="", max_length=5, verbose_name="Naf"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="c4_phone_prefix",
            field=models.CharField(blank=True, default="", max_length=20, verbose_name="Indicatif international"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="c4_siret",
            field=models.CharField(blank=True, default="", max_length=14, verbose_name="Siret ou Siren"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="c4_time_zone",
            field=models.CharField(blank=True, default="", max_length=150, verbose_name="Fuseau"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="c4_website",
            field=models.URLField(blank=True, default="", verbose_name="Site web"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="company_name",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Nom de l'entreprise"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="image_name",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Nom de l'image"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="image_url",
            field=models.URLField(blank=True, default="", max_length=500, verbose_name="Lien vers l'image"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="kind",
            field=models.CharField(
                blank=True,
                choices=[
                    ("SIAE", "Structure"),
                    ("BUYER", "Acheteur"),
                    ("PARTNER", "Partenaire"),
                    ("ADMIN", "Administrateur"),
                ],
                default="",
                max_length=20,
                verbose_name="Type",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, default="", max_length=20, verbose_name="Téléphone"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="position",
            field=models.CharField(blank=True, default="", max_length=255, verbose_name="Poste"),
            preserve_default=False,
        ),
    ]

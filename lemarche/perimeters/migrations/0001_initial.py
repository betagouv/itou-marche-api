# Generated by Django 3.2.7 on 2021-09-29 08:33

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Perimeter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=255, verbose_name="Nom")),
                ("slug", models.SlugField(max_length=255, unique=True, verbose_name="Slug")),
                (
                    "kind",
                    models.CharField(
                        choices=[("CITY", "Commune"), ("DEPARTMENT", "Département"), ("REGION", "Région")],
                        max_length=20,
                        verbose_name="Type de périmètre",
                    ),
                ),
                ("insee_code", models.CharField(max_length=5, unique=True, verbose_name="Code INSEE")),
                (
                    "coords",
                    django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
                ),
                (
                    "post_codes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=5),
                        blank=True,
                        null=True,
                        size=None,
                        verbose_name="Codes postaux",
                    ),
                ),
                (
                    "department_code",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("01", "01 - Ain"),
                            ("02", "02 - Aisne"),
                            ("03", "03 - Allier"),
                            ("04", "04 - Alpes-de-Haute-Provence"),
                            ("05", "05 - Hautes-Alpes"),
                            ("06", "06 - Alpes-Maritimes"),
                            ("07", "07 - Ardèche"),
                            ("08", "08 - Ardennes"),
                            ("09", "09 - Ariège"),
                            ("10", "10 - Aube"),
                            ("11", "11 - Aude"),
                            ("12", "12 - Aveyron"),
                            ("13", "13 - Bouches-du-Rhône"),
                            ("14", "14 - Calvados"),
                            ("15", "15 - Cantal"),
                            ("16", "16 - Charente"),
                            ("17", "17 - Charente-Maritime"),
                            ("18", "18 - Cher"),
                            ("19", "19 - Corrèze"),
                            ("2A", "2A - Corse-du-Sud"),
                            ("2B", "2B - Haute-Corse"),
                            ("21", "21 - Côte-d'Or"),
                            ("22", "22 - Côtes-d'Armor"),
                            ("23", "23 - Creuse"),
                            ("24", "24 - Dordogne"),
                            ("25", "25 - Doubs"),
                            ("26", "26 - Drôme"),
                            ("27", "27 - Eure"),
                            ("28", "28 - Eure-et-Loir"),
                            ("29", "29 - Finistère"),
                            ("30", "30 - Gard"),
                            ("31", "31 - Haute-Garonne"),
                            ("32", "32 - Gers"),
                            ("33", "33 - Gironde"),
                            ("34", "34 - Hérault"),
                            ("35", "35 - Ille-et-Vilaine"),
                            ("36", "36 - Indre"),
                            ("37", "37 - Indre-et-Loire"),
                            ("38", "38 - Isère"),
                            ("39", "39 - Jura"),
                            ("40", "40 - Landes"),
                            ("41", "41 - Loir-et-Cher"),
                            ("42", "42 - Loire"),
                            ("43", "43 - Haute-Loire"),
                            ("44", "44 - Loire-Atlantique"),
                            ("45", "45 - Loiret"),
                            ("46", "46 - Lot"),
                            ("47", "47 - Lot-et-Garonne"),
                            ("48", "48 - Lozère"),
                            ("49", "49 - Maine-et-Loire"),
                            ("50", "50 - Manche"),
                            ("51", "51 - Marne"),
                            ("52", "52 - Haute-Marne"),
                            ("53", "53 - Mayenne"),
                            ("54", "54 - Meurthe-et-Moselle"),
                            ("55", "55 - Meuse"),
                            ("56", "56 - Morbihan"),
                            ("57", "57 - Moselle"),
                            ("58", "58 - Nièvre"),
                            ("59", "59 - Nord"),
                            ("60", "60 - Oise"),
                            ("61", "61 - Orne"),
                            ("62", "62 - Pas-de-Calais"),
                            ("63", "63 - Puy-de-Dôme"),
                            ("64", "64 - Pyrénées-Atlantiques"),
                            ("65", "65 - Hautes-Pyrénées"),
                            ("66", "66 - Pyrénées-Orientales"),
                            ("67", "67 - Bas-Rhin"),
                            ("68", "68 - Haut-Rhin"),
                            ("69", "69 - Rhône"),
                            ("70", "70 - Haute-Saône"),
                            ("71", "71 - Saône-et-Loire"),
                            ("72", "72 - Sarthe"),
                            ("73", "73 - Savoie"),
                            ("74", "74 - Haute-Savoie"),
                            ("75", "75 - Paris"),
                            ("76", "76 - Seine-Maritime"),
                            ("77", "77 - Seine-et-Marne"),
                            ("78", "78 - Yvelines"),
                            ("79", "79 - Deux-Sèvres"),
                            ("80", "80 - Somme"),
                            ("81", "81 - Tarn"),
                            ("82", "82 - Tarn-et-Garonne"),
                            ("83", "83 - Var"),
                            ("84", "84 - Vaucluse"),
                            ("85", "85 - Vendée"),
                            ("86", "86 - Vienne"),
                            ("87", "87 - Haute-Vienne"),
                            ("88", "88 - Vosges"),
                            ("89", "89 - Yonne"),
                            ("90", "90 - Territoire de Belfort"),
                            ("91", "91 - Essonne"),
                            ("92", "92 - Hauts-de-Seine"),
                            ("93", "93 - Seine-Saint-Denis"),
                            ("94", "94 - Val-de-Marne"),
                            ("95", "95 - Val-d'Oise"),
                            ("971", "971 - Guadeloupe"),
                            ("972", "972 - Martinique"),
                            ("973", "973 - Guyane"),
                            ("974", "974 - La Réunion"),
                            ("975", "975 - Saint-Pierre-et-Miquelon"),
                            ("976", "976 - Mayotte"),
                            ("977", "977 - Saint-Barthélémy"),
                            ("978", "978 - Saint-Martin"),
                            ("984", "984 - Terres australes et antarctiques françaises"),
                            ("986", "986 - Wallis-et-Futuna"),
                            ("987", "987 - Polynésie française"),
                            ("988", "988 - Nouvelle-Calédonie"),
                            ("989", "989 - Île de Clipperton"),
                        ],
                        max_length=3,
                        null=True,
                        verbose_name="Département (code)",
                    ),
                ),
                ("population", models.IntegerField(blank=True, null=True, verbose_name="Population")),
                (
                    "region_code",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("01", "Guadeloupe"),
                            ("02", "Martinique"),
                            ("03", "Guyane"),
                            ("04", "La Réunion"),
                            ("06", "Mayotte"),
                            ("11", "Île-de-France"),
                            ("24", "Centre-Val de Loire"),
                            ("27", "Bourgogne-Franche-Comté"),
                            ("28", "Normandie"),
                            ("32", "Hauts-de-France"),
                            ("44", "Grand Est"),
                            ("52", "Pays de la Loire"),
                            ("53", "Bretagne"),
                            ("75", "Nouvelle-Aquitaine"),
                            ("76", "Occitanie"),
                            ("84", "Auvergne-Rhône-Alpes"),
                            ("93", "Provence-Alpes-Côte d'Azur"),
                            ("94", "Corse"),
                            ("97", "Collectivités d'outre-mer"),
                        ],
                        max_length=2,
                        null=True,
                        verbose_name="Région (code)",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Date de modification")),
            ],
            options={
                "verbose_name": "Périmètre",
                "verbose_name_plural": "Périmètres",
            },
        ),
    ]

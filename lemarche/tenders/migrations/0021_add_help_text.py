# Generated by Django 4.0.6 on 2022-08-04 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sectors", "0003_sector_sectorgroup_ordering"),
        ("perimeters", "0005_alter_perimeter_post_codes"),
        ("tenders", "0020_tender_accept_share_amount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partnersharetender",
            name="amount_in",
            field=models.CharField(
                blank=True,
                choices=[
                    ("0-1K", "0-1000 €"),
                    ("1-5K", "1000-5K €"),
                    ("5-10K", "5K-10K €"),
                    ("10-15K", "10K-15K €"),
                    ("15-20K", "15K-20K €"),
                    ("20-30K", "20K-30K €"),
                    ("30-50K", "30K-50K €"),
                    ("50-100K", "50K-100K €"),
                    ("100-150K", "100K-150K €"),
                    ("150-250K", "150K-250K €"),
                    ("250-500K", "250K-500K €"),
                    ("500-750K", "500K-750K €"),
                    ("750K-1M", "750K-1M €"),
                    (">1M", "> 1M €"),
                ],
                max_length=9,
                null=True,
                verbose_name="Montant du marché limite",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="amount",
            field=models.CharField(
                blank=True,
                choices=[
                    ("0-1K", "0-1000 €"),
                    ("1-5K", "1000-5K €"),
                    ("5-10K", "5K-10K €"),
                    ("10-15K", "10K-15K €"),
                    ("15-20K", "15K-20K €"),
                    ("20-30K", "20K-30K €"),
                    ("30-50K", "30K-50K €"),
                    ("50-100K", "50K-100K €"),
                    ("100-150K", "100K-150K €"),
                    ("150-250K", "150K-250K €"),
                    ("250-500K", "250K-500K €"),
                    ("500-750K", "500K-750K €"),
                    ("750K-1M", "750K-1M €"),
                    (">1M", "> 1M €"),
                ],
                help_text="Sélectionnez le montant reservé aux structures d'insertion et/ou de handicap",
                max_length=9,
                null=True,
                verbose_name="Montant du marché",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="constraints",
            field=models.TextField(
                blank=True,
                help_text="Renseignez les contraintes liées à votre besoin",
                verbose_name="Contraintes techniques spécifiques",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="contact_email",
            field=models.EmailField(
                blank=True,
                help_text="Renseignez votre adresse e-mail professionnelle",
                max_length=254,
                verbose_name="E-mail du contact",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="contact_phone",
            field=models.CharField(
                blank=True,
                help_text="Renseignez votre numéro de téléphone professionnel",
                max_length=20,
                verbose_name="Téléphone du contact",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="deadline_date",
            field=models.DateField(
                help_text="Sélectionnez la date jusqu'à laquelle vous acceptez des réponses",
                verbose_name="Date de clôture des réponses",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="description",
            field=models.TextField(
                blank=True, help_text="Décrivez en quelques mots votre besoin", verbose_name="Description du besoin"
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="external_link",
            field=models.URLField(
                blank=True,
                help_text="Ajoutez ici l'URL de votre appel d'offres",
                verbose_name="Lien vers l'appel d'offres",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="perimeters",
            field=models.ManyToManyField(
                blank=True,
                help_text="Ajoutez un ou plusieurs lieux d'exécutions",
                related_name="tenders",
                to="perimeters.perimeter",
                verbose_name="Lieux d'exécution",
            ),
        ),
        migrations.AlterField(
            model_name="tender",
            name="sectors",
            field=models.ManyToManyField(
                help_text="Sélectionnez un ou plusieurs secteurs d'activité",
                related_name="tenders",
                to="sectors.sector",
                verbose_name="Secteurs d'activité",
            ),
        ),
    ]

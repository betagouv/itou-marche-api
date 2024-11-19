# Generated by Django 4.2.15 on 2024-10-23 10:31

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0013_alter_articlepage_intro_alter_faqpage_intro"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="sub_header_custom_message",
            field=wagtail.fields.StreamField(
                [("message", 0)],
                blank=True,
                block_lookup={0: ("wagtail.blocks.RichTextBlock", (), {"label": "Message personnalisé du bandeau"})},
                help_text="Contenu affiché dans le bandeau sous l'en-tête.",
                null=True,
                verbose_name="Message personnalisé du bandeau",
            ),
        ),
    ]

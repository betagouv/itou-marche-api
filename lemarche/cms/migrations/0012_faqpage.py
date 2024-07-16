# Generated by Django 4.2.13 on 2024-07-16 17:55

import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0011_infocard"),
    ]

    operations = [
        migrations.CreateModel(
            name="FAQPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("intro", models.TextField(blank=True, null=True, verbose_name="Introduction")),
                (
                    "faqs",
                    wagtail.fields.StreamField(
                        [
                            (
                                "faq_group",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "group_title",
                                            wagtail.blocks.CharBlock(
                                                help_text="Le titre du groupe de questions-réponses.", required=True
                                            ),
                                        ),
                                        (
                                            "faqs",
                                            wagtail.blocks.ListBlock(
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "question",
                                                            wagtail.blocks.CharBlock(
                                                                help_text="La question fréquemment posée.",
                                                                required=True,
                                                            ),
                                                        ),
                                                        (
                                                            "answer",
                                                            wagtail.blocks.RichTextBlock(
                                                                help_text="La réponse à la question.", required=True
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("categories", modelcluster.fields.ParentalManyToManyField(blank=True, to="cms.articlecategory")),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "FAQ Page",
                "verbose_name_plural": "FAQ Pages",
            },
            bases=("wagtailcore.page",),
        ),
    ]

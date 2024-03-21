# common blocks
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class CallToAction(blocks.StructBlock):
    cta_id = blocks.CharBlock(
        label="slug",
        help_text="id du call to action (pour le suivi)",
    )
    cta_href = blocks.CharBlock(
        label="Lien du call to action",
    )
    cta_text = blocks.CharBlock(label="Titre du call to action")
    cta_icon = blocks.CharBlock(
        label="Icone du call to action",
        help_text='Bibliothèque <a href="https://remixicon.com/" target="_blanck">remixicon</a>',
        required=False,
    )


class StatsWebsite(blocks.StructBlock):
    """A stats of marche website section"""

    # def get_context(self, value, parent_context=None):
    #     context = super().get_context(value, parent_context)
    #     return context

    class Meta:
        template = "cms/streams/stats_website.html"
        icon = "pen"
        label = "Statistique du marche"


class TendersTestimonialsSection(blocks.StructBlock):
    title = blocks.CharBlock(default="Ils ont publié un besoin sur le marché", required=True, max_length=120)

    class Meta:
        template = "cms/streams/section_they_publish_tenders.html"
        icon = "pen"
        label = "Ils ont publié un besoin sur le marché"


class TendersStudiesCasesSection(blocks.StructBlock):
    title = blocks.CharBlock(default="100% des besoins ont reçu des réponses en 24h", required=True, max_length=120)
    subtitle = blocks.CharBlock(default="Gagnez du temps en utilisant le marché.", required=True, max_length=120)

    class Meta:
        template = "cms/streams/section_studies_cases_tenders.html"
        icon = "pen"
        label = "Etude de cas"


class OurSiaesSection(blocks.StructBlock):
    """An external or internal URL."""

    title = blocks.CharBlock(
        default="Les prestataires inclusifs, des partenaires d'excellence", required=True, max_length=60
    )

    subtitle = blocks.RichTextBlock(
        default="""
            Faire appel à nos 8500 prestataires inclusifs, c'est la garantie d'être accompagné
            par des professionnels reconnus et certifiés dans leur domaine.
        """,
        required=True,
        features=["bold", "italic"],
    )
    # constats = blocks.StreamBlock(
    #     [
    #         (
    #             "constat",
    #             ConstatBlock(),
    #         )
    #     ],
    #     min_num=1,
    #     max_num=3,
    # )

    class Meta:
        template = "cms/streams/section_our_siaes.html"
        icon = "pen"
        label = "Section nos structures"


class OurRessourcesSection(blocks.StructBlock):
    title = blocks.CharBlock(default="Nos ressources", required=True, max_length=120)

    class Meta:
        template = "cms/streams/section_our_ressources.html"
        icon = "pen"
        label = "Nos ressources"


class WhatFindHereSection(blocks.StructBlock):
    title = blocks.CharBlock(default="Sur le marché", required=True, max_length=120)

    class Meta:
        template = "cms/streams/section_what_find_here.html"
        icon = "pen"
        label = "Avantages marché"


class ImageWithLink(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    external_link = blocks.URLBlock(required=True)

    class Meta:
        template = "cms/streams/image_with_link.html"
        label = "Image avec lien externe"


class OurPartnersSection(blocks.StructBlock):
    title = blocks.CharBlock(default="Les partenaires du marché", required=True, max_length=120)
    images_with_link = blocks.StreamBlock([("images", ImageWithLink())], min_num=8, max_num=8)

    class Meta:
        template = "cms/streams/section_our_partners.html"
        icon = "pen"
        label = "Nos partenaires"


class FeatureBlock(blocks.StructBlock):
    """An external or internal URL."""

    title = blocks.CharBlock(required=True, max_length=60)
    subtitle = blocks.RichTextBlock(
        required=True,
        features=["bold", "italic"],
    )

    image = ImageChooserBlock(required=True)
    url = blocks.URLBlock(required=True)

    class Meta:
        template = "cms/streams/card_feature.html"
        icon = "pen"
        label = "Section nos structures"


class OurFeaturesSection(blocks.StructBlock):
    """An external or internal URL."""

    title = blocks.CharBlock(
        default="Une solution complète pour vos achats socialement responsables", required=True, max_length=120
    )

    constats = blocks.StreamBlock(
        [
            (
                "feature",
                FeatureBlock(),
            )
        ],
        min_num=1,
    )

    class Meta:
        template = "cms/streams/section_our_features.html"
        icon = "pen"
        label = "Nos fonctionnalités"


class WhyCallSiaes(blocks.StructBlock):
    """Why call siaes"""

    title = blocks.CharBlock(default="Pourquoi faire appel à un prestataire inclusif ?", required=True, max_length=120)

    class Meta:
        template = "cms/streams/section_why_call_siaes.html"
        icon = "pen"
        label = "Pourquoi faire appel à un prestataire inclusif ?"

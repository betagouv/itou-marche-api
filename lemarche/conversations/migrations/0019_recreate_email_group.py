# Generated by Django 4.2.17 on 2025-01-15 11:06

from django.db import migrations


def delete_email_groups(apps, schema_editor):
    # Get the model
    EmailGroup = apps.get_model("conversations", "EmailGroup")
    # Delete all email groups
    EmailGroup.objects.all().delete()


def create_email_groups(apps, schema_editor):
    # Get the model
    EmailGroup = apps.get_model("conversations", "EmailGroup")

    # Create email groups
    email_groups = [
        {
            "display_name": "Structure(s) intéressée(s)",
            "description": "En désactivant cette option, vous ne serez plus averti par email lorsque des fournisseurs s'intéressent à votre besoin, ce qui pourrait vous faire perdre des opportunités de collaboration rapide et efficace.",
            "relevant_user_kind": "BUYER",
            "can_be_unsubscribed": True,
        },
        {
            "display_name": "Communication marketing",
            "description": "En désactivant cette option, vous ne recevrez plus par email nos newsletters, enquêtes, invitations à des webinaires et Open Labs, ce qui pourrait vous priver d'informations utiles et de moments d'échange exclusifs.",
            "relevant_user_kind": "BUYER",
            "can_be_unsubscribed": True,
        },
        {
            "display_name": "Opportunités commerciales",
            "description": "En désactivant cette option, vous ne recevrez plus par email les demandes de devis et les appels d'offres spécialement adaptés à votre activité, ce qui pourrait vous faire manquer des opportunités importantes pour votre entreprise.",
            "relevant_user_kind": "SIAE",
            "can_be_unsubscribed": True,
        },
        {
            "display_name": "Demandes de mise en relation",
            "description": "En désactivant cette option, vous ne recevrez plus par email les demandes de mise en relation de clients intéressés par votre structure, ce qui pourrait vous faire perdre des opportunités précieuses de collaboration et de développement.",
            "relevant_user_kind": "SIAE",
            "can_be_unsubscribed": True,
        },
        {
            "display_name": "Communication marketing",
            "description": "En désactivant cette option, vous ne recevrez plus par email nos newsletters, enquêtes, invitations aux webinaires et Open Labs, ce qui pourrait vous faire passer à côté d’informations clés, de ressources utiles et d’événements exclusifs.",
            "relevant_user_kind": "SIAE",
            "can_be_unsubscribed": True,
        },
    ]

    for group in email_groups:
        EmailGroup.objects.create(**group)


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0018_conversation_is_anonymized"),
    ]

    operations = [
        migrations.RunPython(delete_email_groups, migrations.RunPython.noop),
        migrations.RunPython(create_email_groups, migrations.RunPython.noop),
    ]

# Generated by Django 4.2.2 on 2023-08-31 09:55

from django.db import migrations, models


def populate_validated_at_for_already_sent_conversations(apps, schema_editor):
    Conversation = apps.get_model("conversations", "Conversation")

    for conversation in Conversation.objects.filter(validated_at__isnull=True):
        conversation.validated_at = conversation.created_at
        conversation.save()


class Migration(migrations.Migration):
    dependencies = [
        ("conversations", "0008_conversation_sender_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="validated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Date de validation"),
        ),
        migrations.RunPython(populate_validated_at_for_already_sent_conversations),
    ]

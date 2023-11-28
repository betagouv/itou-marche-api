# Generated by Django 3.2.7 on 2021-10-04 20:04

from uuid import uuid4

from django.db import migrations, models
from django.utils.text import slugify


def slugify_name(apps, schema_editor):
    # see Siae.set_slug()
    Siae = apps.get_model("siaes", "Siae")
    all_siae_slugs = []
    for siae in Siae.objects.all().order_by("-is_active"):
        name_slug = f"{slugify(siae.name)[:40]}-{siae.department}"
        if name_slug in all_siae_slugs:
            name_slug += f"-{str(uuid4())[:4]}"
        all_siae_slugs.append(name_slug)
        siae.slug = name_slug
        siae.save()


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0016_siae_contact_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="slug",
            field=models.SlugField(max_length=255, null=True, verbose_name="Slug"),
        ),
        migrations.RunPython(slugify_name),
    ]

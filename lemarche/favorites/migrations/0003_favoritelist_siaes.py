# Generated by Django 3.2.8 on 2021-12-02 15:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siaes", "0038_siae_image_count"),
        ("favorites", "0002_favoriteitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="favoritelist",
            name="siaes",
            field=models.ManyToManyField(
                blank=True,
                related_name="favorite_lists",
                through="favorites.FavoriteItem",
                to="siaes.Siae",
                verbose_name="Structures en favoris",
            ),
        ),
    ]

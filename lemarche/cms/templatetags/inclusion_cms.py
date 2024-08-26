from django import template


register = template.Library()


@register.inclusion_tag("cms/show_article_categories_badges.html")
def show_article_categories_badges(article):
    """display list of article categories"""

    categories = []
    if hasattr(article, "articlepage"):
        categories = article.articlepage.categories.all()

    return {"categories": categories}

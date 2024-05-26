from django.core.cache import cache
from django.conf import settings
from catalog.models import Category


def get_cached_categories():
    if settings.CACHE_ENABLED:
        cache_key = 'categories_list'
        categories = cache.get(cache_key)

        if categories is None:
            categories = list(Category.objects.all())
            cache.set(cache_key, categories)
    else:
        categories = list(Category.objects.all())

    return categories

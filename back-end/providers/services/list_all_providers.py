from providers.models import ServiceProvider


def list_all_providers(*, q=None, category=None):
    providers = ServiceProvider.objects.live().select_related("owner").with_links_and_categories()
    if q:
        providers = providers.matching(q)
    if category:
        providers = providers.in_category(category)
    return providers.order_by("business_name", "id")

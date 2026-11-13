from providers.models import ServiceCategory


def list_categories():
    return ServiceCategory.objects.filter(is_active=True).order_by("name")

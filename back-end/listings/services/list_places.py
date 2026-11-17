from collections import Counter

from listings.services.shared.queries import listed_properties


def list_places():
    """Every state and suburb that currently has a listing, with how many."""
    counts = Counter(listed_properties().values_list("state", "suburb"))
    return [
        {"state": state, "suburb": suburb, "listings": count}
        for (state, suburb), count in sorted(counts.items())
    ]

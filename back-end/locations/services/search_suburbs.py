import csv
from functools import cache
from pathlib import Path

DEFAULT_LIMIT = 50
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "au_suburbs.csv"


@cache
def _suburbs_by_state():
    by_state = {}
    with DATA_FILE.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            by_state.setdefault(row["state"], []).append(
                {"suburb": row["suburb"], "postcode": row["postcode"]}
            )
    return by_state


def search_suburbs(*, state, q=None, limit=None):
    suburbs = _suburbs_by_state().get(state, [])
    terms = (q or "").lower().split()
    matches = [row for row in suburbs if all(term in row["suburb"].lower() for term in terms)]
    typed = " ".join(terms)
    matches.sort(key=lambda row: not row["suburb"].lower().startswith(typed))
    return matches[: limit or DEFAULT_LIMIT]

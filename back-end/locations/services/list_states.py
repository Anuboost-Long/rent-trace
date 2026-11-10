from locations.catalogue import STATES


def list_states():
    return [{"code": code, "name": name} for code, name in STATES]

from django.db import transaction


def send_after_commit(send, *args):
    transaction.on_commit(lambda: send(*args))

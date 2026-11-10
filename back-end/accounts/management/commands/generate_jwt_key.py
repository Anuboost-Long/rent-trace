from getpass import getpass

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.security import signing_keys


class Command(BaseCommand):
    help = (
        "Generate a JWT signing key, randomly (default) or from secret words, "
        "and print it or write it to config/.env."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-words",
            action="store_true",
            help="Build the key from secret words you type (hidden). The same words and "
            "label always give the same key, so you can recreate it later.",
        )
        parser.add_argument(
            "--label",
            default="local",
            help="Environment name mixed into a words-based key, so the same words give a "
            "different key per environment (default: local).",
        )
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write the key into the env file instead of printing it.",
        )
        parser.add_argument(
            "--env-file",
            default=str(settings.BASE_DIR / "config" / ".env"),
            help="Env file to update with --write (default: config/.env).",
        )

    def handle(self, *, from_words, label, write, env_file, **_):
        key = self._key_from_words(label) if from_words else signing_keys.generate_random_key()
        if not write:
            self.stdout.write(key)
            return
        signing_keys.write_env_value(env_file, "JWT_SIGNING_KEY", key)
        self.stdout.write(
            self.style.SUCCESS(
                f"JWT_SIGNING_KEY updated in {env_file}. "
                "Restart the server; everyone has to sign in again."
            )
        )

    def _key_from_words(self, label):
        words = getpass("Secret words (hidden): ")
        problem = signing_keys.words_problem(words)
        if problem:
            raise CommandError(f"{problem} A key made from words is only as strong as the words.")
        if getpass("Type them again: ") != words:
            raise CommandError("The two entries don't match. Nothing was changed.")
        return signing_keys.derive_key_from_words(words, label)

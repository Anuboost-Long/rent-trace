import io
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, override_settings

from accounts.security import signing_keys
from accounts.security.checks import jwt_signing_key_length
from accounts.tests.base import AuthApiTestCase

WORDS = "copper lantern river seventeen"


class GenerateJwtKeyTests(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.env_file = Path(self.directory.name) / ".env"
        self.env_file.write_text(
            "DJANGO_DEBUG=True\nJWT_SIGNING_KEY=old-short-key\nREDIS_URL=redis://x\n"
        )
        os.chmod(self.env_file, 0o600)

    def tearDown(self):
        self.directory.cleanup()

    def run_command(self, *args, typed=None):
        output = io.StringIO()
        with mock.patch(
            "accounts.management.commands.generate_jwt_key.getpass", side_effect=typed or []
        ):
            call_command("generate_jwt_key", *args, "--env-file", str(self.env_file), stdout=output)
        return output.getvalue()

    def env_key(self):
        line = next(
            line
            for line in self.env_file.read_text().splitlines()
            if line.startswith("JWT_SIGNING_KEY=")
        )
        return line.split("=", 1)[1]

    def test_random_keys_are_long_and_unique(self):
        first, second = signing_keys.generate_random_key(), signing_keys.generate_random_key()
        self.assertGreaterEqual(len(first.encode()), signing_keys.MIN_KEY_BYTES)
        self.assertNotEqual(first, second)

    def test_same_words_and_label_give_the_same_key(self):
        local = signing_keys.derive_key_from_words(WORDS, "local")
        self.assertEqual(local, signing_keys.derive_key_from_words(WORDS, "local"))
        self.assertNotEqual(local, signing_keys.derive_key_from_words(WORDS, "production"))
        self.assertNotEqual(local, signing_keys.derive_key_from_words(WORDS + "s", "local"))
        self.assertGreaterEqual(len(local.encode()), signing_keys.MIN_KEY_BYTES)

    def test_weak_words_are_refused(self):
        self.assertIsNotNone(signing_keys.words_problem("one two three"))
        self.assertIsNotNone(signing_keys.words_problem("a b c d"))
        self.assertIsNone(signing_keys.words_problem(WORDS))
        with self.assertRaisesMessage(CommandError, "at least 4 words"):
            self.run_command("--from-words", "--write", typed=["too short"])
        self.assertEqual(self.env_key(), "old-short-key")

    def test_mismatched_words_change_nothing(self):
        with self.assertRaisesMessage(CommandError, "don't match"):
            self.run_command("--from-words", "--write", typed=[WORDS, WORDS + " typo"])
        self.assertEqual(self.env_key(), "old-short-key")

    def test_write_replaces_only_the_key_and_never_prints_it(self):
        output = self.run_command("--write")
        key = self.env_key()
        self.assertNotEqual(key, "old-short-key")
        self.assertNotIn(key, output)
        self.assertEqual(
            [line.split("=")[0] for line in self.env_file.read_text().splitlines()],
            ["DJANGO_DEBUG", "JWT_SIGNING_KEY", "REDIS_URL"],
        )
        self.assertEqual(self.env_file.stat().st_mode & 0o777, 0o600)

    def test_words_key_written_matches_derivation(self):
        self.run_command("--from-words", "--label", "staging", "--write", typed=[WORDS, WORDS])
        self.assertEqual(self.env_key(), signing_keys.derive_key_from_words(WORDS, "staging"))

    def test_without_write_the_key_is_printed_and_file_untouched(self):
        output = self.run_command()
        self.assertGreaterEqual(len(output.strip()), signing_keys.MIN_KEY_BYTES)
        self.assertEqual(self.env_key(), "old-short-key")

    def test_missing_key_line_is_added(self):
        self.env_file.write_text("DJANGO_DEBUG=True\n")
        self.run_command("--write")
        self.assertGreaterEqual(len(self.env_key().encode()), signing_keys.MIN_KEY_BYTES)

    @override_settings(JWT_SIGNING_KEY="only-twenty-bytes!!!")
    def test_system_check_warns_about_a_short_key(self):
        self.assertEqual([w.id for w in jwt_signing_key_length(None)], ["accounts.W001"])

    @override_settings(JWT_SIGNING_KEY="x" * 64)
    def test_system_check_is_quiet_for_a_long_key(self):
        self.assertEqual(jwt_signing_key_length(None), [])


class SigningKeyEndpointTests(AuthApiTestCase):
    def test_returns_a_new_random_key_without_authentication(self):
        first = self.client.get("/api/auth/signing-key/")
        second = self.client.get("/api/auth/signing-key/")
        self.assertEqual((first.status_code, second.status_code), (200, 200))
        self.assertGreaterEqual(first.data["length_bytes"], signing_keys.MIN_KEY_BYTES)
        self.assertEqual(first.data["length_bytes"], len(first.data["key"].encode()))
        self.assertNotEqual(first.data["key"], second.data["key"])
        self.assertEqual(first["Cache-Control"], "no-store")

    def test_does_not_change_the_live_key(self):
        live = settings.JWT_SIGNING_KEY
        self.client.get("/api/auth/signing-key/")
        self.assertEqual(settings.JWT_SIGNING_KEY, live)

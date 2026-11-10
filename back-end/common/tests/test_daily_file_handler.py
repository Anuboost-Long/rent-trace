import logging
import tempfile
from datetime import date
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from common.daily_file_handler import DailyFileHandler


class DailyFileHandlerTests(SimpleTestCase):
    def test_each_day_gets_its_own_dated_file(self):
        with tempfile.TemporaryDirectory() as directory:
            handler = DailyFileHandler(directory, "api")
            logger = logging.Logger("daily-test")
            logger.addHandler(handler)

            for day in (date(2026, 11, 9), date(2026, 11, 10)):
                with mock.patch("common.daily_file_handler.date") as fake_date:
                    fake_date.today.return_value = day
                    logger.warning("on %s", day)
            handler.close()

            files = sorted(path.name for path in Path(directory).iterdir())
            self.assertEqual(files, ["api-20261109.log", "api-20261110.log"])
            self.assertIn("2026-11-10", (Path(directory) / "api-20261110.log").read_text())

import logging
from datetime import date
from pathlib import Path


class DailyFileHandler(logging.FileHandler):
    """Writes to <directory>/<prefix>-YYYYMMDD.log and starts a new file each day."""

    def __init__(self, directory, prefix, encoding="utf-8"):
        self.directory = Path(directory)
        self.prefix = prefix
        self.directory.mkdir(parents=True, exist_ok=True)
        super().__init__(self.path_for_today(), encoding=encoding, delay=True)

    def path_for_today(self):
        return str(self.directory / f"{self.prefix}-{date.today():%Y%m%d}.log")

    def emit(self, record):
        today = self.path_for_today()
        if today != self.baseFilename:
            self.close()
            self.baseFilename = today
        super().emit(record)

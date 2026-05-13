"""Один `.env` в каталоге проекта (рядом с этим файлом)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


class Config:
    def __init__(self) -> None:
        self.API_URL = (os.environ.get("API_URL") or "").strip()
        self.SERIAL_PORT = (os.environ.get("SERIAL_PORT") or "").strip()

    def __str__(self) -> str:
        return f"API_URL={self.API_URL!r}, SERIAL_PORT={self.SERIAL_PORT!r}"

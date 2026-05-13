"""
Серверный скрипт чтения сканера по последовательному порту и отправки кодов на HTTP API.

Переменные в одном файле `.env` в каталоге приложения (там же, где `main.py`). Уже заданные в окружении переменные не перезаписываются.
  API_URL        — URL для POST JSON {"scanned_code": "..."} (обязательно)
  SERIAL_PORT    — устройство, например /dev/ttyUSB0 или COM3 (обязательно)
  SERIAL_BAUD    — скорость, по умолчанию 9600
  HTTP_TIMEOUT   — таймаут запроса в секундах, по умолчанию 15
  HTTP_VERIFY_SSL — true/false, по умолчанию true
  SERIAL_RECONNECT_SEC — пауза перед повторным открытием порта, по умолчанию 3
  LOG_LEVEL      — DEBUG/INFO/WARNING/ERROR, по умолчанию INFO
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import time

import requests
import serial

from config import Config

logger = logging.getLogger("scanner")

_shutdown = False


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off")

def _setup_logging() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        stream=sys.stdout,
        force=True,
    )


def _on_signal(signum: int, _frame) -> None:
    global _shutdown
    _shutdown = True
    logger.info("Получен сигнал %s, завершение после текущей итерации…", signum)


def _send_code(api_url: str, code: str, timeout: float, verify_ssl: bool) -> None:
    payload = {"scanned_code": code}
    try:
        response = requests.post(
            api_url,
            json=payload,
            timeout=timeout,
            verify=verify_ssl,
        )
        if response.ok:
            logger.info("Отправлено на API, HTTP %s", response.status_code)
        else:
            body = (response.text or "")[:500]
            logger.error(
                "API ответил %s: %s",
                response.status_code,
                body or "(пустое тело)",
            )
    except requests.RequestException as exc:
        logger.error("Ошибка HTTP при отправке кода: %s", exc)


def run() -> None:
    global _shutdown

    _setup_logging()

    cfg = Config()
    api_url = cfg.API_URL
    serial_port = cfg.SERIAL_PORT
    if not api_url:
        logger.error("В .env или окружении нет API_URL.")
        sys.exit(1)
    if not serial_port:
        logger.error("В .env или окружении нет SERIAL_PORT.")
        sys.exit(1)

    baud = int(os.environ.get("SERIAL_BAUD", "9600"))
    http_timeout = float(os.environ.get("HTTP_TIMEOUT", "15"))
    reconnect_sec = float(os.environ.get("SERIAL_RECONNECT_SEC", "3"))
    verify_ssl = _env_bool("HTTP_VERIFY_SSL", True)

    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)

    logger.info(
        "Старт: порт=%s baud=%s API=%s",
        serial_port,
        baud,
        api_url,
    )

    while not _shutdown:
        try:
            ser = serial.Serial(serial_port, baud, timeout=1)
        except (serial.SerialException, OSError) as exc:
            logger.warning(
                "Не удалось открыть порт %s: %s. Повтор через %.1f с",
                serial_port,
                exc,
                reconnect_sec,
            )
            time.sleep(reconnect_sec)
            continue

        logger.info("Порт открыт, ожидание сканирования…")

        try:
            while not _shutdown:
                try:
                    raw = ser.readline()
                except (serial.SerialException, OSError) as exc:
                    logger.error("Ошибка чтения с порта: %s", exc)
                    break

                if not raw:
                    continue

                data = raw.decode("utf-8", errors="replace").strip()
                if not data:
                    continue

                logger.info("Код: %s", data)
                _send_code(api_url, data, http_timeout, verify_ssl)
        finally:
            try:
                ser.close()
            except OSError:
                pass

        if _shutdown:
            break

        logger.warning("Соединение с портом закрыто, переподключение через %.1f с…", reconnect_sec)
        time.sleep(reconnect_sec)

    logger.info("Остановка завершена.")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass

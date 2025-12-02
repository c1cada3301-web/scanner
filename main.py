import json
import time
import serial
import logging
import requests
from serial.tools import list_ports

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info(
    f"Сканер будет работать только если:\n"
    f"Он переведён в режим виртуального COM-порта (VCOM).\n"
    f"На Windows установлен драйвер для виртуального порта.\n"
    f"Ваш скомпилированный скрипт (.exe) запущен и читает данные с нужного COM-порта.\n\n"
)

ports = list_ports.comports()
if not ports:
    logger.error("Нет доступных COM-портов.")
    exit(1)

print("Доступные порты:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

choice = int(input("Выберите номер порта(usbmodem): "))
port_name = ports[choice].device

async def scan_qr_codes():
    ser = serial.Serial(port_name, 9600, timeout=1)
    if not ser:
        logger.error("Нет порта или порт изменился(Вы отсканировали штрих-код для USB COM Port?).")
        return
    logger.info("Сканирование запущено...")
    while True:
        data = ser.readline().decode('utf-8').strip()
        if data:
            logger.info(f"Код: {data}")
            await decoder(data)

async def decoder(data):
            # Пример отправки данных через HTTP (если нужно)
            payload = {"scanned_code": data}
            response = requests.post("http://89.169.146.150:8000/api/endpoint", json=payload)

if __name__ == "__main__":
    import asyncio
    asyncio.run(scan_qr_codes())

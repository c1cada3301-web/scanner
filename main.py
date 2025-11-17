import json
import time
import serial
import logging
import requests
from serial.tools import list_ports

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ports = list_ports.comports()
if not ports:
    logger.error("Нет доступных COM-портов.")
    exit(1)

print("Доступные порты:")
for i, port in enumerate(ports):
    print(f"{i}: {port.device}")

choice = int(input("Выберите номер порта: "))
port_name = ports[choice].device  # или выбрать по имени/описанию

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
            response = requests.post("http://0.0.0.0:8000/api/endpoint", json=payload)

if __name__ == "__main__":
    import asyncio
    asyncio.run(scan_qr_codes())
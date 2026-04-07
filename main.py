import threading
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import requests
from serial.tools import list_ports

class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Scanner Client")
        self.geometry("420x260")
        self.resizable(False, False)

        self.server_ip = tk.StringVar(value="84.201.186.125")
        self.port_name = tk.StringVar()
        self.status = tk.StringVar(value="Ожидание...")

        self.create_widgets()
        self.refresh_ports()

    def refresh_ports(self):
        ports = [p.device for p in list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_name.set(ports[0])
        else:
            self.port_name.set("")

    def create_widgets(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="IP сервера:").pack(anchor=tk.W)
        ip_entry = ttk.Entry(frm, textvariable=self.server_ip, width=30)
        ip_entry.pack(fill=tk.X, pady=5)

        ttk.Label(frm, text="COM-порт:").pack(anchor=tk.W)
        self.port_combo = ttk.Combobox(frm, textvariable=self.port_name, state="readonly")
        self.port_combo.pack(fill=tk.X, pady=5)

        refresh_btn = ttk.Button(frm, text="Обновить порты", command=self.refresh_ports)
        refresh_btn.pack(fill=tk.X, pady=2)

        scan_btn = ttk.Button(frm, text="Старт сканирования", command=self.start_scan)
        scan_btn.pack(fill=tk.X, pady=10)

        self.status_lbl = ttk.Label(frm, textvariable=self.status, foreground="blue")
        self.status_lbl.pack(fill=tk.X, pady=5)

    def start_scan(self):
        threading.Thread(target=self.scan_qr_codes, daemon=True).start()

    def scan_qr_codes(self):
        try:
            ser = serial.Serial(self.port_name.get(), 9600, timeout=1)
        except Exception as e:
            self.status.set(f"Ошибка открытия порта: {e}")
            return
        self.status.set("Сканирование запущено...")
        while True:
            try:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    self.status.set(f"Код: {data}")
                    payload = {"scanned_code": data}
                    url = f"http://{self.server_ip.get()}:8000/api/endpoint"
                    try:
                        resp = requests.post(url, json=payload, timeout=5)
                        if resp.status_code == 200:
                            self.status.set("Отправлено успешно!")
                        else:
                            self.status.set(f"Ошибка HTTP: {resp.status_code}")
                    except Exception as e:
                        self.status.set(f"Ошибка отправки: {e}")
            except Exception as e:
                self.status.set(f"Ошибка чтения: {e}")

if __name__ == "__main__":
    app = ScannerApp()
    app.mainloop()
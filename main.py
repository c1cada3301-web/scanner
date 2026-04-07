import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import requests
from serial.tools import list_ports

ser = None
scanning = False

def get_ports():
    return list_ports.comports()

def log(msg, color="white"):
    log_box.config(state="normal")
    log_box.insert("end", msg + "\n", color)
    log_box.see("end")
    log_box.config(state="disabled")

def send_code(data):
    payload = {"scanned_code": data}
    try:
        response = requests.post("http://89.169.146.150:8000/api/endpoint", json=payload, timeout=5)
        log(f"  → Отправлено (HTTP {response.status_code})", "green")
    except requests.RequestException as e:
        log(f"  → Ошибка отправки: {e}", "red")

def scan_loop():
    global ser, scanning
    while scanning:
        try:
            data = ser.readline().decode("utf-8").strip()
            if data:
                log(f"Код: {data}", "yellow")
                send_code(data)
        except Exception as e:
            log(f"Ошибка чтения: {e}", "red")
            root.after(0, stop_scan)
            break

def start_scan():
    global ser, scanning
    selected = port_var.get()
    if not selected:
        log("Выберите порт!", "red")
        return
    try:
        ser = serial.Serial(selected, 9600, timeout=1)
    except serial.SerialException as e:
        log(f"Не удалось открыть порт {selected}: {e}", "red")
        return
    scanning = True
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")
    port_combo.config(state="disabled")
    status_var.set("● Сканирование...")
    status_label.config(foreground="#00e676")
    log(f"Подключено к {selected}. Сканирование запущено.", "green")
    threading.Thread(target=scan_loop, daemon=True).start()

def stop_scan():
    global ser, scanning
    scanning = False
    if ser and ser.is_open:
        ser.close()
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")
    port_combo.config(state="readonly")
    status_var.set("● Остановлено")
    status_label.config(foreground="#ef5350")
    log("Сканирование остановлено.", "white")

def refresh_ports():
    ports = get_ports()
    port_combo["values"] = [p.device for p in ports]
    if ports:
        port_var.set(ports[0].device)
        log(f"Найдено портов: {len(ports)}", "white")
    else:
        port_var.set("")
        log("COM-порты не найдены.", "red")

# --- GUI ---
root = tk.Tk()
root.title("QR Сканер")
root.geometry("520x420")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

BG = "#1e1e1e"
BG2 = "#2d2d2d"
FG = "#ffffff"
ACCENT = "#2979ff"

# Верхняя панель
top = tk.Frame(root, bg=BG, pady=10)
top.pack(fill="x", padx=16)

tk.Label(top, text="COM-порт:", bg=BG, fg=FG, font=("Segoe UI", 10)).pack(side="left")

port_var = tk.StringVar()
port_combo = ttk.Combobox(top, textvariable=port_var, state="readonly", width=12, font=("Segoe UI", 10))
port_combo.pack(side="left", padx=8)

btn_refresh = tk.Button(top, text="⟳", bg=BG2, fg=FG, relief="flat", padx=6,
                        font=("Segoe UI", 11), cursor="hand2", command=refresh_ports)
btn_refresh.pack(side="left")

btn_start = tk.Button(top, text="Старт", bg=ACCENT, fg=FG, relief="flat",
                      padx=12, pady=4, font=("Segoe UI", 10, "bold"),
                      cursor="hand2", command=start_scan)
btn_start.pack(side="left", padx=(16, 4))

btn_stop = tk.Button(top, text="Стоп", bg="#424242", fg=FG, relief="flat",
                     padx=12, pady=4, font=("Segoe UI", 10, "bold"),
                     cursor="hand2", command=stop_scan, state="disabled")
btn_stop.pack(side="left")

# Лог
log_box = scrolledtext.ScrolledText(root, bg=BG2, fg=FG, font=("Consolas", 10),
                                    relief="flat", state="disabled", padx=8, pady=8)
log_box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
log_box.tag_config("green", foreground="#00e676")
log_box.tag_config("red", foreground="#ef5350")
log_box.tag_config("yellow", foreground="#ffeb3b")
log_box.tag_config("white", foreground="#ffffff")

# Статус
bottom = tk.Frame(root, bg=BG, pady=6)
bottom.pack(fill="x", padx=16)

status_var = tk.StringVar(value="● Остановлено")
status_label = tk.Label(bottom, textvariable=status_var, bg=BG, fg="#ef5350", font=("Segoe UI", 9))
status_label.pack(side="left")

tk.Label(bottom, text="Поддержка: @shtrnv", bg=BG, fg="#757575", font=("Segoe UI", 9)).pack(side="right")

refresh_ports()
log("Сканер будет работать только если:", "white")
log("  • Он переведён в режим виртуального COM-порта (VCOM).", "white")
log("  • Сначала вы должны перевести сканер в режим VCOM.", "white")
log("  • А потом уже запускать программу.", "white")
log("  • В случае ошибок пишите в техподдержку тг: @shtrnv\n", "white")
log("Выберите порт и нажмите Старт.", "green")

root.mainloop()

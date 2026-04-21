import tkinter as tk
from tkinter import messagebox  # Módulo para janelas de confirmação
from threading import Thread
import requests

# Configurações de Rede
ips = [f"192.168.0.{i}" for i in range(11, 19)]
headers = {"Content-Type": "application/json"}

def call_api(port_name):
    """Cria o comando PATCH para troca de entrada [3]."""
    payload = {"dev": {"ingest": {"input": port_name}}}
    for ip in ips:
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", json=payload, headers=headers, timeout=1
        )).start()

def confirm_switch(port_name):
    """Solicita confirmação antes da comutação. Uma vez confirmado, envia o payload para as processadoras"""
    target = "Disguise (DP1)" if port_name == "dp1" else "Resolume (DP2)"
    if messagebox.askyesno("Confirmação", f"Deseja realmente comutar todas as processadoras para {target}?"):
        call_api(port_name)

def update_led(index, ip):
    """Consulta o status atual a cada 2 segundos via GET"""
    try:
        response = requests.get(f"http://{ip}/api/v1/public?dev.ingest.input", timeout=0.8)
        if response.status_code == 200:
            current = response.json()['dev']['ingest']['input']
            color = "#3498db" if "dp1" in current else "#e67e22"
            leds[index].config(fg=color)
    except:
        leds[index].config(fg="gray")

def check_all_statuses():
    for i, ip in enumerate(ips):
        Thread(target=update_led, args=(i, ip)).start()
    root.after(2000, check_all_statuses)

root = tk.Tk()
root.title("Helios Batch Switcher - Secure Mode")
root.geometry("400x320")

monitor_frame = tk.LabelFrame(root, text=" Status das Processadoras ", padx=10, pady=10)
monitor_frame.pack(pady=10)

leds = []
for i in range(8):
    row, col = i // 2, i % 2
    f = tk.Frame(monitor_frame); f.grid(row=row, column=col, padx=20, pady=5, sticky="w")
    tk.Label(f, text=f"Helios {i+1}: ", font=("Arial", 10)).pack(side="left")
    led = tk.Label(f, text="●", font=("Arial", 14), fg="gray"); led.pack(side="left")
    leds.append(led)

btn_frame = tk.Frame(root); btn_frame.pack(pady=10)

# Os botões agora chamam a função confirm_switch
tk.Button(btn_frame, text="Disguise (DP1)", bg="#3498db", fg="white", font=("Arial", 10, "bold"),
          width=15, height=2, command=lambda: confirm_switch("dp1")).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="Resolume (DP2)", bg="#e67e22", fg="white", font=("Arial", 10, "bold"),
          width=15, height=2, command=lambda: confirm_switch("dp2")).grid(row=0, column=1, padx=10)

check_all_statuses()
root.mainloop()
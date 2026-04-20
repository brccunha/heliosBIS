import tkinter as tk
from threading import Thread
import requests

# Configurações
ips = [f"192.168.0.{i}" for i in range(11, 18)]
headers = {"Content-Type": "application/json"}

def call_api(input_name):
    payload = {"dev": {"ingest": {"input": input_name}}}
    for ip in ips:
        # Dispara uma thread por processadora para garantir simultaneidade
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", 
            json=payload, 
            headers=headers, 
            timeout=1
        )).start()

# Interface Gráfica
root = tk.Tk()
root.title("Helios Input Switcher")
root.geometry("300x150")

tk.Label(root, text="Controle de Entrada - 8 Processadoras").pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(expand=True)

tk.Button(btn_frame, text="Disguise (DP1)", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
          width=12, height=2, command=lambda: call_api("dp1")).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="Resolume (DP2)", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
          width=12, height=2, command=lambda: call_api("dp2")).grid(row=0, column=1, padx=10)

root.mainloop()
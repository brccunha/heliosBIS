import tkinter as tk
from threading import Thread
import requests

# IPs específicos para o teste
ips = ["192.168.0.12"]
headers = {"Content-Type": "application/json"}

def call_api(input_name):
    payload = {"dev": {"ingest": {"input": input_name}}}
    for ip in ips:
        # Dispara comando em paralelo para garantir simultaneidade
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", 
            json=payload, 
            headers=headers, 
            timeout=2
        )).start()

# Interface Gráfica
root = tk.Tk()
root.title("Helios Batch Input Switcher (beta)")
root.geometry("300x150")

tk.Label(root, text="Controle de Entrada - Processadora 2").pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(expand=True)

tk.Button(btn_frame, text="DP1", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
          width=12, height=2, command=lambda: call_api("dp1")).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="DP2", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
          width=12, height=2, command=lambda: call_api("dp2")).grid(row=0, column=1, padx=10)

root.mainloop()
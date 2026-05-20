import tkinter as tk
from tkinter import messagebox
from threading import Thread
import requests

# Configurações de Rede
ips = [f"192.168.0.{i}" for i in range(11, 19)]
headers = {"Content-Type": "application/json"}

def send_patch(payload):
    """Envia o comando PATCH para todas as processadoras em paralelo"""
    for ip in ips:
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", json=payload, headers=headers, timeout=1
        )).start()

def confirm_topology(mode):
    """Segurança para alteração de topologia da rede."""
    msg = f"Deseja mudar a topologia de todas as processadoras para {mode.upper()}?"
    if messagebox.askyesno("ALTERAR TOPOLOGIA", msg):
        payload = {"dev": {"display": {"redundancy": {"mode": mode}}}}
        send_patch(payload)

def confirm_redundancy(target_state):
    """Segurança para flip de processadora Main/Backup."""
    msg = f"Deseja forçar todas as processadoras a assumirem o papel de {target_state.upper()}?"
    if messagebox.askyesno("ALERTA DE REDUNDÂNCIA", msg):
        payload = {"dev": {"display": {"redundancy": {"state": target_state}}}}
        send_patch(payload)

# --- Interface Gráfica ---
root = tk.Tk()
root.title("Helios Master Control - Redundancy & Topology")
root.geometry("450x250")

# Seção de Redundância (Flip)
tk.Label(root, text="Controle de Redundância (Flip)", font=("Arial", 10, "bold")).pack(pady=5)
flip_frame = tk.Frame(root)
flip_frame.pack(pady=5)

tk.Button(flip_frame, text="ASSUMIR MAIN", bg="#3498db", fg="white", width=18, 
          command=lambda: confirm_redundancy("main")).grid(row=0, column=0, padx=10)
tk.Button(flip_frame, text="ASSUMIR BACKUP", bg="#f39c12", fg="white", width=18, 
          command=lambda: confirm_redundancy("backup")).grid(row=0, column=1, padx=10)

# Seção de Topologia (Modo)
tk.Label(root, text="Topologia do Sistema", font=("Arial", 10, "bold")).pack(pady=10)
mode_frame = tk.Frame(root)
mode_frame.pack(pady=5)

tk.Button(mode_frame, text="MODO FAILOVER", bg="#9b59b6", fg="white", width=18, 
          command=lambda: confirm_topology("failover")).grid(row=0, column=0, padx=10)
tk.Button(mode_frame, text="MODO SEAMLESS", bg="#2c3e50", fg="white", width=18, 
          command=lambda: confirm_topology("seamless")).grid(row=0, column=1, padx=10)

root.mainloop()
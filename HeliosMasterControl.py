import tkinter as tk
from tkinter import messagebox, scrolledtext
from threading import Thread
import requests

# Configurações de Rede
ips = [f"192.168.0.{i}" for i in range(11, 19)]
headers = {"Content-Type": "application/json"}
all_current_alerts = {} 

def send_patch(payload):
    for ip in ips:
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", json=payload, headers=headers, timeout=1
        )).start()

def update_health_display():
    """Limpa o painel e mostra apenas os alertas ativos no dicionário global."""
    health_text.config(state='normal')
    health_text.delete('1.0', tk.END) # Limpa todas as linhas anteriores [1]
    # Organiza por número da Helios para manter a ordem visual
    for idx in sorted(all_current_alerts.keys()):
        for msg in all_current_alerts[idx]:
            health_text.insert(tk.END, msg + "\n")
    health_text.config(state='disabled')

def fetch_status(index, ip):
    try:
        response = requests.get(f"http://{ip}/api/v1/public?dev.display.redundancy&sys.alerts&dev.display.blackout", timeout=0.8)
        if response.status_code == 200:
            data = response.json()
            
            # 1. Feedback de Redundância e Blackout
            red = data.get('dev', {}).get('display', {}).get('redundancy', {})
            state = red.get('state', 'OFFLINE').upper()
            mode = red.get('mode', 'none')
            is_blackout = data.get('dev', {}).get('display', {}).get('blackout', False) [3]
            
            color = "#9b59b6" if mode == "failover" else "#2c3e50"
            display_text = f"{state} (BLK)" if is_blackout else state
            status_labels[index].config(text=display_text, fg=color)

            # 2. Lógica de Saúde (Filtra apenas alertas ativos de severidade 2, 3 e 4) [2]
            alerts = data.get('sys', {}).get('alerts', {}) [4]
            processor_alerts = []
            for details in alerts.values():
                sev = details.get('severity')
                if sev in [1, 5, 6]: # Critical, Error, Warning [2]
                    sev_name = {2: "CRITICAL", 3: "ERROR", 4: "WARNING"}.get(sev)
                    brief = details.get('brief', 'Alert') [7]
                    processor_alerts.append(f"Helios {index+1}: {sev_name} - {brief}")
            
            # Atualiza o dicionário global da Helios específica e redesenha o painel
            all_current_alerts[index] = processor_alerts
            update_health_display() 
    except:
        status_labels[index].config(text="OFFLINE", fg="gray")
        all_current_alerts[index] = [f"Helios {index+1}: OFFLINE"]
        update_health_display()

def monitor_loop():
    for i, ip in enumerate(ips):
        Thread(target=fetch_status, args=(i, ip)).start()
    root.after(2000, monitor_loop)

# --- Funções de Comando ---
def confirm_topology(mode):
    if messagebox.askyesno("TOPOLOGIA", f"Mudar para {mode.upper()}?"):
        send_patch({"dev": {"display": {"redundancy": {"mode": mode}}}}) [8]

def confirm_redundancy(target_state):
    if messagebox.askyesno("REDUNDÂNCIA", f"Assumir {target_state.upper()}?"):
        send_patch({"dev": {"display": {"redundancy": {"state": target_state}}}}) [8, 9]

def confirm_blackout(state):
    action = "ATIVAR" if state else "LIMPAR"
    if messagebox.askyesno("BLACKOUT", f"Deseja {action} o Blackout global?"):
        send_patch({"dev": {"display": {"blackout": state}}}) [10]

# --- Interface Gráfica ---
root = tk.Tk()
root.title("Helios Master Control")
root.geometry("500x780")

monitor_frame = tk.LabelFrame(root, text=" Status das Processadoras ", padx=10, pady=10)
monitor_frame.pack(pady=10, fill="x", padx=20)
status_labels = []
for i in range(8):
    row, col = i // 2, i % 2
    f = tk.Frame(monitor_frame); f.grid(row=row, column=col, padx=20, pady=5, sticky="w")
    tk.Label(f, text=f"Helios {i+1}: ", font=("Arial", 10, "bold")).pack(side="left")
    lbl = tk.Label(f, text="BUSCANDO...", font=("Arial", 10, "bold"), fg="gray")
    lbl.pack(side="left"); status_labels.append(lbl)

tk.Label(root, text="Controle de Redundância (Flip)", font=("Arial", 10, "bold")).pack(pady=5)
flip_frame = tk.Frame(root); flip_frame.pack()
tk.Button(flip_frame, text="GO MAIN", bg="#3498db", fg="white", width=18, command=lambda: confirm_redundancy("main")).grid(row=0, column=0, padx=10)
tk.Button(flip_frame, text="GO BACKUP", bg="#f39c12", fg="white", width=18, command=lambda: confirm_redundancy("backup")).grid(row=0, column=1, padx=10)

tk.Label(root, text="Topologia do Sistema", font=("Arial", 10, "bold")).pack(pady=10)
mode_frame = tk.Frame(root); mode_frame.pack()
tk.Button(mode_frame, text="MODO FAILOVER", bg="#9b59b6", fg="white", width=18, command=lambda: confirm_topology("failover")).grid(row=0, column=0, padx=10)
tk.Button(mode_frame, text="MODO SEAMLESS", bg="#2c3e50", fg="white", width=18, command=lambda: confirm_topology("seamless")).grid(row=0, column=1, padx=10)

tk.Label(root, text="Master Blackout", font=("Arial", 10, "bold")).pack(pady=10)
blk_frame = tk.Frame(root); blk_frame.pack()
tk.Button(blk_frame, text="ATIVAR BLACKOUT", bg="#e74c3c", fg="white", width=18, command=lambda: confirm_blackout(True)).grid(row=0, column=0, padx=10)
tk.Button(blk_frame, text="LIMPAR BLACKOUT", bg="#2ecc71", fg="white", width=18, command=lambda: confirm_blackout(False)).grid(row=0, column=1, padx=10)

tk.Label(root, text="Painel de Saúde (Alertas Ativos)", font=("Arial", 10, "bold")).pack(pady=15)
health_text = scrolledtext.ScrolledText(root, width=55, height=8, font=("Consolas", 9), bg="#f8f9fa", state='disabled')
health_text.pack(padx=20, pady=5)

monitor_loop()
root.mainloop()
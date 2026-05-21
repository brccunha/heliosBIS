import tkinter as tk
from tkinter import messagebox, scrolledtext
from threading import Thread
import requests

# Configurações de Rede
ips = [f"192.168.0.{i}" for i in range(11, 19)]
headers = {"Content-Type": "application/json"}
all_current_alerts = {}

def send_patch(payload):
    """Envia comandos PATCH para todas as processadoras."""
    for ip in ips:
        Thread(target=lambda i=ip: requests.patch(
            f"http://{i}/api/v1/public", json=payload, headers=headers, timeout=1
        )).start()

def fetch_status(index, ip):
    """Consulta redundância e alertas via GET [1, 2, 5]."""
    try:
        response = requests.get(f"http://{ip}/api/v1/public?dev.display.redundancy&sys.alerts", timeout=0.8)
        if response.status_code == 200:
            data = response.json()
            
            # 1. Lógica de Redundância e Cores
            red = data.get('dev', {}).get('display', {}).get('redundancy', {})
            state = red.get('state', 'OFFLINE').upper() # ACTIVE/STANDBY [1]
            mode = red.get('mode', 'none') # failover/seamless [1]
            
            color = "#9b59b6" if mode == "failover" else "#2c3e50"
            status_labels[index].config(text=state, fg=color)

            # 2. Lógica de Saúde (Health Pane) [2, 3]
            alerts = data.get('sys', {}).get('alerts', {})
            processor_alerts = []
            for details in alerts.values():
                sev = details.get('severity')
                if sev in [6, 7]: # Apenas Error e Warning [3]
                    sev_name = "ERROR" if sev == 3 else "WARNING"
                    brief = details.get('brief', 'Alert')
                    processor_alerts.append(f"Helios {index+1}: {sev_name} - {brief}")
            
            all_current_alerts[index] = processor_alerts
            update_health_display()
    except:
        status_labels[index].config(text="OFFLINE", fg="gray")
        all_current_alerts[index] = []

def update_health_display():
    """Atualiza dinamicamente a área de alertas ativos."""
    health_text.config(state='normal')
    health_text.delete('1.0', tk.END)
    for idx in sorted(all_current_alerts.keys()):
        for msg in all_current_alerts[idx]:
            health_text.insert(tk.END, msg + "\n")
    health_text.config(state='disabled')

def monitor_loop():
    for i, ip in enumerate(ips):
        Thread(target=fetch_status, args=(i, ip)).start()
    root.after(2000, monitor_loop)
    
# --- Pedidos de confirmação antes de alterar as configuração de topologia e redundância ---
def confirm_topology(mode):
    if messagebox.askyesno("ALTERAR TOPOLOGIA", f"Deseja mudar todas para {mode.upper()}?"):
        send_patch({"dev": {"display": {"redundancy": {"mode": mode}}}})

def confirm_redundancy(target_state):
    if messagebox.askyesno("ALERTA", f"Forçar todas as processadoras para {target_state.upper()}?"):
        send_patch({"dev": {"display": {"redundancy": {"state": target_state}}}})

# --- Interface Gráfica ---
root = tk.Tk()
root.title("Helios Master Control - Professional Suite")
root.geometry("500x650")

# Tabela de Status (Monitoramento)
monitor_frame = tk.LabelFrame(root, text=" Status das Processadoras ", padx=10, pady=10)
monitor_frame.pack(pady=10, fill="x", padx=20)

status_labels = []
for i in range(8):
    row, col = i // 2, i % 2
    f = tk.Frame(monitor_frame); f.grid(row=row, column=col, padx=20, pady=5, sticky="w")
    tk.Label(f, text=f"Helios {i+1}: ", font=("Arial", 10, "bold")).pack(side="left")
    lbl = tk.Label(f, text="BUSCANDO...", font=("Arial", 10, "bold"), fg="gray")
    lbl.pack(side="left")
    status_labels.append(lbl)

# Comandos de Redundância
tk.Label(root, text="Controle de Redundância (Fallback)", font=("Arial", 10, "bold")).pack(pady=5)
flip_frame = tk.Frame(root); flip_frame.pack(pady=5)
tk.Button(flip_frame, text="GO MAIN", bg="#3498db", fg="white", width=18, command=lambda: confirm_redundancy("main")).grid(row=0, column=0, padx=10)
tk.Button(flip_frame, text="GO BACKUP", bg="#f39c12", fg="white", width=18, command=lambda: confirm_redundancy("backup")).grid(row=0, column=1, padx=10)

# Comandos de Topologia
tk.Label(root, text="Topologia do Sistema", font=("Arial", 10, "bold")).pack(pady=5)
mode_frame = tk.Frame(root); mode_frame.pack(pady=5)
tk.Button(mode_frame, text="MODO FAILOVER", bg="#9b59b6", fg="white", width=18, command=lambda: confirm_topology("failover")).grid(row=0, column=0, padx=10)
tk.Button(mode_frame, text="MODO SEAMLESS", bg="#2c3e50", fg="white", width=18, command=lambda: confirm_topology("seamless")).grid(row=0, column=1, padx=10)

# Health Pane
tk.Label(root, text="Painel de Saúde (Alertas Ativos)", font=("Arial", 10, "bold")).pack(pady=10)
health_text = scrolledtext.ScrolledText(root, width=55, height=8, font=("Consolas", 9), bg="#f8f9fa", state='disabled')
health_text.pack(padx=20, pady=5)

monitor_loop()
root.mainloop()
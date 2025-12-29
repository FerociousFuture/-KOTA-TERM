#!/usr/bin/env python3
import json
import os
import sys
import time

# Ajusta la ruta si es necesario
JSON_PATH = os.path.expanduser("~/mascota_savegame.json")

# Colores ANSI
C_RESET = '\033[0m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_MAGENTA = '\033[95m'
C_BOLD = '\033[1m'

def get_color(valor, es_inverso=False):
    if es_inverso:
        if valor < 30: return C_GREEN
        if valor < 60: return C_YELLOW
        return C_RED
    else:
        if valor > 70: return C_GREEN
        if valor > 30: return C_YELLOW
        return C_RED

def main():
    try:
        if not os.path.exists(JSON_PATH):
            sys.exit(0)

        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Chequear congelamiento
        if data.get("congelado", False):
            nombre = data.get("nombre", "Mascota")
            print(f"   ❄️  {C_BOLD}{nombre}{C_RESET}  ::  {C_CYAN}[CONGELADO EN CRIOSTASIS]{C_RESET}")
            print("")
            return

        # --- LÓGICA DE SIMULACIÓN (Igual que antes) ---
        ultima_conexion = float(data.get("ultima_conexion", time.time()))
        hambre = float(data.get("hambre", 100))
        energia = float(data.get("energia", 100))
        dormido = data.get("estado_dormido", False)
        
        ahora = time.time()
        horas_pasadas = (ahora - ultima_conexion) / 3600

        if horas_pasadas > 0.02:
            if dormido:
                hambre -= horas_pasadas * 0.5
                energia += horas_pasadas * 50.0
            else:
                hambre -= horas_pasadas * 4.2
                energia -= horas_pasadas * 4.2

        hambre = max(0, min(100, hambre))
        energia = max(0, min(100, energia))
        
        nombre = data.get("nombre", "Mascota")
        afecto_raw = float(data.get("afecto", 0))
        afecto = (afecto_raw + 100) / 2
        status = data.get("status", "vivo")
        p = data.get("personalidad", {})
        estres = float(p.get("estres", 0))

        estres_simulado = estres
        if hambre < 30: estres_simulado += 10
        if energia < 30: estres_simulado += 10
        estres_simulado = min(100, estres_simulado)

        if status != "vivo":
            estado_icon = "💀"
            estado_txt = f"{C_RED}Muerto{C_RESET}"
        elif dormido:
            estado_icon = "💤"
            estado_txt = f"{C_CYAN}Dormido{C_RESET}"
        else:
            estado_icon = "●"
            estado_txt = f"{C_GREEN}Activo{C_RESET}"
        
        out = (
            f"   {estado_icon} {C_BOLD}{nombre}{C_RESET}  ::  "
            f"🍖 {get_color(hambre)}{int(hambre)}%{C_RESET}  "
            f"⚡ {get_color(energia)}{int(energia)}%{C_RESET}  "
            f"🧠 {get_color(estres_simulado, True)}{int(estres_simulado)}%{C_RESET}  "
            f"❤️  {C_MAGENTA}{int(afecto)}%{C_RESET}  "
            f"[{estado_txt}]"
        )
        
        print(out)
        print("")

    except Exception:
        pass

if __name__ == "__main__":
    main()
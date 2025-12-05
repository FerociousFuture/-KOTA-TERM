#!/usr/bin/env python3
import json
import os
import sys
import time  # Necesario para calcular el paso del tiempo

# Ajusta la ruta si es necesario
JSON_PATH = os.path.expanduser("~/mascota_savegame.json")

# Colores ANSI
C_RESET = '\033[0m'
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_MAGENTA = '\033[95m'
C_GRAY = '\033[90m'
C_BOLD = '\033[1m'

def get_color(valor, es_inverso=False):
    """Retorna color según el valor y si es inverso (para estrés)"""
    if es_inverso:  # Para estrés (bajo es bueno)
        if valor < 30: return C_GREEN
        if valor < 60: return C_YELLOW
        return C_RED
    else:  # Para energía/hambre (alto es bueno)
        if valor > 70: return C_GREEN
        if valor > 30: return C_YELLOW
        return C_RED

def main():
    try:
        # Verificar si existe el archivo
        if not os.path.exists(JSON_PATH):
            print(f"{C_GRAY}[No se encontró mascota_savegame.json]{C_RESET}")
            sys.exit(0)

        # Cargar datos
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- LÓGICA DE SIMULACIÓN DE TIEMPO ---
        # Extraemos datos base
        ultima_conexion = float(data.get("ultima_conexion", time.time()))
        hambre = float(data.get("hambre", 100))
        energia = float(data.get("energia", 100))
        dormido = data.get("estado_dormido", False)
        
        # Calcular tiempo transcurrido
        ahora = time.time()
        horas_pasadas = (ahora - ultima_conexion) / 3600

        # Aplicar el mismo decaimiento que el script principal
        if horas_pasadas > 0.02: # Solo si ha pasado un poco de tiempo
            if dormido:
                # Metabolismo lento dormido
                hambre -= horas_pasadas * 2.0
                energia += horas_pasadas * 12.5
            else:
                # Metabolismo normal despierto
                hambre -= horas_pasadas * 10.0
                energia -= horas_pasadas * 6.25

        # Limitar valores (Clamp 0-100)
        hambre = max(0, min(100, hambre))
        energia = max(0, min(100, energia))
        
        # --- FIN LÓGICA SIMULACIÓN ---

        nombre = data.get("nombre", "Mascota")
        afecto_raw = float(data.get("afecto", 0))
        # Normalizar afecto de -100~100 a 0~100 para display
        afecto = (afecto_raw + 100) / 2
        
        status = data.get("status", "vivo")
        
        # Personalidad
        p = data.get("personalidad", {})
        estres = float(p.get("estres", 0))

        # Recalcular estrés visualmente basado en las nuevas stats calculadas
        # (Opcional, pero ayuda a que sea coherente)
        estres_simulado = estres
        if hambre < 30: estres_simulado += 10
        if energia < 30: estres_simulado += 10
        estres_simulado = min(100, estres_simulado)

        # Iconos y Estado
        if status != "vivo":
            estado_icon = "💀"
            estado_txt = f"{C_RED}Muerto{C_RESET}"
        elif dormido:
            estado_icon = "💤"
            estado_txt = f"{C_CYAN}Dormido{C_RESET}"
        else:
            estado_icon = "●"
            estado_txt = f"{C_GREEN}Activo{C_RESET}"
        
        # Renderizado compacto
        out = (
            f"   {estado_icon} {C_BOLD}{nombre}{C_RESET}  ::  "
            f"🍖 {get_color(hambre)}{int(hambre)}%{C_RESET}  "
            f"⚡ {get_color(energia)}{int(energia)}%{C_RESET}  "
            f"🧠 {get_color(estres_simulado, True)}{int(estres_simulado)}%{C_RESET}  "
            f"❤️  {C_MAGENTA}{int(afecto)}%{C_RESET}  "
            f"[{estado_txt}]"
        )
        
        print(out)
        print("")  # Salto de línea extra

    except json.JSONDecodeError:
        print(f"{C_RED}[Error: JSON corrupto]{C_RESET}")
        sys.exit(1)
    except Exception as e:
        # Modo silencioso: si falla, no muestra nada
        pass

if __name__ == "__main__":
    main()
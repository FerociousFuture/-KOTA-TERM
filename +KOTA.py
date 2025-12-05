#!/usr/bin/env python3
"""
+KOTA - Mascota Virtual de Terminal
Uso: python +KOTA.py [comando] [argumentos]

Comandos disponibles:
    estado          - Ver estado actual
    alimentar       - Dar comida
    dormir          - Poner a dormir / despertar
    jugar [juego]   - Jugar (rps, pares, adivina, tictactoe)
    acariciar       - Dar cariño para bajar estrés
    pasear          - Salir a caminar (gasta energía, sube felicidad)
    renombrar [nom] - Cambiar el nombre de la mascota
    stats           - Ver estadísticas detalladas
    reset           - Reiniciar mascota
"""

import json
import time
import math
import random
import os
import sys
from datetime import datetime

# --- CONFIGURACIÓN ---
FILE_DATA = "mascota_savegame.json"

# Colores ANSI
class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

class GeoPet:
    def __init__(self):
        self.data = {
            "nombre": "Ente",
            "hambre": 100.0,
            "energia": 100.0,
            "afecto": 50.0,
            "ultima_conexion": time.time(),
            "estado_dormido": False,
            "maltrato_acumulado": 0,
            "juegos_stats": {"rps": 0, "tictactoe": 0, "pares": 0, "adivina": 0},
            "ia_memory": {
                "rps_history": [],
                "par_non_bias": 0
            },
            "status": "vivo",
            "personalidad": {
                "alimentacion_frecuencia": 0,
                "privacion_sueno": 0,
                "juego_favorito": "neutral",
                "hambre_critica_count": 0,
                "sobrealimentacion": 0,
                "maltrato_psicologico": 0,
                "amor_recibido": 0,
                "estres": 0,
            },
            "historial": {
                "alimentaciones": [],
                "sesiones_juego": [],
                "ciclos_sueno": [],
                "paseos": [] 
            }
        }
        
        self.cargar_datos()
        
        if self.data["status"] == "escapado":
            self.mostrar_abandono()
            sys.exit(1)
        
        self.procesar_tiempo_offline()
        self.actualizar_personalidad()

    # ==========================================================
    # PERSISTENCIA
    # ==========================================================
    def cargar_datos(self):
        if os.path.exists(FILE_DATA):
            try:
                with open(FILE_DATA, 'r') as f:
                    cargar = json.load(f)
                    for key in self.data:
                        if key in cargar:
                            if isinstance(self.data[key], dict) and isinstance(cargar[key], dict):
                                self.data[key].update(cargar[key])
                            else:
                                self.data[key] = cargar[key]
            except:
                print(f"{Color.RED}Error cargando datos. Iniciando nuevo.{Color.RESET}")

    def guardar_datos(self):
        self.data["ultima_conexion"] = time.time()
        with open(FILE_DATA, 'w') as f:
            json.dump(self.data, f, indent=4)

    def procesar_tiempo_offline(self):
        ahora = time.time()
        delta = ahora - self.data["ultima_conexion"]
        horas = delta / 3600

        if horas < 0.02:
            return

        # --- MODIFICACIÓN: Metabolismo ---
        if self.data["estado_dormido"]:
            # Si duerme, metabolismo lento (2 puntos por hora)
            decay_hambre = horas * 2.0 
            self.data["energia"] += horas * 12.5
            self.data["personalidad"]["privacion_sueno"] -= horas * 3
        else:
            # Si despierto, metabolismo normal (10 puntos por hora)
            decay_hambre = horas * 10.0
            self.data["energia"] -= horas * 6.25
            self.data["personalidad"]["privacion_sueno"] += horas * 2

        self.data["hambre"] -= decay_hambre
        
        hora_actual = datetime.now().hour
        if 0 <= hora_actual <= 6 and not self.data["estado_dormido"]:
            if self.data["energia"] < 30:
                self.data["afecto"] -= 15
                self.data["maltrato_acumulado"] += 10
                self.data["personalidad"]["maltrato_psicologico"] += 5
        
        self.check_limites()

    def check_limites(self):
        self.data["hambre"] = max(0, min(100, self.data["hambre"]))
        self.data["energia"] = max(0, min(100, self.data["energia"]))
        self.data["afecto"] = max(-100, min(100, self.data["afecto"]))
        
        for key in ["privacion_sueno", "estres", "maltrato_psicologico"]:
            if key in self.data["personalidad"]:
                self.data["personalidad"][key] = max(0, min(100, 
                    self.data["personalidad"][key]))

        if self.data["afecto"] < -70 or self.data["maltrato_acumulado"] > 150:
            self.escapar()

    def escapar(self):
        self.data["status"] = "escapado"
        self.guardar_datos()
        self.mostrar_abandono()
        sys.exit(1)

    def mostrar_abandono(self):
        print(f"\n{Color.RED}{Color.BOLD}╔═══════════════════════════════════╗{Color.RESET}")
        print(f"{Color.RED}{Color.BOLD}║   +KOTA  SE HA IDO DE CASA       ║{Color.RESET}")
        print(f"{Color.RED}{Color.BOLD}╚═══════════════════════════════════╝{Color.RESET}")
        print(f"\n{Color.YELLOW}Encontraste una nota:{Color.RESET}\n")
        print(f"{Color.GRAY}┌────────────────────────────────┐{Color.RESET}")
        print(f"{Color.GRAY}│ 'No puedo seguir así.          │{Color.RESET}")
        print(f"{Color.GRAY}│  Me voy a buscar un mejor      │{Color.RESET}")
        print(f"{Color.GRAY}│  dueño. No me busques.'        │{Color.RESET}")
        print(f"{Color.GRAY}│                    - +KOTA     │{Color.RESET}")
        print(f"{Color.GRAY}└────────────────────────────────┘{Color.RESET}\n")
        print(f"{Color.CYAN}Usa 'python +KOTA.py reset' para empezar de nuevo.{Color.RESET}\n")

    # ==========================================================
    # PERSONALIDAD Y GRÁFICOS
    # ==========================================================
    def actualizar_personalidad(self):
        p = self.data["personalidad"]
        estres = 0
        if self.data["hambre"] < 30: estres += 30
        if self.data["energia"] < 30: estres += 20
        if self.data["afecto"] < 0: estres += 30
        estres += p["privacion_sueno"]
        estres += p["maltrato_psicologico"] * 5
        p["estres"] = min(100, estres)
        
        stats = self.data["juegos_stats"]
        if sum(stats.values()) > 5:
            p["juego_favorito"] = max(stats, key=stats.get)
        
        if self.data["hambre"] < 20:
            p["hambre_critica_count"] += 0.01

    def get_forma_ascii(self):
        p = self.data["personalidad"]
        forma_base = {
            "rps": "triangle", "tictactoe": "square",
            "pares": "pentagon", "adivina": "hexagon",
            "neutral": "circle"
        }
        forma = forma_base.get(p["juego_favorito"], "circle")
        if self.data["afecto"] > 70: forma = "circle"
        elif self.data["afecto"] < -30: forma = "triangle"
        return forma

    def get_color_ascii(self):
        p = self.data["personalidad"]
        if self.data["estado_dormido"]: return Color.BLUE
        salud = (self.data["hambre"] + self.data["energia"]) / 2
        if p["estres"] > 70: return Color.RED
        if self.data["afecto"] > 80 and salud > 70: return Color.MAGENTA
        if self.data["afecto"] > 50 and salud > 60: return Color.CYAN
        if self.data["afecto"] < -30: return Color.RED
        if salud > 70: return Color.GREEN
        elif salud > 40: return Color.YELLOW
        else: return Color.RED

    def get_expresion(self):
        p = self.data["personalidad"]
        if self.data["estado_dormido"]: return "dormido"
        if p["estres"] > 70: return "estresado"
        if self.data["energia"] < 20: return "cansado"
        if self.data["hambre"] < 20: return "hambriento"
        if self.data["afecto"] > 70: return "feliz"
        elif self.data["afecto"] > 30: return "contento"
        elif self.data["afecto"] > -20: return "neutral"
        elif self.data["afecto"] > -50: return "triste"
        else: return "enojado"

    def dibujar(self):
        forma = self.get_forma_ascii()
        color = self.get_color_ascii()
        expresion = self.get_expresion()
        print(f"\n{color}{Color.BOLD}", end="")
        if forma == "triangle": self.dibujar_triangulo(expresion)
        elif forma == "square": self.dibujar_cuadrado(expresion)
        elif forma == "pentagon": self.dibujar_pentagono(expresion)
        elif forma == "hexagon": self.dibujar_hexagono(expresion)
        else: self.dibujar_circulo(expresion)
        print(Color.RESET)

    def get_cara_ascii(self, expresion):
        caras = {
            "dormido": ("─   ─", "Z z z"), "feliz": ("‾ ‾", "^ ^"),
            "contento": ("‾ ‾", "• •"), "neutral": ("─ ─", "• •"),
            "triste": ("╲ ╱", "• •"), "enojado": ("╲ ╱", "◉ ◉"),
            "cansado": ("_ _", "- -"), "hambriento": ("╱ ╲", "O O"),
            "estresado": ("╲ ╱", "◎ ◎")
        }
        return caras.get(expresion, ("─ ─", "• •"))

    # Métodos de dibujo específicos
    def dibujar_triangulo(self, e):
        c, o = self.get_cara_ascii(e)
        print(f"        △\n       ╱ ╲\n      ╱{c}╲\n     ╱ {o} ╲\n    ╱       ╲\n   ╱─────────╲")
    def dibujar_cuadrado(self, e):
        c, o = self.get_cara_ascii(e)
        print(f"   ┌─────────┐\n   │         │\n   │  {c}  │\n   │  {o}  │\n   │         │\n   └─────────┘")
    def dibujar_pentagono(self, e):
        c, o = self.get_cara_ascii(e)
        print(f"      ╱‾‾‾╲\n     ╱     ╲\n    │  {c}  │\n    │  {o}  │\n     ╲     ╱\n      ╲___╱")
    def dibujar_hexagono(self, e):
        c, o = self.get_cara_ascii(e)
        print(f"     ╱‾‾‾‾‾╲\n    ╱       ╲\n   │   {c}   │\n   │   {o}   │\n    ╲       ╱\n     ╲_____╱")
    def dibujar_circulo(self, e):
        c, o = self.get_cara_ascii(e)
        print(f"     ╭─────╮\n    ╱       ╲\n   │   {c}   │\n   │   {o}   │\n    ╲       ╱\n     ╰─────╯")

    # ==========================================================
    # NUEVOS COMANDOS
    # ==========================================================

    def renombrar(self, nuevo_nombre):
        antiguo = self.data["nombre"]
        self.data["nombre"] = nuevo_nombre
        self.guardar_datos()
        print(f"{Color.GREEN}¡Hecho! {antiguo} ahora se llama {Color.BOLD}{nuevo_nombre}{Color.RESET}{Color.GREEN}.{Color.RESET}")
        self.mostrar_estado()

    def acariciar(self):
        if self.data["estado_dormido"]:
            print(f"{Color.YELLOW}Shh... {self.data['nombre']} está durmiendo. Mejor no molestarlo.{Color.RESET}")
            return
        
        # Reacción basada en afecto actual
        if self.data["afecto"] < -20:
            print(f"{Color.RED}{self.data['nombre']} se aparta. No quiere que lo toques.{Color.RESET}")
            self.data["afecto"] += 0.5 # Sube muy poco
        elif self.data["afecto"] < 20:
            print(f"{Color.CYAN}Acaricias a {self.data['nombre']}. Se deja hacer, pero no parece emocionado.{Color.RESET}")
            self.data["afecto"] += 2
            self.data["personalidad"]["estres"] -= 2
        else:
            print(f"{Color.MAGENTA}¡A {self.data['nombre']} le encanta! Ronronea (o vibra) de felicidad.{Color.RESET}")
            self.data["afecto"] += 4
            self.data["personalidad"]["estres"] -= 5
            self.data["personalidad"]["amor_recibido"] += 1
        
        self.actualizar_personalidad()
        self.check_limites()
        self.guardar_datos()

    def pasear(self):
        if self.data["estado_dormido"]:
            print(f"{Color.YELLOW}ZzZz... está dormido.{Color.RESET}")
            return

        if self.data["energia"] < 20:
            print(f"{Color.RED}{self.data['nombre']} está demasiado cansado para salir.{Color.RESET}")
            return
        
        if self.data["hambre"] < 15:
            print(f"{Color.RED}{self.data['nombre']} tiene demasiada hambre para caminar.{Color.RESET}")
            return

        # Costos del paseo
        self.data["energia"] -= 25
        self.data["hambre"] -= 20
        self.data["afecto"] += 10
        self.data["personalidad"]["estres"] -= 15
        
        # Registrar paseo
        if "paseos" not in self.data["historial"]: self.data["historial"]["paseos"] = []
        self.data["historial"]["paseos"].append(time.time())

        # Evento aleatorio
        eventos = [
            "persiguió una ardilla glitch.",
            "encontró un bit brillante en el suelo.",
            "se peleó con una papelera de reciclaje.",
            "marcó territorio en un firewall.",
            "disfrutó de la brisa del ventilador.",
            "recibió elogios de otro usuario."
        ]
        evento = random.choice(eventos)

        print(f"\n{Color.GREEN}🌲 ¡Salieron de paseo! 🌲{Color.RESET}")
        print(f"Caminaron un buen rato y {self.data['nombre']} {evento}")
        print(f"{Color.CYAN}(Energía -25, Hambre -20, Estrés -15, Afecto +10){Color.RESET}")
        
        self.actualizar_personalidad()
        self.check_limites()
        self.guardar_datos()

    # ==========================================================
    # COMANDOS EXISTENTES
    # ==========================================================
    def mostrar_estado(self):
        self.limpiar_pantalla()
        print(f"\n{Color.CYAN}{Color.BOLD}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}║       +KOTA  - Estado Actual          ║{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}╚═══════════════════════════════════════╝{Color.RESET}\n")
        self.dibujar()
        p = self.data["personalidad"]
        print(f"\n{Color.BOLD}Nombre:{Color.RESET} {self.data['nombre']}")
        print(f"{Color.BOLD}Forma:{Color.RESET} {p['juego_favorito'].upper()}")
        print(f"{Color.BOLD}Estado:{Color.RESET} {self.get_estado_texto()}\n")
        self.dibujar_barra("Hambre", self.data["hambre"], Color.GREEN)
        self.dibujar_barra("Energía", self.data["energia"], Color.CYAN)
        afecto_norm = (self.data["afecto"] + 100) / 2
        self.dibujar_barra("Afecto", afecto_norm, Color.MAGENTA)
        print(f"\n{Color.GRAY}Estrés: {int(p['estres'])}% | Privación Sueño: {int(p['privacion_sueno'])}%{Color.RESET}")
        hora = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Color.GRAY}[{hora}]{Color.RESET}")

    def dibujar_barra(self, nombre, valor, color):
        largo_barra = 20
        lleno = int((valor / 100) * largo_barra)
        vacio = largo_barra - lleno
        barra = f"{'█' * lleno}{'░' * vacio}"
        print(f"{nombre:8} [{color}{barra}{Color.RESET}] {int(valor):3}%")

    def get_estado_texto(self):
        expr = self.get_expresion()
        estados = {
            "dormido": "😴 Durmiendo", "feliz": "😊 Muy Feliz",
            "contento": "🙂 Contento", "neutral": "😐 Neutral",
            "triste": "😔 Triste", "enojado": "😠 Enojado",
            "cansado": "😫 Exhausto", "hambriento": "🤤 Hambriento",
            "estresado": "😰 Estresado"
        }
        return estados.get(expr, "Desconocido")

    def alimentar(self):
        if self.data["estado_dormido"]:
            print(f"{Color.YELLOW}+KOTA está durmiendo profundamente.{Color.RESET}")
            return
        if self.data["hambre"] > 90:
            print(f"{Color.YELLOW}+KOTA no tiene hambre ahora.{Color.RESET}")
            self.data["personalidad"]["sobrealimentacion"] += 1
            if self.data["personalidad"]["sobrealimentacion"] > 15:
                self.data["afecto"] -= 2
                print(f"{Color.RED}(Está molesto por forzarlo a comer){Color.RESET}")
        else:
            cantidad = 35 if self.data["hambre"] < 40 else 25
            self.data["hambre"] += cantidad
            self.data["afecto"] += 3
            self.data["personalidad"]["amor_recibido"] += 1
            self.data["historial"]["alimentaciones"].append(time.time())
            print(f"{Color.GREEN}¡{self.data['nombre']} ha comido! (+{cantidad} hambre){Color.RESET}")
            print(f"{Color.MAGENTA}(Afecto +3){Color.RESET}")
        self.actualizar_personalidad()
        self.check_limites()
        self.guardar_datos()
        self.mostrar_estado()

    def dormir(self):
        if not self.data["estado_dormido"]:
            if self.data["energia"] > 70:
                print(f"{Color.YELLOW}{self.data['nombre']} tiene demasiada energía para dormir.{Color.RESET}")
                return
            self.data["estado_dormido"] = True
            self.data["historial"]["ciclos_sueno"].append({
                "inicio": time.time(),
                "energia_inicio": self.data["energia"]
            })
            print(f"{Color.CYAN}{self.data['nombre']} se ha ido a dormir... 💤{Color.RESET}")
        else:
            if len(self.data["historial"]["ciclos_sueno"]) > 0:
                ultimo = self.data["historial"]["ciclos_sueno"][-1]
                duracion = (time.time() - ultimo["inicio"]) / 3600
                if duracion < 4:
                    self.data["afecto"] -= 5
                    self.data["personalidad"]["maltrato_psicologico"] += 2
                    print(f"{Color.RED}Lo despertaste muy pronto. Está molesto. (Afecto -5){Color.RESET}")
            self.data["estado_dormido"] = False
            print(f"{Color.GREEN}{self.data['nombre']} se ha despertado.{Color.RESET}")
        self.guardar_datos()
        self.mostrar_estado()

    def mostrar_stats(self):
        self.limpiar_pantalla()
        p = self.data["personalidad"]
        h = self.data["historial"]
        num_paseos = len(h.get("paseos", []))
        
        print(f"\n{Color.CYAN}{Color.BOLD}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}║     +KOTA  - Estadísticas Completas   ║{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}╚═══════════════════════════════════════╝{Color.RESET}\n")
        print(f"{Color.BOLD}📊 Actividad:{Color.RESET}")
        for juego, count in self.data["juegos_stats"].items():
            print(f"  • {juego:12} : {count} veces")
        
        print(f"\n{Color.BOLD}🧠 Personalidad:{Color.RESET}")
        print(f"  • Juego Favorito    : {p['juego_favorito'].upper()}")
        print(f"  • Amor Recibido     : {int(p['amor_recibido'])} puntos")
        print(f"  • Estrés            : {int(p['estres'])}%")
        print(f"  • Maltrato          : {int(p['maltrato_psicologico'])} puntos")
        
        print(f"\n{Color.BOLD}📜 Historial:{Color.RESET}")
        print(f"  • Alimentaciones    : {len(h['alimentaciones'])} veces")
        print(f"  • Sesiones de Juego : {len(h['sesiones_juego'])} veces")
        print(f"  • Paseos            : {num_paseos} veces")
        
        if len(h["alimentaciones"]) > 0:
            tiempo_total = (time.time() - h["alimentaciones"][0]) / 3600
            print(f"\n{Color.GRAY}Edad aprox: {tiempo_total:.1f} horas{Color.RESET}")

    # ==========================================================
    # JUEGOS
    # ==========================================================
    def jugar(self, tipo_juego):
        if self.data["estado_dormido"]:
            print(f"{Color.YELLOW}Está durmiendo...{Color.RESET}")
            return
        if self.data["energia"] < 15:
            print(f"{Color.RED}Está demasiado cansado para jugar.{Color.RESET}")
            return
        
        if tipo_juego == "rps": self.juego_rps()
        elif tipo_juego == "pares": self.juego_pares()
        elif tipo_juego == "adivina": self.juego_adivina()
        elif tipo_juego == "tictactoe": self.juego_tictactoe()
        else: print(f"{Color.RED}Juego no reconocido. Usa: rps, pares, adivina, tictactoe{Color.RESET}")

    def juego_rps(self):
        print(f"\n{Color.CYAN}{Color.BOLD}✊ Piedra Papel Tijera{Color.RESET}\n")
        eleccion = input(f"Elige ({Color.GREEN}R{Color.RESET}oca, {Color.GREEN}P{Color.RESET}apel, {Color.GREEN}T{Color.RESET}ijera): ").upper()
        if not eleccion or eleccion[0] not in ['R', 'P', 'T']: return
        eleccion = eleccion[0]
        history = self.data["ia_memory"]["rps_history"]
        if len(history) >= 3: prediccion = self.predecir_rps(history[-3:], history)
        else: prediccion = random.choice(['R', 'P', 'T'])
        simbolos = {'R': '✊', 'P': '🖐️', 'T': '✌️'}
        print(f"\nTú: {simbolos[eleccion]}  {self.data['nombre']}: {simbolos[prediccion]}")
        ganador = self.evaluar_rps(eleccion, prediccion)
        if ganador == "empate":
            print(f"{Color.YELLOW}¡EMPATE!{Color.RESET}")
            self.data["afecto"] += 1
        elif ganador == "usuario":
            print(f"{Color.GREEN}¡GANASTE! 🎉{Color.RESET}")
            self.data["afecto"] += 6
            self.data["personalidad"]["amor_recibido"] += 2
        else:
            print(f"{Color.RED}{self.data['nombre']} ganó... 😏{Color.RESET}")
            self.data["afecto"] -= 1
        history.append(eleccion)
        if len(history) > 30: history.pop(0)
        self.data["juegos_stats"]["rps"] += 1
        self.data["hambre"] -= 4
        self.data["energia"] -= 6
        self.finalizar_juego("rps")

    def predecir_rps(self, secuencia, history):
        for i in range(len(history) - 3):
            if history[i:i+3] == secuencia and i+3 < len(history):
                return self.counter_rps(history[i+3])
        conteo = {'R': history.count('R'), 'P': history.count('P'), 'T': history.count('T')}
        return self.counter_rps(max(conteo, key=conteo.get))
    def counter_rps(self, jugada): return {'R': 'P', 'P': 'T', 'T': 'R'}[jugada]
    def evaluar_rps(self, j1, j2):
        if j1 == j2: return "empate"
        if (j1 == 'R' and j2 == 'T') or (j1 == 'P' and j2 == 'R') or (j1 == 'T' and j2 == 'P'): return "usuario"
        return "ia"

    def juego_pares(self):
        print(f"\n{Color.CYAN}{Color.BOLD}🎲 Pares o Nones{Color.RESET}\n")
        try:
            eleccion = int(input("Elige un número (1-10): "))
            if eleccion < 1 or eleccion > 10: raise ValueError
        except: return
        bias = self.data["ia_memory"]["par_non_bias"]
        if abs(bias) > 5:
            ia_num = random.choice([2, 4, 6, 8, 10]) if bias > 0 else random.choice([1, 3, 5, 7, 9])
        else: ia_num = random.randint(1, 10)
        total = eleccion + ia_num
        es_par = (total % 2 == 0)
        print(f"\nTú: {eleccion} | {self.data['nombre']}: {ia_num}")
        print(f"Suma: {total} ({Color.CYAN}{'PAR' if es_par else 'IMPAR'}{Color.RESET})")
        if eleccion % 2 == 0: self.data["ia_memory"]["par_non_bias"] += 1
        else: self.data["ia_memory"]["par_non_bias"] -= 1
        self.data["juegos_stats"]["pares"] += 1
        self.data["hambre"] -= 3
        self.data["energia"] -= 4
        self.data["afecto"] += 2
        self.finalizar_juego("pares")

    def juego_adivina(self):
        print(f"\n{Color.CYAN}{Color.BOLD}🔢 Adivina el Número (1-100){Color.RESET}\n")
        target = random.randint(1, 100)
        intentos = 0
        while intentos < 10:
            try:
                guess = int(input(f"Intento {intentos+1}/10 (0 para salir): "))
                if guess == 0: break
            except: continue
            intentos += 1
            if guess == target:
                print(f"{Color.GREEN}¡CORRECTO en {intentos} intentos! 🎉{Color.RESET}")
                self.data["afecto"] += 12
                self.data["personalidad"]["amor_recibido"] += 3
                break
            elif guess < target: print(f"{Color.YELLOW}⬆️  Más alto{Color.RESET}")
            else: print(f"{Color.YELLOW}⬇️  Más bajo{Color.RESET}")
        else:
            print(f"{Color.RED}Game Over. Era {target}.{Color.RESET}")
            self.data["afecto"] += 1
        self.data["juegos_stats"]["adivina"] += 1
        self.data["hambre"] -= 8
        self.data["energia"] -= 10
        self.finalizar_juego("adivina")

    def juego_tictactoe(self):
        print(f"\n{Color.CYAN}{Color.BOLD}⭕ 3 en Raya{Color.RESET}\n")
        board = [" "] * 9
        def mostrar():
            print(f"\n  {board[0]} │ {board[1]} │ {board[2]}\n  ──┼───┼──\n  {board[3]} │ {board[4]} │ {board[5]}\n  ──┼───┼──\n  {board[6]} │ {board[7]} │ {board[8]}\n")
        mostrar()
        for turno in range(5):
            try:
                pos = int(input(f"Tu turno (0-8): "))
                if pos < 0 or pos > 8 or board[pos] != " ": continue
            except: continue
            board[pos] = "X"
            if self.check_win_ttt(board, "X"):
                mostrar()
                print(f"{Color.GREEN}¡GANASTE! 🎉{Color.RESET}")
                self.data["afecto"] += 8
                break
            if " " not in board:
                mostrar()
                print(f"{Color.YELLOW}¡EMPATE!{Color.RESET}")
                self.data["afecto"] += 3
                break
            move = self.get_move_ttt(board)
            board[move] = "O"
            mostrar()
            if self.check_win_ttt(board, "O"):
                print(f"{Color.RED}{self.data['nombre']} ganó. 😏{Color.RESET}")
                self.data["afecto"] += 1
                break
        self.data["juegos_stats"]["tictactoe"] += 1
        self.data["hambre"] -= 7
        self.data["energia"] -= 9
        self.finalizar_juego("tictactoe")

    def get_move_ttt(self, board):
        move = self.find_win_ttt(board, "O")
        if move != -1: return move
        move = self.find_win_ttt(board, "X")
        if move != -1: return move
        if board[4] == " ": return 4
        esquinas = [0, 2, 6, 8]
        random.shuffle(esquinas)
        for e in esquinas:
            if board[e] == " ": return e
        avail = [i for i, x in enumerate(board) if x == " "]
        return random.choice(avail)
    def find_win_ttt(self, board, player):
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in wins:
            linea = [board[a], board[b], board[c]]
            if linea.count(player) == 2 and linea.count(" ") == 1: return [a, b, c][linea.index(" ")]
        return -1
    def check_win_ttt(self, board, player):
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in wins:
            if board[a] == player and board[b] == player and board[c] == player: return True
        return False

    def finalizar_juego(self, tipo):
        self.data["historial"]["sesiones_juego"].append({"tipo": tipo, "timestamp": time.time()})
        self.actualizar_personalidad()
        self.check_limites()
        self.guardar_datos()
        print(f"\n{Color.GRAY}Afecto: {int(self.data['afecto'])} | Energía: {int(self.data['energia'])}%{Color.RESET}")

    def limpiar_pantalla(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def reset(self):
        if os.path.exists(FILE_DATA):
            os.remove(FILE_DATA)
            print(f"{Color.GREEN}+KOTA  ha sido reiniciado.{Color.RESET}")
        else: print(f"{Color.YELLOW}No hay datos para resetear.{Color.RESET}")

# ==========================================================
# MAIN
# ==========================================================
def main():
    if len(sys.argv) < 2:
        print(f"\n{Color.CYAN}{Color.BOLD}+KOTA - Mascota Virtual de Terminal{Color.RESET}")
        print(f"\n{Color.BOLD}Uso:{Color.RESET} python +KOTA.py [comando]\n")
        print(f"{Color.BOLD}Comandos disponibles:{Color.RESET}")
        print(f"  {Color.GREEN}estado{Color.RESET}           - Ver estado actual")
        print(f"  {Color.GREEN}alimentar{Color.RESET}        - Dar comida")
        print(f"  {Color.GREEN}acariciar{Color.RESET}        - Dar cariño")
        print(f"  {Color.GREEN}pasear{Color.RESET}           - Salir a caminar")
        print(f"  {Color.GREEN}dormir{Color.RESET}           - Dormir/Despertar")
        print(f"  {Color.GREEN}renombrar{Color.RESET} [nom] - Cambiar nombre")
        print(f"  {Color.GREEN}jugar{Color.RESET} [juego]   - Jugar (rps, pares, adivina, tictactoe)")
        print(f"  {Color.GREEN}stats{Color.RESET}            - Ver estadísticas")
        print(f"  {Color.GREEN}reset{Color.RESET}            - Reiniciar mascota\n")
        return

    comando = sys.argv[1].lower()
    pet = GeoPet()

    if comando == "estado": pet.mostrar_estado()
    elif comando == "alimentar": pet.alimentar()
    elif comando == "acariciar": pet.acariciar()
    elif comando == "pasear": pet.pasear()
    elif comando == "dormir": pet.dormir()
    elif comando == "renombrar":
        if len(sys.argv) < 3: print(f"{Color.RED}Debes escribir el nombre nuevo.{Color.RESET}")
        else: pet.renombrar(sys.argv[2])
    elif comando == "jugar":
        if len(sys.argv) < 3: print(f"{Color.RED}Especifica el juego.{Color.RESET}")
        else: pet.jugar(sys.argv[2].lower())
    elif comando == "stats": pet.mostrar_stats()
    elif comando == "reset":
        if input(f"{Color.YELLOW}¿Seguro? (s/n): {Color.RESET}").lower() == 's': pet.reset()
    else: print(f"{Color.RED}Comando no reconocido.{Color.RESET}")

if __name__ == "__main__":
    main()
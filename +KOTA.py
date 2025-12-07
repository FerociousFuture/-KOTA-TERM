#!/usr/bin/env python3
"""
+KOTA - Mascota Virtual de Terminal (Enhanced Edition)
Uso: python +KOTA.py [comando] [argumentos]

Comandos disponibles:
    estado          - Ver estado actual
    alimentar       - Dar comida del inventario
    dormir          - Poner a dormir / despertar
    jugar [juego]   - Jugar (rps, pares, adivina, tictactoe)
    acariciar       - Dar cariño para bajar estrés
    pasear          - Salir a caminar (gasta energía, sube felicidad)
    renombrar [nom] - Cambiar el nombre de la mascota
    tienda          - Acceder a la tienda
    inventario      - Ver tu inventario
    equipar [item]  - Equipar accesorio
    desequipar      - Quitar accesorio equipado
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

# --- CATÁLOGO DE TIENDA ---
TIENDA_ITEMS = {
    "comidas": {
        "manzana": {"precio": 5, "hambre": 20, "tipo": "comun", "emoji": "🍎"},
        "pizza": {"precio": 15, "hambre": 40, "tipo": "chatarra", "emoji": "🍕"},
        "ensalada": {"precio": 12, "hambre": 30, "tipo": "saludable", "emoji": "🥗"},
        "sushi": {"precio": 25, "hambre": 50, "tipo": "premium", "emoji": "🍣"},
        "dulce": {"precio": 8, "hambre": 15, "tipo": "chatarra", "emoji": "🍬"},
    },
    "pociones": {
        "energia_menor": {"precio": 20, "energia": 30, "emoji": "⚡"},
        "energia_mayor": {"precio": 40, "energia": 60, "emoji": "🔋"},
        "anti_estres": {"precio": 35, "estres": -40, "emoji": "😌"},
        "full_revive": {"precio": 100, "hambre": 100, "energia": 100, "afecto": 30, "estres": -50, "emoji": "💊"},
    },
    "accesorios": {
        "sombrero": {"precio": 50, "emoji": "🎩", "tipo": "cabeza"},
        "gafas": {"precio": 40, "emoji": "🕶️", "tipo": "cara"},
        "corbata": {"precio": 35, "emoji": "👔", "tipo": "cuello"},
        "corona": {"precio": 80, "emoji": "👑", "tipo": "cabeza"},
        "bufanda": {"precio": 45, "emoji": "🧣", "tipo": "cuello"},
    }
}

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
                "comida_chatarra": 0,
                "comida_saludable": 0,
                "comida_premium": 0,
            },
            "historial": {
                "alimentaciones": [],
                "sesiones_juego": [],
                "ciclos_sueno": [],
                "paseos": [] 
            },
            # NUEVOS SISTEMAS
            "nivel": 1,
            "exp": 0,
            "exp_max": 100,
            "monedas": 50,  # Monedas iniciales
            "inventario": {
                "comidas": {},
                "pociones": {},
                "accesorios": {}
            },
            "accesorio_equipado": None,
            "forma_evolucion": "basico",  # basico, atletico, intelectual, premium, rebelde
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

        if self.data["estado_dormido"]:
            decay_hambre = horas * 2.0 
            self.data["energia"] += horas * 12.5
            self.data["personalidad"]["privacion_sueno"] -= horas * 3
        else:
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
    # SISTEMA DE NIVELES Y EXPERIENCIA
    # ==========================================================
    def ganar_exp(self, cantidad):
        """Añade experiencia y gestiona subidas de nivel"""
        self.data["exp"] += cantidad
        
        while self.data["exp"] >= self.data["exp_max"]:
            self.data["exp"] -= self.data["exp_max"]
            self.data["nivel"] += 1
            self.data["exp_max"] = int(self.data["exp_max"] * 1.5)
            
            print(f"\n{Color.YELLOW}{Color.BOLD}✨ ¡NIVEL SUBIDO! ✨{Color.RESET}")
            print(f"{Color.GREEN}{self.data['nombre']} ahora es nivel {self.data['nivel']}!{Color.RESET}")
            
            # Recompensa por subir de nivel
            monedas_bonus = self.data["nivel"] * 10
            self.data["monedas"] += monedas_bonus
            print(f"{Color.CYAN}+{monedas_bonus} monedas de bonificación!{Color.RESET}\n")
        
        self.determinar_evolucion()

    def determinar_evolucion(self):
        """Determina la forma evolutiva basada en estadísticas complejas"""
        p = self.data["personalidad"]
        
        # Calcular puntos de cada categoría
        puntos = {
            "atletico": 0,
            "intelectual": 0,
            "premium": 0,
            "rebelde": 0
        }
        
        # Atlético: muchos paseos, energía alta, comida saludable
        if len(self.data["historial"].get("paseos", [])) > 10:
            puntos["atletico"] += 30
        if p.get("comida_saludable", 0) > 15:
            puntos["atletico"] += 25
        if self.data["energia"] > 70:
            puntos["atletico"] += 15
        
        # Intelectual: muchos juegos de estrategia, baja chatarra
        juegos_mentales = self.data["juegos_stats"].get("tictactoe", 0) + self.data["juegos_stats"].get("adivina", 0)
        if juegos_mentales > 15:
            puntos["intelectual"] += 40
        if p.get("comida_chatarra", 0) < 5:
            puntos["intelectual"] += 20
        if self.data["afecto"] > 60:
            puntos["intelectual"] += 15
        
        # Premium: comida premium, alto afecto, accesorios equipados
        if p.get("comida_premium", 0) > 10:
            puntos["premium"] += 40
        if self.data["afecto"] > 80:
            puntos["premium"] += 25
        if self.data["accesorio_equipado"]:
            puntos["premium"] += 20
        
        # Rebelde: mucha chatarra, poco sueño, bajo afecto
        if p.get("comida_chatarra", 0) > 20:
            puntos["rebelde"] += 35
        if p.get("privacion_sueno", 0) > 40:
            puntos["rebelde"] += 25
        if self.data["afecto"] < 20:
            puntos["rebelde"] += 30
        
        # Determinar forma dominante
        forma_anterior = self.data["forma_evolucion"]
        
        if self.data["nivel"] < 5:
            self.data["forma_evolucion"] = "basico"
        else:
            max_puntos = max(puntos.values())
            if max_puntos > 50:
                self.data["forma_evolucion"] = max(puntos, key=puntos.get)
            else:
                self.data["forma_evolucion"] = "basico"
        
        if forma_anterior != self.data["forma_evolucion"] and self.data["nivel"] >= 5:
            print(f"\n{Color.MAGENTA}{Color.BOLD}🌟 ¡EVOLUCIÓN! 🌟{Color.RESET}")
            print(f"{Color.CYAN}{self.data['nombre']} ha evolucionado a forma {self.data['forma_evolucion'].upper()}!{Color.RESET}\n")

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
        """Retorna forma basada en evolución"""
        forma_map = {
            "basico": "circle",
            "atletico": "triangle",
            "intelectual": "square",
            "premium": "hexagon",
            "rebelde": "pentagon"
        }
        return forma_map.get(self.data["forma_evolucion"], "circle")

    def get_color_ascii(self):
        p = self.data["personalidad"]
        if self.data["estado_dormido"]: return Color.BLUE
        
        # Color basado en evolución
        if self.data["forma_evolucion"] == "premium": return Color.MAGENTA
        if self.data["forma_evolucion"] == "atletico": return Color.GREEN
        if self.data["forma_evolucion"] == "intelectual": return Color.CYAN
        if self.data["forma_evolucion"] == "rebelde": return Color.RED
        
        # Color basado en salud
        salud = (self.data["hambre"] + self.data["energia"]) / 2
        if p["estres"] > 70: return Color.RED
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
        
        # Mostrar accesorio si está equipado
        accesorio = ""
        if self.data["accesorio_equipado"]:
            item_data = TIENDA_ITEMS["accesorios"].get(self.data["accesorio_equipado"])
            if item_data:
                accesorio = item_data["emoji"]
        
        print(f"\n{color}{Color.BOLD}", end="")
        if forma == "triangle": self.dibujar_triangulo(expresion, accesorio)
        elif forma == "square": self.dibujar_cuadrado(expresion, accesorio)
        elif forma == "pentagon": self.dibujar_pentagono(expresion, accesorio)
        elif forma == "hexagon": self.dibujar_hexagono(expresion, accesorio)
        else: self.dibujar_circulo(expresion, accesorio)
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

    # Métodos de dibujo específicos (con accesorio)
    def dibujar_triangulo(self, e, acc):
        c, o = self.get_cara_ascii(e)
        print(f"        △ {acc}")
        print(f"       ╱ ╲")
        print(f"      ╱{c}╲")
        print(f"     ╱ {o} ╲")
        print(f"    ╱       ╲")
        print(f"   ╱─────────╲")
    
    def dibujar_cuadrado(self, e, acc):
        c, o = self.get_cara_ascii(e)
        print(f"   ┌─────────┐ {acc}")
        print(f"   │         │")
        print(f"   │  {c}  │")
        print(f"   │  {o}  │")
        print(f"   │         │")
        print(f"   └─────────┘")
    
    def dibujar_pentagono(self, e, acc):
        c, o = self.get_cara_ascii(e)
        print(f"      ╱‾‾‾╲ {acc}")
        print(f"     ╱     ╲")
        print(f"    │  {c}  │")
        print(f"    │  {o}  │")
        print(f"     ╲     ╱")
        print(f"      ╲___╱")
    
    def dibujar_hexagono(self, e, acc):
        c, o = self.get_cara_ascii(e)
        print(f"     ╱‾‾‾‾‾╲ {acc}")
        print(f"    ╱       ╲")
        print(f"   │   {c}   │")
        print(f"   │   {o}   │")
        print(f"    ╲       ╱")
        print(f"     ╲_____╱")
    
    def dibujar_circulo(self, e, acc):
        c, o = self.get_cara_ascii(e)
        print(f"     ╭─────╮ {acc}")
        print(f"    ╱       ╲")
        print(f"   │   {c}   │")
        print(f"   │   {o}   │")
        print(f"    ╲       ╱")
        print(f"     ╰─────╯")

    # ==========================================================
    # SISTEMA DE TIENDA
    # ==========================================================
    def mostrar_tienda(self):
        """Muestra la tienda interactiva"""
        self.limpiar_pantalla()
        while True:
            print(f"\n{Color.CYAN}{Color.BOLD}╔═══════════════════════════════════════╗{Color.RESET}")
            print(f"{Color.CYAN}{Color.BOLD}║          🏪  TIENDA +KOTA             ║{Color.RESET}")
            print(f"{Color.CYAN}{Color.BOLD}╚═══════════════════════════════════════╝{Color.RESET}")
            print(f"\n{Color.YELLOW}💰 Monedas: {self.data['monedas']}{Color.RESET}\n")
            
            print(f"{Color.BOLD}Categorías:{Color.RESET}")
            print(f"  1. Comidas")
            print(f"  2. Pociones")
            print(f"  3. Accesorios")
            print(f"  0. Salir\n")
            
            opcion = input(f"{Color.CYAN}Elige categoría: {Color.RESET}").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                self.tienda_categoria("comidas")
            elif opcion == "2":
                self.tienda_categoria("pociones")
            elif opcion == "3":
                self.tienda_categoria("accesorios")
            else:
                print(f"{Color.RED}Opción no válida{Color.RESET}")
                time.sleep(1)

    def tienda_categoria(self, categoria):
        """Muestra items de una categoría"""
        items = TIENDA_ITEMS[categoria]
        
        while True:
            self.limpiar_pantalla()
            print(f"\n{Color.CYAN}{Color.BOLD}══ {categoria.upper()} ══{Color.RESET}")
            print(f"{Color.YELLOW}💰 Monedas: {self.data['monedas']}{Color.RESET}\n")
            
            lista_items = list(items.keys())
            for i, nombre in enumerate(lista_items, 1):
                item = items[nombre]
                emoji = item.get("emoji", "")
                print(f"  {i}. {emoji} {nombre.capitalize():15} - {Color.YELLOW}{item['precio']}💰{Color.RESET}")
            
            print(f"  0. Volver\n")
            
            try:
                opcion = input(f"{Color.CYAN}Comprar (número): {Color.RESET}").strip()
                if opcion == "0":
                    break
                
                idx = int(opcion) - 1
                if 0 <= idx < len(lista_items):
                    nombre_item = lista_items[idx]
                    self.comprar_item(categoria, nombre_item, items[nombre_item])
                else:
                    print(f"{Color.RED}Opción no válida{Color.RESET}")
                    time.sleep(1)
            except:
                print(f"{Color.RED}Entrada no válida{Color.RESET}")
                time.sleep(1)

    def comprar_item(self, categoria, nombre, item_data):
        """Compra un item"""
        precio = item_data["precio"]
        
        if self.data["monedas"] < precio:
            print(f"{Color.RED}¡No tienes suficientes monedas!{Color.RESET}")
            time.sleep(2)
            return
        
        # Realizar compra
        self.data["monedas"] -= precio
        
        if nombre not in self.data["inventario"][categoria]:
            self.data["inventario"][categoria][nombre] = 0
        self.data["inventario"][categoria][nombre] += 1
        
        emoji = item_data.get("emoji", "")
        print(f"\n{Color.GREEN}✅ ¡Compraste {emoji} {nombre}!{Color.RESET}")
        print(f"{Color.GRAY}Te quedan {self.data['monedas']} monedas{Color.RESET}")
        
        self.guardar_datos()
        time.sleep(2)

    def mostrar_inventario(self):
        """Muestra el inventario del jugador"""
        self.limpiar_pantalla()
        print(f"\n{Color.CYAN}{Color.BOLD}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}║           📦  INVENTARIO              ║{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}╚═══════════════════════════════════════╝{Color.RESET}\n")
        
        vacio = True
        
        for categoria, items in self.data["inventario"].items():
            if items:
                vacio = False
                print(f"{Color.BOLD}{categoria.upper()}:{Color.RESET}")
                for nombre, cantidad in items.items():
                    if cantidad > 0:
                        item_data = TIENDA_ITEMS[categoria].get(nombre, {})
                        emoji = item_data.get("emoji", "")
                        print(f"  {emoji} {nombre.capitalize():15} x{cantidad}")
                print()
        
        if vacio:
            print(f"{Color.GRAY}Tu inventario está vacío.{Color.RESET}")
            print(f"{Color.CYAN}¡Visita la tienda para comprar items!{Color.RESET}")
        
        print()

    def usar_comida(self):
        """Alimenta con comida del inventario"""
        if self.data["estado_dormido"]:
            print(f"{Color.YELLOW}+KOTA está durmiendo profundamente.{Color.RESET}")
            return
        
        comidas = self.data["inventario"]["comidas"]
        if not comidas or all(c == 0 for c in comidas.values()):
            print(f"{Color.RED}No tienes comida. ¡Visita la tienda!{Color.RESET}")
            return
        
        print(f"\n{Color.CYAN}Comidas disponibles:{Color.RESET}")
        lista = [(n, c) for n, c in comidas.items() if c > 0]
        for i, (nombre, cant) in enumerate(lista, 1):
            item = TIENDA_ITEMS["comidas"][nombre]
            print(f"  {i}. {item['emoji']} {nombre.capitalize()} x{cant}")
        
        try:
            idx = int(input(f"\n{Color.CYAN}Usar (número): {Color.RESET}")) - 1
            if 0 <= idx < len(lista):
                nombre, _ = lista[idx]
                item = TIENDA_ITEMS["comidas"][nombre]
                
                self.data["hambre"] += item["hambre"]
                self.data["inventario"]["comidas"][nombre] -= 1
                self.data["afecto"] += 3
                
                # Registrar tipo de comida
                tipo = item.get("tipo", "comun")
                if tipo == "chatarra":
                    self.data["personalidad"]["comida_chatarra"] += 1
                elif tipo == "saludable":
                    self.data["personalidad"]["comida_saludable"] += 1
                elif tipo == "premium":
                    self.data["personalidad"]["comida_premium"] += 1
                
                self.data["historial"]["alimentaciones"].append(time.time())
                print(f"\n{Color.GREEN}¡{self.data['nombre']} comió {item['emoji']} {nombre}!{Color.RESET}")
                print(f"{Color.MAGENTA}(Hambre +{item['hambre']}, Afecto +3){Color.RESET}")
                
                self.actualizar_personalidad()
                self.check_limites()
                self.determinar_evolucion()
                self.guardar_datos()
                self.mostrar_estado()
        except:
            print(f"{Color.RED}Opción no válida{Color.RESET}")

    def equipar_accesorio(self, nombre):
        """Equipa un accesorio"""
        if nombre not in self.data["inventario"]["accesorios"] or self.data["inventario"]["accesorios"][nombre] == 0:
            print(f"{Color.RED}No tienes ese accesorio en el inventario.{Color.RESET}")
            return
        
        self.data["accesorio_equipado"] = nombre
        item = TIENDA_ITEMS["accesorios"][nombre]
        print(f"\n{Color.GREEN}¡{self.data['nombre']} ahora lleva {item['emoji']} {nombre}!{Color.RESET}")
        self.guardar_datos()
        self.mostrar_estado()

    def desequipar_accesorio(self):
        """Quita el accesorio equipado"""
        if not self.data["accesorio_equipado"]:
            print(f"{Color.YELLOW}No hay ningún accesorio equipado.{Color.RESET}")
            return
        
        nombre = self.data["accesorio_equipado"]
        self.data["accesorio_equipado"] = None
        print(f"\n{Color.CYAN}Se quitó {nombre}.{Color.RESET}")
        self.guardar_datos()
        self.mostrar_estado()

    # ==========================================================
    # COMANDOS EXISTENTES (modificados)
    # ==========================================================
    def mostrar_estado(self):
        self.limpiar_pantalla()
        print(f"\n{Color.CYAN}{Color.BOLD}╔═══════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}║       +KOTA  - Estado Actual          ║{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}╚═══════════════════════════════════════╝{Color.RESET}\n")
        self.dibujar()
        p = self.data["personalidad"]
        
        # Barra de nivel
        exp_porcentaje = (self.data["exp"] / self.data["exp_max"]) * 100
        print(f"\n{Color.BOLD}Nombre:{Color.RESET} {self.data['nombre']}")
        print(f"{Color.BOLD}Nivel:{Color.RESET} {self.data['nivel']} | {Color.BOLD}Forma:{Color.RESET} {self.data['forma_evolucion'].upper()}")
        print(f"{Color.BOLD}Exp:{Color.RESET} [{self.crear_barra_mini(exp_porcentaje)}] {self.data['exp']}/{self.data['exp_max']}")
        print(f"{Color.YELLOW}💰 {self.data['monedas']} monedas{Color.RESET}")
        print(f"{Color.BOLD}Estado:{Color.RESET} {self.get_estado_texto()}\n")
        
        self.dibujar_barra("Hambre", self.data["hambre"], Color.GREEN)
        self.dibujar_barra("Energía", self.data["energia"], Color.CYAN)
        afecto_norm = (self.data["afecto"] + 100) / 2
        self.dibujar_barra("Afecto", afecto_norm, Color.MAGENTA)
        print(f"\n{Color.GRAY}Estrés: {int(p['estres'])}% | Privación Sueño: {int(p['privacion_sueno'])}%{Color.RESET}")
        
        if self.data["accesorio_equipado"]:
            item = TIENDA_ITEMS["accesorios"].get(self.data["accesorio_equipado"])
            if item:
                print(f"{Color.GRAY}Equipado: {item['emoji']} {self.data['accesorio_equipado']}{Color.RESET}")
        
        hora = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Color.GRAY}[{hora}]{Color.RESET}")

    def crear_barra_mini(self, porcentaje):
        """Crea una mini barra de progreso"""
        largo = 10
        lleno = int((porcentaje / 100) * largo)
        return "█" * lleno + "░" * (largo - lleno)

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
        
        if self.data["afecto"] < -20:
            print(f"{Color.RED}{self.data['nombre']} se aparta. No quiere que lo toques.{Color.RESET}")
            self.data["afecto"] += 0.5
        elif self.data["afecto"] < 20:
            print(f"{Color.CYAN}Acaricias a {self.data['nombre']}. Se deja hacer, pero no parece emocionado.{Color.RESET}")
            self.data["afecto"] += 2
            self.data["personalidad"]["estres"] -= 2
        else:
            print(f"{Color.MAGENTA}¡A {self.data['nombre']} le encanta! Ronronea (o vibra) de felicidad.{Color.RESET}")
            self.data["afecto"] += 4
            self.data["personalidad"]["estres"] -= 5
            self.data["personalidad"]["amor_recibido"] += 1
        
        self.ganar_exp(5)
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

        self.data["energia"] -= 25
        self.data["hambre"] -= 20
        self.data["afecto"] += 10
        self.data["personalidad"]["estres"] -= 15
        
        if "paseos" not in self.data["historial"]: self.data["historial"]["paseos"] = []
        self.data["historial"]["paseos"].append(time.time())

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
        
        self.ganar_exp(15)
        self.actualizar_personalidad()
        self.check_limites()
        self.guardar_datos()

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
        
        print(f"{Color.BOLD}📊 Progreso:{Color.RESET}")
        print(f"  • Nivel             : {self.data['nivel']}")
        print(f"  • Experiencia       : {self.data['exp']}/{self.data['exp_max']}")
        print(f"  • Forma Evolutiva   : {self.data['forma_evolucion'].upper()}")
        print(f"  • Monedas           : {self.data['monedas']}💰")
        
        print(f"\n{Color.BOLD}🎮 Actividad:{Color.RESET}")
        for juego, count in self.data["juegos_stats"].items():
            print(f"  • {juego:12} : {count} veces")
        
        print(f"\n{Color.BOLD}🧠 Personalidad:{Color.RESET}")
        print(f"  • Juego Favorito    : {p['juego_favorito'].upper()}")
        print(f"  • Amor Recibido     : {int(p['amor_recibido'])} puntos")
        print(f"  • Estrés            : {int(p['estres'])}%")
        print(f"  • Comida Chatarra   : {p.get('comida_chatarra', 0)}")
        print(f"  • Comida Saludable  : {p.get('comida_saludable', 0)}")
        print(f"  • Comida Premium    : {p.get('comida_premium', 0)}")
        
        print(f"\n{Color.BOLD}📜 Historial:{Color.RESET}")
        print(f"  • Alimentaciones    : {len(h['alimentaciones'])} veces")
        print(f"  • Sesiones de Juego : {len(h['sesiones_juego'])} veces")
        print(f"  • Paseos            : {num_paseos} veces")
        
        if len(h["alimentaciones"]) > 0:
            tiempo_total = (time.time() - h["alimentaciones"][0]) / 3600
            print(f"\n{Color.GRAY}Edad aprox: {tiempo_total:.1f} horas{Color.RESET}")

    # ==========================================================
    # JUEGOS (con recompensas)
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
        
        monedas = 0
        exp = 0
        if ganador == "empate":
            print(f"{Color.YELLOW}¡EMPATE!{Color.RESET}")
            self.data["afecto"] += 1
            monedas = 3
            exp = 5
        elif ganador == "usuario":
            print(f"{Color.GREEN}¡GANASTE! 🎉{Color.RESET}")
            self.data["afecto"] += 6
            self.data["personalidad"]["amor_recibido"] += 2
            monedas = 10
            exp = 15
        else:
            print(f"{Color.RED}{self.data['nombre']} ganó... 😏{Color.RESET}")
            self.data["afecto"] -= 1
            monedas = 2
            exp = 3
        
        self.data["monedas"] += monedas
        print(f"{Color.YELLOW}+{monedas}💰 | +{exp} EXP{Color.RESET}")
        
        history.append(eleccion)
        if len(history) > 30: history.pop(0)
        self.data["juegos_stats"]["rps"] += 1
        self.data["hambre"] -= 4
        self.data["energia"] -= 6
        self.ganar_exp(exp)
        self.finalizar_juego("rps")

    def predecir_rps(self, secuencia, history):
        for i in range(len(history) - 3):
            if history[i:i+3] == secuencia and i+3 < len(history):
                return self.counter_rps(history[i+3])
        conteo = {'R': history.count('R'), 'P': history.count('P'), 'T': history.count('T')}
        return self.counter_rps(max(conteo, key=conteo.get))
    
    def counter_rps(self, jugada): 
        return {'R': 'P', 'P': 'T', 'T': 'R'}[jugada]
    
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
        
        monedas = 5
        exp = 8
        self.data["monedas"] += monedas
        print(f"{Color.YELLOW}+{monedas}💰 | +{exp} EXP{Color.RESET}")
        
        self.data["juegos_stats"]["pares"] += 1
        self.data["hambre"] -= 3
        self.data["energia"] -= 4
        self.data["afecto"] += 2
        self.ganar_exp(exp)
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
                monedas = max(20, 50 - intentos * 3)
                exp = max(25, 40 - intentos * 2)
                self.data["monedas"] += monedas
                print(f"{Color.YELLOW}+{monedas}💰 | +{exp} EXP{Color.RESET}")
                self.ganar_exp(exp)
                break
            elif guess < target: print(f"{Color.YELLOW}⬆️  Más alto{Color.RESET}")
            else: print(f"{Color.YELLOW}⬇️  Más bajo{Color.RESET}")
        else:
            print(f"{Color.RED}Game Over. Era {target}.{Color.RESET}")
            self.data["afecto"] += 1
            monedas = 5
            self.data["monedas"] += monedas
            print(f"{Color.YELLOW}+{monedas}💰{Color.RESET}")
        
        self.data["juegos_stats"]["adivina"] += 1
        self.data["hambre"] -= 8
        self.data["energia"] -= 10
        self.finalizar_juego("adivina")

    def juego_tictactoe(self):
        print(f"\n{Color.CYAN}{Color.BOLD}⭕ 3 en Raya{Color.RESET}\n")
        board = [" "] * 9
        def mostrar():
            print(f"\n  {board[0]} │ {board[1]} │ {board[2]}\n  ──┼───┼──\n  {board[3]} │ {board[4]} │ {board[5]}\n  ──┼───┼──\n  {board[6]} │ {board[7]} │ {board[8]}\n")
        
        monedas = 0
        exp = 0
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
                monedas = 15
                exp = 20
                break
            if " " not in board:
                mostrar()
                print(f"{Color.YELLOW}¡EMPATE!{Color.RESET}")
                self.data["afecto"] += 3
                monedas = 8
                exp = 10
                break
            move = self.get_move_ttt(board)
            board[move] = "O"
            mostrar()
            if self.check_win_ttt(board, "O"):
                print(f"{Color.RED}{self.data['nombre']} ganó. 😏{Color.RESET}")
                self.data["afecto"] += 1
                monedas = 5
                exp = 5
                break
        
        if monedas > 0:
            self.data["monedas"] += monedas
            print(f"{Color.YELLOW}+{monedas}💰 | +{exp} EXP{Color.RESET}")
            self.ganar_exp(exp)
        
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
        print(f"  {Color.GREEN}alimentar{Color.RESET}        - Dar comida del inventario")
        print(f"  {Color.GREEN}acariciar{Color.RESET}        - Dar cariño")
        print(f"  {Color.GREEN}pasear{Color.RESET}           - Salir a caminar")
        print(f"  {Color.GREEN}dormir{Color.RESET}           - Dormir/Despertar")
        print(f"  {Color.GREEN}renombrar{Color.RESET} [nom] - Cambiar nombre")
        print(f"  {Color.GREEN}jugar{Color.RESET} [juego]   - Jugar (rps, pares, adivina, tictactoe)")
        print(f"  {Color.GREEN}tienda{Color.RESET}           - Acceder a la tienda")
        print(f"  {Color.GREEN}inventario{Color.RESET}       - Ver tu inventario")
        print(f"  {Color.GREEN}equipar{Color.RESET} [item]  - Equipar accesorio")
        print(f"  {Color.GREEN}desequipar{Color.RESET}       - Quitar accesorio")
        print(f"  {Color.GREEN}stats{Color.RESET}            - Ver estadísticas")
        print(f"  {Color.GREEN}reset{Color.RESET}            - Reiniciar mascota\n")
        return

    comando = sys.argv[1].lower()
    pet = GeoPet()

    if comando == "estado": pet.mostrar_estado()
    elif comando == "alimentar": pet.usar_comida()
    elif comando == "acariciar": pet.acariciar()
    elif comando == "pasear": pet.pasear()
    elif comando == "dormir": pet.dormir()
    elif comando == "tienda": pet.mostrar_tienda()
    elif comando == "inventario": pet.mostrar_inventario()
    elif comando == "equipar":
        if len(sys.argv) < 3: print(f"{Color.RED}Especifica el accesorio.{Color.RESET}")
        else: pet.equipar_accesorio(sys.argv[2])
    elif comando == "desequipar": pet.desequipar_accesorio()
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
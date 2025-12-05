# +KOTA 
### Mascota Virtual de Terminal

Una mascota virtual tipo Tamagotchi que vive en tu terminal, aprende de tus acciones y desarrolla personalidad única.

---

## Instalación Rápida

### 1. Descargar los archivos

```bash
# Clona el repositorio o descarga los archivos
git clone https://github.com/tu-usuario/+KOTA.git
cd +KOTA
```

### 2. Dar permisos de ejecución

```bash
chmod +x +KOTA.py
chmod +x +KOTA_STATUS.py
```

### 3. Agregar monitor automático al terminal

**Para Bash:**
```bash
echo "" >> ~/.bashrc
echo "# +KOTA Monitor" >> ~/.bashrc
echo "python3 $(pwd)/+KOTA_STATUS.py" >> ~/.bashrc
source ~/.bashrc
```

**Para Zsh:**
```bash
echo "" >> ~/.zshrc
echo "# +KOTA Monitor" >> ~/.zshrc
echo "python3 $(pwd)/+KOTA_STATUS.py" >> ~/.zshrc
source ~/.zshrc
```

### 4. (Opcional) Crear alias para facilitar uso

```bash
# Agregar al final de ~/.bashrc o ~/.zshrc
echo "alias kota='python3 $(pwd)/+KOTA.py'" >> ~/.bashrc
source ~/.bashrc
```

---

## Uso Básico

### Sin alias:
```bash
python3 +KOTA.py estado          # Ver estado
python3 +KOTA.py alimentar       # Dar comida
python3 +KOTA.py jugar rps       # Jugar
```

### Con alias:
```bash
kota estado          # Ver estado
kota alimentar       # Dar comida
kota jugar rps       # Jugar
kota pasear          # Salir a caminar
kota acariciar       # Dar cariño
kota dormir          # Dormir/Despertar
```

---

## Comandos Disponibles

```
estado              Ver estado completo con gráfico ASCII
alimentar           Dar comida (+25-35 hambre, +3 afecto)
acariciar           Reducir estrés (-5) y aumentar afecto (+4)
pasear              Salir a caminar (-25 energía, +10 afecto, -15 estrés)
dormir              Poner a dormir o despertar
renombrar [nombre]  Cambiar el nombre de tu mascota
jugar [tipo]        Jugar minijuegos (rps, pares, adivina, tictactoe)
stats               Ver estadísticas detalladas
reset               Reiniciar mascota (borra todo)
```

---

## Juegos

- **rps** - Piedra, Papel o Tijera (la IA aprende tus patrones)
- **pares** - Pares o Nones (desarrolla sesgo adaptativo)
- **adivina** - Adivina el número del 1-100
- **tictactoe** - 3 en Raya (IA estratégica)

---

## Monitor en Terminal

Cada vez que abras una nueva terminal, verás algo como:

```
   ● Beyonder  ::  🍖 100%  ⚡ 85%  🧠 15%  ❤️  75%  [Activo]
```

**Indicadores:**
- 🍖 Hambre (🟢>70% 🟡30-70% 🔴<30%)
- ⚡ Energía (🟢>70% 🟡30-70% 🔴<30%)
- 🧠 Estrés (🟢<30% 🟡30-60% 🔴>60%)
- ❤️ Afecto (0-100%)
- Estado: Activo / Dormido 💤 / Muerto 💀

---

## Advertencias

Tu mascota **escapará** si:
- El afecto cae por debajo de **-70**
- El maltrato acumulado supera **150 puntos**

**Causas de maltrato:**
- Sobrealimentar cuando está lleno
- Despertarlo muy pronto (<4 horas)
- Dejarlo con hambre crítica prolongada
- Tenerlo despierto de madrugada sin energía

---

## 🔧 Requisitos

- **Python 3.6+**
- Sistema Linux/Unix con terminal
- Solo usa biblioteca estándar (sin dependencias extra)

---

## Estructura de Archivos

```
+KOTA/
├── +KOTA.py              # Programa principal
├── +KOTA_STATUS.py       # Monitor para terminal
├── mascota_savegame.json # Guardado automático
└── README.md             # Este archivo
```

---


## Desinstalación

```bash
# 1. Remover líneas de ~/.bashrc o ~/.zshrc
nano ~/.bashrc  # Elimina las líneas de +KOTA

# 2. Eliminar archivos
rm +KOTA.py +KOTA_STATUS.py mascota_savegame.json

# 3. Recargar terminal
source ~/.bashrc
```

---

¡Cuida bien de tu +KOTA! 

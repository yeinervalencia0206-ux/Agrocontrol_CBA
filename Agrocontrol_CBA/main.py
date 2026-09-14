import json
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

# Configuración de rutas y archivos según la estructura requerida
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_PRODUCTOS = DATA_DIR / "productos.json"
FILE_LOTES = DATA_DIR / "lotes.json"
FILE_MOVIMIENTOS = DATA_DIR / "movimientos.json"
FILE_VENTAS = DATA_DIR / "ventas.json"

# Estructuras de datos en memoria
productos = {}
lotes = {}
movimientos = {}
ventas = {}

def cargar_datos():
    """Carga todos los datos desde los archivos JSON en la carpeta data/."""
    global productos, lotes, movimientos, ventas
    
    # Productos
    try:
        if FILE_PRODUCTOS.exists():
            with open(FILE_PRODUCTOS, "r", encoding="utf-8") as f:
                productos = json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error al cargar productos.json: {e}")
        productos = {}

    # Lotes
    try:
        if FILE_LOTES.exists():
            with open(FILE_LOTES, "r", encoding="utf-8") as f:
                lotes = json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error al cargar lotes.json: {e}")
        lotes = {}

    # Movimientos
    try:
        if FILE_MOVIMIENTOS.exists():
            with open(FILE_MOVIMIENTOS, "r", encoding="utf-8") as f:
                movimientos = json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error al cargar movimientos.json: {e}")
        movimientos = {}

    # Ventas
    try:
        if FILE_VENTAS.exists():
            with open(FILE_VENTAS, "r", encoding="utf-8") as f:
                ventas = json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error al cargar ventas.json: {e}")
        ventas = {}
        
    print(Fore.CYAN + "¡Datos cargados correctamente desde la carpeta data/!")

def guardar_datos():
    """Guarda todos los diccionarios actuales en sus respectivos archivos JSON."""
    try:
        with open(FILE_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=4, ensure_ascii=False)
        with open(FILE_LOTES, "w", encoding="utf-8") as f:
            json.dump(lotes, f, indent=4, ensure_ascii=False)
        with open(FILE_MOVIMIENTOS, "w", encoding="utf-8") as f:
            json.dump(movimientos, f, indent=4, ensure_ascii=False)
        with open(FILE_VENTAS, "w", encoding="utf-8") as f:
            json.dump(ventas, f, indent=4, ensure_ascii=False)
        print(Fore.GREEN + "¡Datos guardados exitosamente en formato JSON!")
    except Exception as e:
        print(Fore.RED + f"Error al guardar los datos: {e}")
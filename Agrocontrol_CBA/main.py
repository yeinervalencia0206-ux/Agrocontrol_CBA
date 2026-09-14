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
        
def calcular_stock(codigo_producto):
    """Calcula el stock actual a partir de los movimientos registrados (Regla de negocio 3)."""
    stock = 0
    for mov in movimientos.values():
        if mov["producto_codigo"] == codigo_producto:
            if mov["tipo"] == "ENTRADA":
                stock += mov["cantidad"]
            elif mov["tipo"] == "SALIDA":
                stock -= mov["cantidad"]
    return stock

def generar_id_movimiento():
    """Genera un identificador secuencial para los movimientos, ej. M0001."""
    nuevo_num = len(movimientos) + 1
    return f"M{nuevo_num:04d}"

def generar_id_venta():
    """Genera un identificador secuencial para las ventas, ej. V0001."""
    nuevo_num = len(ventas) + 1
    return f"V{nuevo_num:04d}"

def menu_gestion_productos():
    while True:
        print(Fore.YELLOW + Style.BRIGHT + "\n--- GESTIÓN DE PRODUCTOS ---" + Style.RESET_ALL)
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Actualizar producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            codigo = input("Ingrese el código del producto (ej. P001): ").strip().upper()
            if not codigo:
                print(Fore.RED + "El código no puede estar vacío.")
                continue
            if codigo in productos:
                print(Fore.RED + "El producto ya existe (RF01).")
                continue
            
            nombre = input("Nombre del producto: ").strip()
            categoria = input("Categoría: ").strip()
            unidad = input("Unidad de medida (ej. unidad, kg): ").strip()
            
            try:
                precio = float(input("Precio unitario: "))
                if precio <= 0:
                    print(Fore.RED + "El precio debe ser mayor a 0 (RF01).")
                    continue
                stock_minimo = int(input("Stock mínimo: "))
                if stock_minimo < 0:
                    print(Fore.RED + "El stock mínimo no puede ser negativo (RF01).")
                    continue
                
                productos[codigo] = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "categoria": categoria,
                    "unidad": unidad,
                    "precio": precio,
                    "stock_minimo": stock_minimo,
                    "activo": True
                }
                guardar_datos()
                print(Fore.GREEN + "¡Producto registrado con éxito!")
            except ValueError:
                print(Fore.RED + "Error: Ingrese valores numéricos válidos (RF18).")
                
        elif opcion == "2":
            print(Fore.CYAN + "\n--- LISTA DE PRODUCTOS ---")
            if not productos:
                print("No hay productos registrados.")
            else:
                filtro = input("Buscar por código o parte del nombre (Enter para ver todos): ").strip().lower()
                encontrados = False
                for cod, p in productos.items():
                    if not filtro or filtro in cod.lower() or filtro in p['nombre'].lower():
                        stock_actual = calcular_stock(cod)
                        estado = "Activo" if p['activo'] else "Inactivo"
                        print(f"[{p['codigo']}] {p['nombre']} | Cat: {p['categoria']} | Precio: ${p['precio']} | Stock Actual: {stock_actual} | Min: {p['stock_minimo']} | Estado: {estado}")
                        encontrados = True
                if not encontrados:
                    print(Fore.YELLOW + "No se encontraron productos con ese criterio.")
                    
        elif opcion == "3":
            codigo = input("Ingrese el código del producto a actualizar: ").strip().upper()
            if codigo not in productos:
                print(Fore.RED + "El producto no existe.")
                continue
            
            p = productos[codigo]
            print(f"Actualizando producto: {p['nombre']}. Deje en blanco para mantener el valor actual.")
            
            nuevo_nombre = input(f"Nuevo nombre [{p['nombre']}]: ").strip()
            if nuevo_nombre: p['nombre'] = nuevo_nombre
            
            nueva_cat = input(f"Nueva categoría [{p['categoria']}]: ").strip()
            if nueva_cat: p['categoria'] = nueva_cat
            
            nueva_un = input(f"Nueva unidad [{p['unidad']}]: ").strip()
            if nueva_un: p['unidad'] = nueva_un
            
            nuevo_precio = input(f"Nuevo precio [{p['precio']}]: ").strip()
            if nuevo_precio:
                try:
                    val = float(nuevo_precio)
                    if val > 0: p['precio'] = val
                    else: print(Fore.RED + "Precio inválido, se mantiene el anterior.")
                except ValueError: print(Fore.RED + "Valor no numérico, se mantiene el anterior.")
                
            nuevo_smin = input(f"Nuevo stock mínimo [{p['stock_minimo']}]: ").strip()
            if nuevo_smin:
                try:
                    val = int(nuevo_smin)
                    if val >= 0: p['stock_minimo'] = val
                    else: print(Fore.RED + "Stock mínimo inválido, se mantiene el anterior.")
                except ValueError: print(Fore.RED + "Valor no numérico, se mantiene el anterior.")
                
            guardar_datos()
            print(Fore.GREEN + "¡Producto actualizado correctamente (RF03)!")
            
        elif opcion == "4":
            codigo = input("Ingrese el código del producto a desactivar: ").strip().upper()
            if codigo not in productos:
                print(Fore.RED + "El producto no existe.")
                continue
            productos[codigo]['activo'] = False
            guardar_datos()
            print(Fore.GREEN + "¡Producto desactivado correctamente (RF04)! Se conserva su historial.")
            
        elif opcion == "0":
            break
        else:
            print(Fore.RED + "Opción inválida.")
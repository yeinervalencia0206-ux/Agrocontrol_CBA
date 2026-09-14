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
            
def menu_gestion_lotes():
    while True:
        print(Fore.YELLOW + Style.BRIGHT + "\n--- GESTIÓN DE LOTES PRODUCTIVOS ---" + Style.RESET_ALL)
        print("1. Registrar lote")
        print("2. Consultar lotes")
        print("3. Registrar proceso de cosecha")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            id_lote = input("Identificador del lote (ej. L001): ").strip().upper()
            if not id_lote:
                print(Fore.RED + "El ID no puede estar vacío.")
                continue
            if id_lote in lotes:
                print(Fore.RED + "El lote ya existe.")
                continue
                
            prod_cod = input("Código del producto asociado: ").strip().upper()
            if prod_cod not in productos or not productos[prod_cod]['activo']:
                print(Fore.RED + "El producto no existe o está inactivo (RF05).")
                continue
                
            fecha_siembra = input("Fecha de siembra (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(fecha_siembra, "%Y-%m-%d")
            except ValueError:
                print(Fore.RED + "Formato de fecha inválido. Use YYYY-MM-DD.")
                continue
                
            try:
                area_m2 = float(input("Área en metros cuadrados (m2): "))
                if area_m2 <= 0:
                    print(Fore.RED + "El área debe ser mayor a 0.")
                    continue
                
                lotes[id_lote] = {
                    "id_lote": id_lote,
                    "producto_codigo": prod_cod,
                    "fecha_siembra": fecha_siembra,
                    "area_m2": area_m2,
                    "cantidad_producida": 0,
                    "estado": "EN_PRODUCCION"
                }
                guardar_datos()
                print(Fore.GREEN + "¡Lote registrado exitosamente (RF05)! Estado: EN_PRODUCCION.")
            except ValueError:
                print(Fore.RED + "Ingrese un valor numérico válido para el área.")
                
        elif opcion == "2":
            print(Fore.CYAN + "\n--- LOTES PRODUCTIVOS ---")
            if not lotes:
                print("No hay lotes registrados.")
            else:
                for lid, l in lotes.items():
                    print(f"Lote: {lid} | Producto: {l['producto_codigo']} | Siembra: {l['fecha_siembra']} | Área: {l['area_m2']}m2 | Prod: {l['cantidad_producida']} | Estado: {l['estado']}")
                    
        elif opcion == "3":
            id_lote = input("Ingrese el ID del lote a cosechar: ").strip().upper()
            if id_lote not in lotes:
                print(Fore.RED + "El lote no existe (PF003).")
                continue
            lote = lotes[id_lote]
            if lote['estado'] != "EN_PRODUCCION":
                print(Fore.RED + f"El lote ya se encuentra en estado '{lote['estado']}' y no puede cosecharse de nuevo (PF004, Regla 5).")
                continue
                
            try:
                cantidad_cosechada = int(input("Ingrese la cantidad producida en la cosecha: "))
                if cantidad_cosechada <= 0:
                    print(Fore.RED + "La cantidad debe ser mayor a 0.")
                    continue
                
                lote['cantidad_producida'] = cantidad_cosechada
                lote['estado'] = "COSECHADO"
                
                # Generar automáticamente una entrada de inventario (RF07)
                m_id = generar_id_movimiento()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                movimientos[m_id] = {
                    "id": m_id,
                    "producto_codigo": lote['producto_codigo'],
                    "tipo": "ENTRADA",
                    "cantidad": cantidad_cosechada,
                    "motivo": f"Cosecha lote {id_lote}",
                    "fecha": fecha_actual
                }
                
                guardar_datos()
                print(Fore.GREEN + f"¡Lote {id_lote} cosechado con éxito! Se generó la entrada de inventario {m_id} (RF07).")
            except ValueError:
                print(Fore.RED + "Ingrese un número entero válido.")
                
        elif opcion == "0":
            break
        else:
            print(Fore.RED + "Opción inválida.")
            
def menu_movimientos_inventario():
    while True:
        print(Fore.YELLOW + Style.BRIGHT + "\n--- MOVIMIENTOS DE INVENTARIO ---" + Style.RESET_ALL)
        print("1. Registrar entrada manual")
        print("2. Registrar salida manual")
        print("3. Ver historial de movimientos")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1" or opcion == "2":
            tipo = "ENTRADA" if opcion == "1" else "SALIDA"
            prod_cod = input("Código del producto: ").strip().upper()
            if prod_cod not in productos:
                print(Fore.RED + "El producto no existe.")
                continue
            
            try:
                cantidad = int(input("Cantidad: "))
                if cantidad <= 0:
                    print(Fore.RED + "La cantidad debe ser mayor a 0.")
                    continue
                
                # Validar stock para salidas (RF09)
                if tipo == "SALIDA":
                    stock_actual = calcular_stock(prod_cod)
                    if stock_actual < cantidad:
                        print(Fore.RED + f"Stock insuficiente (Stock disponible: {stock_actual}). No se puede realizar la salida (PF005, Regla 4).")
                        continue
                        
                motivo = input("Motivo obligatorio del movimiento: ").strip()
                if not motivo:
                    print(Fore.RED + "El motivo es obligatorio (RF08).")
                    continue
                
                m_id = generar_id_movimiento()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                movimientos[m_id] = {
                    "id": m_id,
                    "producto_codigo": prod_cod,
                    "tipo": tipo,
                    "cantidad": cantidad,
                    "motivo": motivo,
                    "fecha": fecha_actual
                }
                guardar_datos()
                print(Fore.GREEN + f"¡Movimiento {m_id} registrado con éxito!")
            except ValueError:
                print(Fore.RED + "Ingrese una cantidad numérica válida.")
                
        elif opcion == "3":
            print(Fore.CYAN + "\n--- HISTORIAL DE MOVIMIENTOS ---")
            if not movimientos:
                print("No hay movimientos registrados.")
            else:
                for mid, m in movimientos.items():
                    print(f"[{m['id']}] {m['fecha']} | {m['tipo']} | Prod: {m['producto_codigo']} | Cant: {m['cantidad']} | Motivo: {m['motivo']}")
                    
        elif opcion == "0":
            break
        else:
            print(Fore.RED + "Opción inválida.")
def registrar_venta():
    print(Fore.CYAN + "\n--- REGISTRAR VENTA ---")
    items_venta = []
    total_venta = 0.0
    
    while True:
        prod_cod = input("Ingrese el código del producto a vender (o escriba 'fin' para terminar): ").strip().upper()
        if prod_cod == 'FIN':
            break
            
        if prod_cod not in productos or not productos[prod_cod]['activo']:
            print(Fore.RED + "El producto no existe o está inactivo.")
            continue
            
        try:
            cantidad = int(input(f"Cantidad de '{productos[prod_cod]['nombre']}': "))
            if cantidad <= 0:
                print(Fore.RED + "La cantidad debe ser mayor a 0.")
                continue
                
            # Validar stock suficiente (RF10, Regla 4)
            stock_actual = calcular_stock(prod_cod)
            if stock_actual < cantidad:
                print(Fore.RED + f"Stock insuficiente. Stock disponible: {stock_actual} (PF005).")
                continue
                
            precio_unitario = productos[prod_cod]['precio'] # Regla 7
            subtotal = precio_unitario * cantidad
            
            items_venta.append({
                "codigo": prod_cod,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario
            })
            total_venta += subtotal
            print(Fore.GREEN + f"Ítem agregado. Subtotal: ${subtotal}")
        except ValueError:
            print(Fore.RED + "Ingrese una cantidad numérica válida.")
            
    if not items_venta:
        print(Fore.YELLOW + "La venta fue cancelada (debe contener al menos un ítem - Regla 6).")
        return
        
    # Registrar la venta y descontar inventario mediante movimientos de salida (RF10)
    v_id = generar_id_venta()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    ventas[v_id] = {
        "id": v_id,
        "fecha": fecha_actual,
        "items": items_venta,
        "total": total_venta
    }
    
    # Generar movimientos de salida automáticos asociados a la venta
    for item in items_venta:
        m_id = generar_id_movimiento()
        movimientos[m_id] = {
            "id": m_id,
            "producto_codigo": item['codigo'],
            "tipo": "SALIDA",
            "cantidad": item['cantidad'],
            "motivo": f"Venta {v_id}",
            "fecha": fecha_actual
        }
        
    guardar_datos()
    print(Fore.GREEN + f"\n¡Venta {v_id} registrada con éxito! Total a pagar: ${total_venta} (RF11, PF006, PF007).")

def consultar_ventas():
    print(Fore.CYAN + "\n--- CONSULTAR VENTAS ---")
    if not ventas:
        print("No hay ventas registradas.")
    else:
        for vid, v in ventas.items():
            print(f"Venta ID: {vid} | Fecha: {v['fecha']} | Total: ${v['total']}")
            for item in v['items']:
                print(f"   -> Producto: {item['codigo']} | Cantidad: {item['cantidad']} | Precio U: ${item['precio_unitario']}")
def alertas_stock():
    print(Fore.CYAN + "\n--- ALERTAS DE STOCK BAJO (RF12) ---")
    alerta_encontrada = False
    for cod, p in productos.items():
        if p['activo']:
            stock_actual = calcular_stock(cod)
            if stock_actual <= p['stock_minimo']:
                print(Fore.RED + f"¡ALERTA! Producto '{p['nombre']}' ({cod}) tiene stock bajo. Actual: {stock_actual} | Mínimo: {p['stock_minimo']}")
                alerta_encontrada = True
    if not alerta_encontrada:
        print(Fore.GREEN + "Todos los productos activos tienen niveles de stock óptimos.")

def menu_reportes():
    while True:
        print(Fore.YELLOW + Style.BRIGHT + "\n--- MÓDULO DE REPORTES ---" + Style.RESET_ALL)
        print("1. Reporte de existencias y valor del inventario")
        print("2. Reporte de ventas (Ingresos y unidades)")
        print("3. Ranking de los 3 productos más vendidos")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            print(Fore.CYAN + "\n--- REPORTE DE INVENTARIO ---")
            valor_total_inventario = 0.0
            if not productos:
                print("No hay productos.")
            else:
                for cod, p in productos.items():
                    stock = calcular_stock(cod)
                    valor_inventario = stock * p['precio']
                    valor_total_inventario += valor_inventario
                    print(f"[{cod}] {p['nombre']} | Stock: {stock} | Precio Venta: ${p['precio']} | Valor Total: ${valor_inventario}")
                print(Fore.GREEN + f"\nValor total acumulado del inventario a precio de venta: ${valor_total_inventario} (RF13)")
                
        elif opcion == "2":
            print(Fore.CYAN + "\n--- REPORTE DE VENTAS ---")
            total_ventas_realizadas = len(ventas)
            unidades_vendidas = 0
            ingresos_totales = 0.0
            for v in ventas.values():
                ingresos_totales += v['total']
                for item in v['items']:
                    unidades_vendidas += item['cantidad']
            print(f"Número total de ventas: {total_ventas_realizadas}")
            print(f"Unidades totales vendidas: {unidades_vendidas}")
            print(f"Ingresos totales acumulados: ${ingresos_totales} (RF14)")
            
        elif opcion == "3":
            print(Fore.CYAN + "\n--- RANKING: TOP 3 PRODUCTOS MÁS VENDIDOS --- (RF15)")
            conteo_productos = {}
            for v in ventas.values():
                for item in v['items']:
                    cod = item['codigo']
                    conteo_productos[cod] = conteo_productos.get(cod, 0) + item['cantidad']
                    
            top_productos = sorted(conteo_productos.items(), key=lambda x: x[1], reverse=True)[:3]
            if not top_productos:
                print("No hay suficientes datos de ventas para generar el ranking.")
            else:
                for i, (cod, cant) in enumerate(top_productos, 1):
                    nombre_prod = productos[cod]['nombre'] if cod in productos else cod
                    print(f"{i}. Producto: {nombre_prod} ({cod}) — Cantidad vendida: {cant} unidades")
                    
        elif opcion == "0":
            break
        else:
            print(Fore.RED + "Opción inválida.")
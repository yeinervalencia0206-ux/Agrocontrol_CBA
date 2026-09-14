from datetime import datetime
import json
from pathlib import Path

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
    
    try:
        if FILE_PRODUCTOS.exists():
            with open(FILE_PRODUCTOS, "r", encoding="utf-8") as f:
                productos = json.load(f)
    except Exception as e:
        print(f"Error al cargar productos.json: {e}")
        productos = {}

    try:
        if FILE_LOTES.exists():
            with open(FILE_LOTES, "r", encoding="utf-8") as f:
                lotes = json.load(f)
    except Exception as e:
        print(f"Error al cargar lotes.json: {e}")
        lotes = {}

    try:
        if FILE_MOVIMIENTOS.exists():
            with open(FILE_MOVIMIENTOS, "r", encoding="utf-8") as f:
                movimientos = json.load(f)
    except Exception as e:
        print(f"Error al cargar movimientos.json: {e}")
        movimientos = {}

    try:
        if FILE_VENTAS.exists():
            with open(FILE_VENTAS, "r", encoding="utf-8") as f:
                ventas = json.load(f)
    except Exception as e:
        print(f"Error al cargar ventas.json: {e}")
        ventas = {}
        
    print("¡Datos cargados correctamente desde la carpeta data/!")

def guardar_datos():
    """Guarda los diccionarios actuales en formato JSON."""
    try:
        with open(FILE_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump(productos, f, indent=4, ensure_ascii=False)
        with open(FILE_LOTES, "w", encoding="utf-8") as f:
            json.dump(lotes, f, indent=4, ensure_ascii=False)
        with open(FILE_MOVIMIENTOS, "w", encoding="utf-8") as f:
            json.dump(movimientos, f, indent=4, ensure_ascii=False)
        with open(FILE_VENTAS, "w", encoding="utf-8") as f:
            json.dump(ventas, f, indent=4, ensure_ascii=False)
        print("¡Datos guardados exitosamente en formato JSON!")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        
def calcular_stock(codigo_producto):
    """Calcula el stock actual a partir de los movimientos registrados."""
    stock = 0
    for mov in movimientos.values():
        if mov["producto_codigo"] == codigo_producto:
            if mov["tipo"] == "ENTRADA":
                stock += mov["cantidad"]
            elif mov["tipo"] == "SALIDA":
                stock -= mov["cantidad"]
    return stock

def generar_id_movimiento():
    nuevo_num = len(movimientos) + 1
    return f"M{nuevo_num:04d}"

def generar_id_venta():
    nuevo_num = len(ventas) + 1
    return f"V{nuevo_num:04d}"

def menu_gestion_productos():
    while True:
        print("\n--- GESTIÓN DE PRODUCTOS ---")
        print("1. Registrar producto")
        print("2. Listar productos")
        print("3. Actualizar producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            codigo = input("Ingrese el código del producto (ej. P001): ").strip().upper()
            if not codigo:
                print("El código no puede estar vacío.")
                continue
            if codigo in productos:
                print("El producto ya existe.")
                continue
            
            nombre = input("Nombre del producto: ").strip()
            categoria = input("Categoría: ").strip()
            unidad = input("Unidad de medida (ej. unidad, kg): ").strip()
            
            try:
                precio = float(input("Precio unitario de venta: "))
                if precio <= 0:
                    print("El precio debe ser mayor a 0.")
                    continue
                
                stock_inicial = int(input("Stock inicial del producto: "))
                if stock_inicial < 0:
                    print("El stock inicial no puede ser negativo.")
                    continue

                stock_minimo = int(input("Stock mínimo: "))
                if stock_minimo < 0:
                    print("El stock mínimo no puede ser negativo.")
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

                if stock_inicial > 0:
                    m_id = generar_id_movimiento()
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    movimientos[m_id] = {
                        "id": m_id,
                        "producto_codigo": codigo,
                        "tipo": "ENTRADA",
                        "cantidad": stock_inicial,
                        "motivo": "Stock inicial de registro",
                        "fecha": fecha_actual
                    }

                guardar_datos()
                print("¡Producto registrado con éxito!")
            except ValueError:
                print("Error: Ingrese valores numéricos válidos.")
                
        elif opcion == "2":
            print("\n--- LISTA DE PRODUCTOS ---")
            if not productos:
                print("No hay productos registrados.")
            else:
                for cod, p in productos.items():
                    stock_actual = calcular_stock(cod)
                    estado = "Activo" if p['activo'] else "Inactivo"
                    print(f"[{p['codigo']}] {p['nombre']} | Cat: {p['categoria']} | Precio: ${p['precio']} | Stock: {stock_actual} | Estado: {estado}")
                    
        elif opcion == "3":
            codigo = input("Ingrese el código del producto a actualizar: ").strip().upper()
            if codigo not in productos:
                print("El producto no existe.")
                continue
            
            p = productos[codigo]
            print(f"Actualizando producto: {p['nombre']}. Deje en blanco para mantener.")
            
            nuevo_nombre = input(f"Nuevo nombre [{p['nombre']}]: ").strip()
            if nuevo_nombre: p['nombre'] = nuevo_nombre
            
            nueva_cat = input(f"Nueva categoría [{p['categoria']}]: ").strip()
            if nueva_cat: p['categoria'] = nueva_cat
            
            nuevo_precio = input(f"Nuevo precio [{p['precio']}]: ").strip()
            if nuevo_precio:
                try:
                    val = float(nuevo_precio)
                    if val > 0: p['precio'] = val
                except ValueError: print("Valor inválido.")
                
            guardar_datos()
            print("¡Producto actualizado correctamente!")
            
        elif opcion == "4":
            codigo = input("Ingrese el código del producto a desactivar: ").strip().upper()
            if codigo not in productos:
                print("El producto no existe.")
                continue
            productos[codigo]['activo'] = False
            guardar_datos()
            print("¡Producto desactivado correctamente!")
            
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")
            
def menu_gestion_lotes():
    while True:
        print("\n--- GESTIÓN DE LOTES PRODUCTIVOS ---")
        print("1. Registrar lote")
        print("2. Consultar lotes")
        print("3. Registrar proceso de cosecha")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            id_lote = input("Identificador del lote (ej. L001): ").strip().upper()
            if not id_lote or id_lote in lotes:
                print("ID inválido o ya existente.")
                continue
            prod_cod = input("Código del producto asociado: ").strip().upper()
            if prod_cod not in productos or not productos[prod_cod]['activo']:
                print("El producto no existe o está inactivo.")
                continue
            fecha_siembra = input("Fecha de siembra (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(fecha_siembra, "%Y-%m-%d")
                area_m2 = float(input("Área en metros cuadrados (m2): "))
                lotes[id_lote] = {
                    "id_lote": id_lote,
                    "producto_codigo": prod_cod,
                    "fecha_siembra": fecha_siembra,
                    "area_m2": area_m2,
                    "cantidad_producida": 0,
                    "estado": "EN_PRODUCCION"
                }
                guardar_datos()
                print("¡Lote registrado exitosamente!")
            except ValueError:
                print("Datos ingresados incorrectos.")
        elif opcion == "2":
            for lid, l in lotes.items():
                print(f"Lote: {lid} | Prod: {l['producto_codigo']} | Siembra: {l['fecha_siembra']} | Estado: {l['estado']}")
        elif opcion == "3":
            id_lote = input("ID del lote a cosechar: ").strip().upper()
            if id_lote not in lotes or lotes[id_lote]['estado'] != "EN_PRODUCCION":
                print("Lote inválido o ya cosechado.")
                continue
            try:
                cant = int(input("Cantidad producida: "))
                lotes[id_lote]['cantidad_producida'] = cant
                lotes[id_lote]['estado'] = "COSECHADO"
                m_id = generar_id_movimiento()
                movimientos[m_id] = {
                    "id": m_id,
                    "producto_codigo": lotes[id_lote]['producto_codigo'],
                    "tipo": "ENTRADA",
                    "cantidad": cant,
                    "motivo": f"Cosecha lote {id_lote}",
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                guardar_datos()
                print("¡Cosecha registrada y stock actualizado!")
            except ValueError:
                print("Cantidad inválida.")
        elif opcion == "0":
            break
            
def menu_movimientos_inventario():
    while True:
        print("\n--- MOVIMIENTOS DE INVENTARIO ---")
        print("1. Registrar entrada manual")
        print("2. Registrar salida manual")
        print("3. Ver historial de movimientos")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        if opcion in ["1", "2"]:
            tipo = "ENTRADA" if opcion == "1" else "SALIDA"
            prod_cod = input("Código del producto: ").strip().upper()
            if prod_cod not in productos:
                print("Producto no existe.")
                continue
            try:
                cant = int(input("Cantidad: "))
                if tipo == "SALIDA" and calcular_stock(prod_cod) < cant:
                    print("Stock insuficiente.")
                    continue
                motivo = input("Motivo del movimiento: ").strip()
                m_id = generar_id_movimiento()
                movimientos[m_id] = {
                    "id": m_id,
                    "producto_codigo": prod_cod,
                    "tipo": tipo,
                    "cantidad": cant,
                    "motivo": motivo,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                guardar_datos()
                print("¡Movimiento registrado!")
            except ValueError:
                print("Valor numérico inválido.")
        elif opcion == "3":
            for mid, m in movimientos.items():
                print(f"[{m['id']}] {m['fecha']} | {m['tipo']} | Prod: {m['producto_codigo']} | Cant: {m['cantidad']} | Motivo: {m['motivo']}")
        elif opcion == "0":
            break

def registrar_venta():
    print("\n--- REGISTRAR VENTA ---")
    items_venta = []
    total_venta = 0.0
    
    while True:
        prod_cod = input("Ingrese el código del producto a vender (o escriba 'fin' para terminar): ").strip().upper()
        if prod_cod == 'FIN':
            break
        if prod_cod not in productos or not productos[prod_cod]['activo']:
            print("Producto no disponible.")
            continue
        try:
            cantidad = int(input(f"Cantidad de '{productos[prod_cod]['nombre']}': "))
            if calcular_stock(prod_cod) < cantidad:
                print("Stock insuficiente.")
                continue
            
            precio = productos[prod_cod]['precio']
            subtotal_item = precio * cantidad
            total_venta += subtotal_item
            
            items_venta.append({
                "codigo": prod_cod,
                "cantidad": cantidad,
                "precio_unitario": precio
            })
            
            # Muestra el subtotal del ítem y enseguida el total parcial acumulado
            print(f"Ítem agregado. Subtotal: ${subtotal_item}")
            print(f"Total parcial acumulado: ${total_venta}")
            
        except ValueError:
            print("Cantidad inválida.")
            
    if not items_venta:
        print("Venta cancelada.")
        return
        
    v_id = generar_id_venta()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    ventas[v_id] = {
        "id": v_id,
        "fecha": fecha_actual,
        "items": items_venta,
        "total": total_venta,
        "estado": "COMPLETADA"
    }
    
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
    
    codigos_items = ", ".join([item['codigo'] for item in items_venta])
    print(f"\n¡Venta {v_id} registrada con éxito! Total a pagar: ${total_venta} ({codigos_items}).")

def consultar_ventas_por_fecha():
    """Permite consultar ventas filtradas por un rango de fechas (YYYY-MM-DD)."""
    print("\n--- CONSULTAR VENTAS POR RANGO DE FECHAS ---")
    f_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
    f_fin = input("Fecha de fin (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(f_inicio, "%Y-%m-%d")
        datetime.strptime(f_fin, "%Y-%m-%d")
    except ValueError:
        print("Formato de fecha inválido. Use YYYY-MM-DD.")
        return

    encontradas = False
    print(f"\nResultados entre {f_inicio} y {f_fin}:")
    for vid, v in ventas.items():
        fecha_venta = v["fecha"].split(" ")[0]
        if f_inicio <= fecha_venta <= f_fin:
            print(f"Venta ID: {vid} | Fecha: {v['fecha']} | Total: ${v['total']} | Estado: {v.get('estado', 'COMPLETADA')}")
            encontradas = True

    if not encontradas:
        print("No se encontraron ventas en ese rango de fechas.")

def alertas_stock():
    print("\n--- ALERTAS DE STOCK BAJO ---")
    for cod, p in productos.items():
        if p['activo'] and calcular_stock(cod) <= p['stock_minimo']:
            print(f"¡ALERTA! '{p['nombre']}' ({cod}) stock actual: {calcular_stock(cod)} (Mínimo: {p['stock_minimo']})")

def menu_reportes():
    while True:
        print("\n--- MÓDULO DE REPORTES ---")
        print("1. Reporte de existencias y valor del inventario")
        print("2. Reporte de ventas (Ingresos y unidades)")
        print("3. Consultar ventas por rango de fechas")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            valor_total = 0.0
            for cod, p in productos.items():
                stock = calcular_stock(cod)
                val = stock * p['precio']
                valor_total += val
                print(f"[{cod}] {p['nombre']} | Stock: {stock} | Valor Venta: ${val}")
            print(f"Valor total acumulado del inventario: ${valor_total}")
            
        elif opcion == "2":
            ingresos = sum(v['total'] for v in ventas.values())
            unidades = sum(item['cantidad'] for v in ventas.values() for item in v['items'])
            print(f"Ventas procesadas: {len(ventas)}")
            print(f"Unidades totales vendidas: {unidades}")
            print(f"Ingresos netos acumulados: ${ingresos}")
            
        elif opcion == "3":
            consultar_ventas_por_fecha()
            
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")

def mostrar_menu():
    print("\n==================== AGROCONTROL CBA ====================")
    print("1. Gestión de productos")
    print("2. Gestión de lotes productivos")
    print("3. Movimientos de inventario")
    print("4. Registrar venta")
    print("5. Alertas de stock")
    print("6. Reportes")
    print("0. Salir")

def main():
    cargar_datos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_gestion_productos()
        elif opcion == "2":
            menu_gestion_lotes()
        elif opcion == "3":
            menu_movimientos_inventario()
        elif opcion == "4":
            registrar_venta()
        elif opcion == "5":
            alertas_stock()
        elif opcion == "6":
            menu_reportes()
        elif opcion == "0":
            guardar_datos()
            print("\nSaliendo del Sistema AgroControl CBA. ¡Hasta luego!")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
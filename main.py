import json
import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
 
# Configuración de rutas y archivos según la estructura requerida
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
 
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
 
REPORTS_DIR = BASE_DIR / "reportes"
REPORTS_DIR.mkdir(exist_ok=True)
 
FILE_PRODUCTOS = DATA_DIR / "productos.json"
FILE_LOTES = DATA_DIR / "lotes.json"
FILE_MOVIMIENTOS = DATA_DIR / "movimientos.json"
FILE_VENTAS = DATA_DIR / "ventas.json"
FILE_USUARIOS = DATA_DIR / "usuarios.json"
 
# Estructuras de datos en memoria
productos = {}
lotes = {}
movimientos = {}
ventas = {}
usuarios = {}
 
# Sesión activa
usuario_actual = None
rol_actual = None
 
def cargar_datos():
    """Carga todos los datos desde los archivos JSON en la carpeta data/ con manejo seguro de archivos vacíos."""
    global productos, lotes, movimientos, ventas, usuarios
 
    # Productos
    try:
        if FILE_PRODUCTOS.exists() and FILE_PRODUCTOS.stat().st_size > 0:
            with open(FILE_PRODUCTOS, "r", encoding="utf-8") as f:
                productos = json.load(f)
    except Exception as e:
        print(f"Error al cargar productos.json: {e}")
        productos = {}
 
    # Lotes
    try:
        if FILE_LOTES.exists() and FILE_LOTES.stat().st_size > 0:
            with open(FILE_LOTES, "r", encoding="utf-8") as f:
                lotes = json.load(f)
    except Exception as e:
        print(f"Error al cargar lotes.json: {e}")
        lotes = {}
 
    # Movimientos
    try:
        if FILE_MOVIMIENTOS.exists() and FILE_MOVIMIENTOS.stat().st_size > 0:
            with open(FILE_MOVIMIENTOS, "r", encoding="utf-8") as f:
                movimientos = json.load(f)
    except Exception as e:
        print(f"Error al cargar movimientos.json: {e}")
        movimientos = {}
 
    # Ventas
    try:
        if FILE_VENTAS.exists() and FILE_VENTAS.stat().st_size > 0:
            with open(FILE_VENTAS, "r", encoding="utf-8") as f:
                ventas = json.load(f)
    except Exception as e:
        print(f"Error al cargar ventas.json: {e}")
        ventas = {}
 
    # Usuarios (autenticación)
    try:
        if FILE_USUARIOS.exists() and FILE_USUARIOS.stat().st_size > 0:
            with open(FILE_USUARIOS, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
    except Exception as e:
        print(f"Error al cargar usuarios.json: {e}")
        usuarios = {}
 
    print("¡Datos cargados correctamente desde la carpeta data/!")
 
def copia_seguridad():
    """Crea una copia de seguridad con marca de tiempo de todos los archivos JSON
    antes de que sean sobrescritos (se ejecuta automáticamente dentro de guardar_datos)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivos = [FILE_PRODUCTOS, FILE_LOTES, FILE_MOVIMIENTOS, FILE_VENTAS, FILE_USUARIOS]
    for archivo in archivos:
        try:
            if archivo.exists() and archivo.stat().st_size > 0:
                destino = BACKUP_DIR / f"{archivo.stem}_{timestamp}{archivo.suffix}"
                shutil.copy2(archivo, destino)
        except Exception as e:
            print(f"Advertencia: no se pudo respaldar {archivo.name}: {e}")
 
def guardar_datos():
    """Guarda todos los diccionarios actuales en sus respectivos archivos JSON.
    Antes de escribir, genera una copia de seguridad de los archivos existentes."""
    try:
        copia_seguridad()
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
 
# ==================== AUTENTICACIÓN Y ROLES ====================
 
def hash_password(password):
    """Genera un hash SHA-256 de la contraseña; nunca se guarda en texto plano."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
 
def inicializar_usuarios():
    """Crea usuarios por defecto si aún no existe ningún usuario registrado (primer uso)."""
    global usuarios
    if not usuarios:
        usuarios = {
            "admin": {
                "password_hash": hash_password("admin123"),
                "rol": "INSTRUCTOR"
            },
            "operador": {
                "password_hash": hash_password("operador123"),
                "rol": "OPERADOR"
            }
        }
        try:
            with open(FILE_USUARIOS, "w", encoding="utf-8") as f:
                json.dump(usuarios, f, indent=4, ensure_ascii=False)
            print("\nNo se encontraron usuarios registrados. Se crearon usuarios por defecto:")
            print("  -> admin / admin123      (rol INSTRUCTOR)")
            print("  -> operador / operador123 (rol OPERADOR)")
            print("Se recomienda cambiar estas contraseñas apenas sea posible.\n")
        except Exception as e:
            print(f"Error al crear usuarios por defecto: {e}")
 
def autenticar():
    """Solicita usuario y contraseña (máximo 3 intentos). Retorna True si el acceso fue concedido."""
    global usuario_actual, rol_actual
    print("\n==================== INICIO DE SESIÓN — AGROCONTROL CBA ====================")
    intentos = 0
    while intentos < 3:
        usuario = input("Usuario: ").strip().lower()
        clave = input("Contraseña: ").strip()
 
        if usuario in usuarios and usuarios[usuario]["password_hash"] == hash_password(clave):
            usuario_actual = usuario
            rol_actual = usuarios[usuario]["rol"]
            print(f"\n¡Bienvenido, {usuario}! Rol asignado: {rol_actual}")
            return True
        else:
            intentos += 1
            restantes = 3 - intentos
            if restantes > 0:
                print(f"Usuario o contraseña incorrectos. Le quedan {restantes} intento(s).")
            else:
                print("Usuario o contraseña incorrectos.")
 
    print("\nSe agotaron los intentos de inicio de sesión. Cerrando el sistema.")
    return False
 
def acceso_permitido(roles_permitidos):
    """Verifica si el rol de la sesión activa está autorizado para la acción solicitada."""
    if rol_actual not in roles_permitidos:
        print(f"Acceso denegado: esta función requiere el rol {' o '.join(roles_permitidos)}. "
              f"Su rol actual es {rol_actual}.")
        return False
    return True
 
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
            if not acceso_permitido(["INSTRUCTOR"]):
                continue
            codigo = input("Ingrese el código del producto (ej. P001): ").strip().upper()
            if not codigo:
                print("El código no puede estar vacío.")
                continue
            if codigo in productos:
                print("El producto ya existe (RF01).")
                continue
            
            nombre = input("Nombre del producto: ").strip()
            categoria = input("Categoría: ").strip()
            unidad = input("Unidad de medida (ej. unidad, kg): ").strip()
            
            try:
                precio = float(input("Precio unitario: "))
                if precio <= 0:
                    print("El precio debe ser mayor a 0 (RF01).")
                    continue
                
                stock_inicial = int(input("Stock inicial del producto: "))
                if stock_inicial < 0:
                    print("El stock inicial no puede ser negativo.")
                    continue
 
                stock_minimo = int(input("Stock mínimo: "))
                if stock_minimo < 0:
                    print("El stock mínimo no puede ser negativo (RF01).")
                    continue
 
                costo_unitario = None
                costo_str = input("Costo unitario de producción (opcional, Enter para omitir): ").strip()
                if costo_str:
                    try:
                        costo_unitario = float(costo_str)
                        if costo_unitario < 0:
                            print("El costo no puede ser negativo; se omite el costo.")
                            costo_unitario = None
                    except ValueError:
                        print("Valor no numérico; se omite el costo.")
                
                productos[codigo] = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "categoria": categoria,
                    "unidad": unidad,
                    "precio": precio,
                    "stock_inicial": stock_inicial,
                    "stock_minimo": stock_minimo,
                    "costo_unitario": costo_unitario,
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
                print("¡Producto registrado con éxito y stock guardado!")
            except ValueError:
                print("Error: Ingrese valores numéricos válidos (RF18).")
                
        elif opcion == "2":
            print("\n--- LISTA DE PRODUCTOS ---")
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
                    print("No se encontraron productos con ese criterio.")
                    
        elif opcion == "3":
            if not acceso_permitido(["INSTRUCTOR"]):
                continue
            codigo = input("Ingrese el código del producto a actualizar: ").strip().upper()
            if codigo not in productos:
                print("El producto no existe.")
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
                    else: print("Precio inválido, se mantiene el anterior.")
                except ValueError: print("Valor no numérico, se mantiene el anterior.")
                
            nuevo_smin = input(f"Nuevo stock mínimo [{p['stock_minimo']}]: ").strip()
            if nuevo_smin:
                try:
                    val = int(nuevo_smin)
                    if val >= 0: p['stock_minimo'] = val
                    else: print("Stock mínimo inválido, se mantiene el anterior.")
                except ValueError: print("Valor no numérico, se mantiene el anterior.")
 
            costo_actual = p.get('costo_unitario')
            costo_actual_str = costo_actual if costo_actual is not None else "sin definir"
            nuevo_costo = input(f"Nuevo costo unitario [{costo_actual_str}]: ").strip()
            if nuevo_costo:
                try:
                    val = float(nuevo_costo)
                    if val >= 0: p['costo_unitario'] = val
                    else: print("Costo inválido, se mantiene el anterior.")
                except ValueError: print("Valor no numérico, se mantiene el anterior.")
                
            guardar_datos()
            print("¡Producto actualizado correctamente (RF03)!")
            
        elif opcion == "4":
            if not acceso_permitido(["INSTRUCTOR"]):
                continue
            codigo = input("Ingrese el código del producto a desactivar: ").strip().upper()
            if codigo not in productos:
                print("El producto no existe.")
                continue
            productos[codigo]['activo'] = False
            guardar_datos()
            print("¡Producto desactivado correctamente (RF04)! Se conserva su historial.")
            
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
            if not id_lote:
                print("El ID no puede estar vacío.")
                continue
            if id_lote in lotes:
                print("El lote ya existe.")
                continue
                
            prod_cod = input("Código del producto asociado: ").strip().upper()
            if prod_cod not in productos or not productos[prod_cod]['activo']:
                print("El producto no existe o está inactivo (RF05).")
                continue
                
            fecha_siembra = input("Fecha de siembra (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(fecha_siembra, "%Y-%m-%d")
            except ValueError:
                print("Formato de fecha inválido. Use YYYY-MM-DD.")
                continue
                
            try:
                area_m2 = float(input("Área en metros cuadrados (m2): "))
                if area_m2 <= 0:
                    print("El área debe ser mayor a 0.")
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
                print("¡Lote registrado exitosamente (RF05)! Estado: EN_PRODUCCION.")
            except ValueError:
                print("Ingrese un valor numérico válido para el área.")
                
        elif opcion == "2":
            print("\n--- LOTES PRODUCTIVOS ---")
            if not lotes:
                print("No hay lotes registrados.")
            else:
                for lid, l in lotes.items():
                    print(f"Lote: {lid} | Producto: {l['producto_codigo']} | Siembra: {l['fecha_siembra']} | Área: {l['area_m2']}m2 | Prod: {l['cantidad_producida']} | Estado: {l['estado']}")
                    
        elif opcion == "3":
            id_lote = input("Ingrese el ID del lote a cosechar: ").strip().upper()
            if id_lote not in lotes:
                print("El lote no existe (PF003).")
                continue
            lote = lotes[id_lote]
            if lote['estado'] != "EN_PRODUCCION":
                print(f"El lote ya se encuentra en estado '{lote['estado']}' y no puede cosecharse de nuevo (PF004, Regla 5).")
                continue
                
            try:
                cantidad_cosechada = int(input("Ingrese la cantidad producida en la cosecha: "))
                if cantidad_cosechada <= 0:
                    print("La cantidad debe ser mayor a 0.")
                    continue
                
                lote['cantidad_producida'] = cantidad_cosechada
                lote['estado'] = "COSECHADO"
                
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
                print(f"¡Lote {id_lote} cosechado con éxito! Se generó la entrada de inventario {m_id} (RF07).")
            except ValueError:
                print("Ingrese un número entero válido.")
                
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")
            
def menu_movimientos_inventario():
    while True:
        print("\n--- MOVIMIENTOS DE INVENTARIO ---")
        print("1. Registrar entrada manual")
        print("2. Registrar salida manual")
        print("3. Ver historial de movimientos")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1" or opcion == "2":
            tipo = "ENTRADA" if opcion == "1" else "SALIDA"
            prod_cod = input("Código del producto: ").strip().upper()
            if prod_cod not in productos:
                print("El producto no existe.")
                continue
            
            try:
                cantidad = int(input("Cantidad: "))
                if cantidad <= 0:
                    print("La cantidad debe ser mayor a 0.")
                    continue
                
                if tipo == "SALIDA":
                    stock_actual = calcular_stock(prod_cod)
                    if stock_actual < cantidad:
                        print(f"Stock insuficiente (Stock disponible: {stock_actual}). No se puede realizar la salida (PF005, Regla 4).")
                        continue
                        
                motivo = input("Motivo obligatorio del movimiento: ").strip()
                if not motivo:
                    print("El motivo es obligatorio (RF08).")
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
                print(f"¡Movimiento {m_id} registrado con éxito!")
            except ValueError:
                print("Ingrese una cantidad numérica válida.")
                
        elif opcion == "3":
            print("\n--- HISTORIAL DE MOVIMIENTOS ---")
            if not movimientos:
                print("No hay movimientos registrados.")
            else:
                for mid, m in movimientos.items():
                    print(f"[{m['id']}] {m['fecha']} | {m['tipo']} | Prod: {m['producto_codigo']} | Cant: {m['cantidad']} | Motivo: {m['motivo']}")
                    
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")
 
def registrar_venta():
    print("\n--- REGISTRAR VENTA ---")
    items_venta = []
    total_venta = 0.0
    
    while True:
        prod_cod = input("Ingrese el código del producto a vender (o escriba 'fin' para terminar): ").strip().upper()
        if prod_cod == 'FIN':
            break
            
        if prod_cod not in productos or not productos[prod_cod]['activo']:
            print("El producto no existe o está inactivo.")
            continue
            
        try:
            cantidad = int(input(f"Cantidad de '{productos[prod_cod]['nombre']}': "))
            if cantidad <= 0:
                print("La cantidad debe ser mayor a 0.")
                continue
                
            stock_actual = calcular_stock(prod_cod)
            if stock_actual < cantidad:
                print(f"Stock insuficiente. Stock disponible: {stock_actual} (PF005).")
                continue
                
            precio_unitario = productos[prod_cod]['precio']
            subtotal = precio_unitario * cantidad
            
            items_venta.append({
                "codigo": prod_cod,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal,
                "cantidad_devuelta": 0
            })
            total_venta += subtotal
            print(f"Ítem agregado. Subtotal: ${subtotal:.2f}")
        except ValueError:
            print("Ingrese una cantidad numérica válida.")
            
    if not items_venta:
        print("La venta fue cancelada (debe contener al menos un ítem - Regla 6).")
        return
        
    v_id = generar_id_venta()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    ventas[v_id] = {
        "id": v_id,
        "fecha": fecha_actual,
        "items": items_venta,
        "total": total_venta,
        "total_devuelto": 0.0
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
    print(f"\n¡Venta {v_id} registrada con éxito!")
    print(f"Total a pagar de la venta: ${total_venta:.2f} (RF11, PF006, PF007).")
 
def consultar_ventas():
    print("\n--- CONSULTAR VENTAS ---")
    if not ventas:
        print("No hay ventas registradas.")
    else:
        for vid, v in ventas.items():
            print(f"Venta ID: {vid} | Fecha: {v['fecha']} | Total: ${v['total']:.2f}")
            for item in v['items']:
                # MEJORA APLICADA: Uso de .get() para evitar caídas si el JSON es antiguo y no tiene 'subtotal'
                subtotal_item = item.get('subtotal', item['cantidad'] * item['precio_unitario'])
                devuelto = item.get('cantidad_devuelta', 0)
                extra_dev = f" | Devuelto: {devuelto}" if devuelto else ""
                print(f"    -> Producto: {item['codigo']} | Cantidad: {item['cantidad']} | Precio U: ${item['precio_unitario']:.2f} | Subtotal: ${subtotal_item:.2f}{extra_dev}")
 
def alertas_stock():
    print("\n--- ALERTAS DE STOCK BAJO (RF12) ---")
    alerta_encontrada = False
    for cod, p in productos.items():
        if p['activo']:
            stock_actual = calcular_stock(cod)
            if stock_actual <= p['stock_minimo']:
                print(f"¡ALERTA! Producto '{p['nombre']}' ({cod}) tiene stock bajo. Actual: {stock_actual} | Mínimo: {p['stock_minimo']}")
                alerta_encontrada = True
    if not alerta_encontrada:
        print("Todos los productos activos tienen niveles de stock óptimos.")
 
def menu_reportes():
    while True:
        print("\n--- MÓDULO DE REPORTES ---")
        print("1. Reporte de existencias y valor del inventario")
        print("2. Reporte de ventas (Ingresos y unidades)")
        print("3. Ranking de los 3 productos más vendidos")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n--- REPORTE DE INVENTARIO ---")
            valor_total_inventario = 0.0
            if not productos:
                print("No hay productos.")
            else:
                for cod, p in productos.items():
                    stock = calcular_stock(cod)
                    valor_inventario = stock * p['precio']
                    valor_total_inventario += valor_inventario
                    print(f"[{cod}] {p['nombre']} | Stock: {stock} | Precio Venta: ${p['precio']} | Valor Total: ${valor_inventario}")
                print(f"\nValor total acumulado del inventario a precio de venta: ${valor_total_inventario} (RF13)")
                
        elif opcion == "2":
            print("\n--- REPORTE DE VENTAS ---")
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
            print("\n--- RANKING: TOP 3 PRODUCTOS MÁS VENDIDOS --- (RF15)")
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
            print("Opción inválida.")
 
# ==================== FUNCIONES AVANZADAS (NUEVOS REQUERIMIENTOS) ====================
 
def consultar_ventas_por_fecha():
    """Filtra y muestra las ventas registradas dentro de un rango de fechas dado."""
    print("\n--- CONSULTAR VENTAS POR RANGO DE FECHAS ---")
    fecha_inicio_str = input("Fecha inicio (YYYY-MM-DD): ").strip()
    fecha_fin_str = input("Fecha fin (YYYY-MM-DD): ").strip()
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        print("Formato de fecha inválido. Use YYYY-MM-DD.")
        return
 
    if fecha_inicio > fecha_fin:
        print("La fecha de inicio no puede ser posterior a la fecha fin.")
        return
 
    encontradas = False
    total_periodo = 0.0
    for vid, v in ventas.items():
        try:
            fecha_venta = datetime.strptime(v['fecha'], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if fecha_inicio <= fecha_venta <= fecha_fin:
            encontradas = True
            total_periodo += v['total']
            print(f"\nVenta ID: {vid} | Fecha: {v['fecha']} | Total: ${v['total']:.2f}")
            for item in v['items']:
                subtotal_item = item.get('subtotal', item['cantidad'] * item['precio_unitario'])
                print(f"    -> Producto: {item['codigo']} | Cantidad: {item['cantidad']} | Subtotal: ${subtotal_item:.2f}")
 
    if not encontradas:
        print("No se encontraron ventas en el rango de fechas indicado.")
    else:
        print(f"\nTotal de ingresos en el periodo consultado: ${total_periodo:.2f}")
 
def reporte_utilidad_estimada():
    """Calcula la utilidad estimada (precio de venta - costo unitario) por producto vendido.
    Requiere que el producto tenga registrado un costo_unitario; de lo contrario se omite."""
    print("\n--- REPORTE DE UTILIDAD ESTIMADA ---")
    conteo_productos = {}
    for v in ventas.values():
        for item in v['items']:
            cod = item['codigo']
            cantidad_neta = item['cantidad'] - item.get('cantidad_devuelta', 0)
            if cantidad_neta > 0:
                conteo_productos[cod] = conteo_productos.get(cod, 0) + cantidad_neta
 
    if not conteo_productos:
        print("No hay ventas registradas para calcular la utilidad.")
        return
 
    utilidad_total = 0.0
    productos_omitidos = []
    for cod, cantidad_vendida in conteo_productos.items():
        if cod not in productos:
            continue
        p = productos[cod]
        costo_unitario = p.get('costo_unitario')
        if costo_unitario is None:
            productos_omitidos.append(cod)
            continue
        utilidad_unitaria = p['precio'] - costo_unitario
        utilidad_producto = utilidad_unitaria * cantidad_vendida
        utilidad_total += utilidad_producto
        print(f"[{cod}] {p['nombre']} | Vendidas (netas): {cantidad_vendida} | Precio: ${p['precio']:.2f} | "
              f"Costo: ${costo_unitario:.2f} | Utilidad unit.: ${utilidad_unitaria:.2f} | Utilidad total: ${utilidad_producto:.2f}")
 
    if productos_omitidos:
        print(f"\nNota: se omitieron del cálculo los productos sin costo unitario registrado: {', '.join(productos_omitidos)}.")
        print("Puede asignarles un costo desde 'Gestión de productos > Actualizar producto'.")
 
    print(f"\nUtilidad estimada total del negocio: ${utilidad_total:.2f}")
 
def registrar_devolucion():
    """Registra la devolución total o parcial de un ítem de una venta,
    generando el movimiento de inventario inverso (ENTRADA)."""
    print("\n--- REGISTRAR DEVOLUCIÓN DE VENTA ---")
    v_id = input("Ingrese el ID de la venta (ej. V0001): ").strip().upper()
    if v_id not in ventas:
        print("La venta no existe.")
        return
 
    venta = ventas[v_id]
    print(f"\nVenta {v_id} | Fecha: {venta['fecha']} | Total: ${venta['total']:.2f}")
    for idx, item in enumerate(venta['items'], 1):
        devuelto_previo = item.get('cantidad_devuelta', 0)
        disponible = item['cantidad'] - devuelto_previo
        print(f"{idx}. {item['codigo']} | Vendido: {item['cantidad']} | Ya devuelto: {devuelto_previo} | Disponible para devolver: {disponible}")
 
    try:
        idx_sel = int(input("Seleccione el número de ítem a devolver (0 para cancelar): "))
    except ValueError:
        print("Ingrese un número válido.")
        return
 
    if idx_sel == 0:
        print("Devolución cancelada.")
        return
    if idx_sel < 1 or idx_sel > len(venta['items']):
        print("Selección inválida.")
        return
 
    item = venta['items'][idx_sel - 1]
    devuelto_previo = item.get('cantidad_devuelta', 0)
    disponible = item['cantidad'] - devuelto_previo
    if disponible <= 0:
        print("Este ítem ya fue devuelto en su totalidad.")
        return
 
    try:
        cantidad_dev = int(input(f"Cantidad a devolver (máximo {disponible}): "))
        if cantidad_dev <= 0 or cantidad_dev > disponible:
            print("Cantidad inválida.")
            return
    except ValueError:
        print("Ingrese un número entero válido.")
        return
 
    motivo = input("Motivo de la devolución: ").strip()
    if not motivo:
        print("El motivo de la devolución es obligatorio.")
        return
 
    # La venta original generó una SALIDA de inventario; la devolución genera el movimiento inverso: ENTRADA
    m_id = generar_id_movimiento()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    movimientos[m_id] = {
        "id": m_id,
        "producto_codigo": item['codigo'],
        "tipo": "ENTRADA",
        "cantidad": cantidad_dev,
        "motivo": f"Devolución venta {v_id}: {motivo}",
        "fecha": fecha_actual
    }
 
    item['cantidad_devuelta'] = devuelto_previo + cantidad_dev
    monto_devuelto = cantidad_dev * item['precio_unitario']
    venta['total_devuelto'] = venta.get('total_devuelto', 0.0) + monto_devuelto
 
    guardar_datos()
    print(f"\n¡Devolución registrada con éxito!")
    print(f"Movimiento {m_id} generado: ENTRADA de {cantidad_dev} unidades de {item['codigo']} al inventario.")
    print(f"Monto a reembolsar por esta devolución: ${monto_devuelto:.2f}")
 
def exportar_inventario_csv():
    """Exporta el reporte de existencias y valor de inventario a un archivo CSV
    usando la biblioteca estándar csv."""
    print("\n--- EXPORTAR REPORTE DE INVENTARIO A CSV ---")
    if not productos:
        print("No hay productos para exportar.")
        return
 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = REPORTS_DIR / f"inventario_{timestamp}.csv"
 
    try:
        with open(nombre_archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Codigo", "Nombre", "Categoria", "Unidad", "Precio",
                "Costo Unitario", "Stock Actual", "Stock Minimo",
                "Valor Inventario", "Estado"
            ])
            for cod, p in productos.items():
                stock = calcular_stock(cod)
                costo = p.get('costo_unitario')
                costo_str = f"{costo:.2f}" if costo is not None else "N/D"
                valor = stock * p['precio']
                estado = "Activo" if p['activo'] else "Inactivo"
                writer.writerow([
                    cod, p['nombre'], p['categoria'], p['unidad'], f"{p['precio']:.2f}",
                    costo_str, stock, p['stock_minimo'], f"{valor:.2f}", estado
                ])
        print(f"¡Reporte exportado exitosamente en: {nombre_archivo}!")
    except Exception as e:
        print(f"Error al exportar el archivo CSV: {e}")
 
def menu_funciones_avanzadas():
    while True:
        print("\n--- FUNCIONES AVANZADAS ---")
        print("1. Consultar ventas por rango de fechas")
        print("2. Reporte de utilidad estimada (solo INSTRUCTOR)")
        print("3. Registrar devolución de venta")
        print("4. Exportar reporte de inventario a CSV")
        print("0. Volver al menú principal")
 
        opcion = input("Seleccione una opción: ").strip()
 
        if opcion == "1":
            consultar_ventas_por_fecha()
        elif opcion == "2":
            if acceso_permitido(["INSTRUCTOR"]):
                reporte_utilidad_estimada()
        elif opcion == "3":
            registrar_devolucion()
        elif opcion == "4":
            exportar_inventario_csv()
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")
 
def mostrar_menu():
    print("\n==================== AGROCONTROL CBA ====================")
    print(f"Usuario: {usuario_actual} | Rol: {rol_actual}")
    print("1. Gestión de productos")
    print("2. Gestión de lotes productivos")
    print("3. Movimientos de inventario")
    print("4. Registrar venta")
    print("5. Consultar ventas")
    print("6. Alertas de stock")
    print("7. Reportes")
    print("8. Guardar datos")
    print("9. Funciones avanzadas (fechas, utilidad, devoluciones, CSV)")
    print("0. Salir")
 
def main():
    cargar_datos()
    inicializar_usuarios()
 
    if not autenticar():
        return
 
    ejecutando = True
 
    while ejecutando:
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
            consultar_ventas()
        elif opcion == "6":
            alertas_stock()
        elif opcion == "7":
            menu_reportes()
        elif opcion == "8":
            guardar_datos()
        elif opcion == "9":
            menu_funciones_avanzadas()
        elif opcion == "0":
            guardar_datos()
            print("\nSaliendo del Sistema AgroControl CBA. ¡Hasta luego!")
            ejecutando = False
        else:
            print("Opción inválida. Intente de nuevo (RF18).")
 
if __name__ == "__main__":
    main()
 
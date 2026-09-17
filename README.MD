Sistema de informacion desarrollado en Python para la gestion integral de inventario agricola. Controla productos, lotes productivos, movimientos de stock y ventas, garantizando trazabilidad desde la siembra hasta la venta final.

Este proyecto cumple con los requerimientos funcionales RF01 a RF12 y las reglas de negocio establecidas.

Presentado por
Ficha: 3409610
- Yeiner Valencia
- Alexis Perez
- Ismael Palencia

Materia: Analisis y Desarrollo de Software
Archivo principal: main.py

---

Estructura del Proyecto

```text
proyecto/
├── main.py
├── README.md
└── data/
    ├── productos.json
    ├── lotes.json
    ├── movimientos.json
    └── ventas.json
``````
Modulos del Sistema

1. Gestion de Productos
Permite registrar, listar, actualizar y desactivar productos.
- Validacion de codigo unico, precio > 0 y stock minimo >= 0 (RF01).
- El stock inicial genera automaticamente un movimiento de tipo ENTRADA.
- Al desactivar (RF04) no se elimina, se conserva todo su historial para trazabilidad.

2. Gestion de Lotes Productivos
Control del ciclo agricola.
- Registro con fecha de siembra (YYYY-MM-DD) y area en m2 (RF05).
- Estados: EN_PRODUCCION -> COSECHADO.
- Al registrar la cosecha (RF07), el sistema crea automaticamente una ENTRADA al inventario.
- Un lote en estado COSECHADO no puede volver a cosecharse (Regla de Negocio 5).

3. Movimientos de Inventario - Kardex
Corazon del sistema.
- Registro manual de ENTRADAS y SALIDAS con motivo obligatorio (RF08).
- Regla de Oro (Regla 3): El stock no se guarda, se calcula con la formula Stock Actual = Suma(ENTRADAS) - Suma(SALIDAS).
- Valida stock insuficiente antes de cualquier SALIDA (Regla 4).
- Funcion calcular_stock() recorre todo el historial para dar el dato real.

4. Modulo de Ventas
- Permite vender multiples productos en una sola transaccion (RF11).
- Valida stock en tiempo real y estado activo del producto.
- Por cada producto vendido, genera un movimiento de SALIDA con motivo Venta V0001.
- Calculo automatico de subtotal y total de la venta.

5. Reportes y Alertas
- Alertas de Stock Bajo (RF12): Alerta cuando stock_actual <= stock_minimo.
- Reporte de existencias valorizado.
- Reporte de ingresos y ranking de los 3 productos mas vendidos.

Como Ejecutar

Requisitos: Python 3.8 o superior. No necesita instalar librerias externas.

1. Guarda el codigo como main.py
2. Abre la terminal en esa carpeta
3. Ejecuta: python main.py

El sistema creara automaticamente la carpeta data/ y los archivos JSON con manejo seguro para archivos vacios.

Buenas Practicas Implementadas

- Manejo de errores con try/except para evitar que el programa se caiga (RF18).
- Archivos con codificacion utf-8 para tildes y caracteres especiales.
- IDs secuenciales con formato M0001, V0001 para trazabilidad.
- Persistencia de datos inmediata con guardar_datos() despues de cada operacion.
- Uso de Pathlib para compatibilidad de rutas.

Tecnologias Utilizadas

- Python 3
- JSON para persistencia de datos
- Programacion Modular con menus interactivos
- Datetime para registro de fechas
- Visual Code Studio
- GitHub

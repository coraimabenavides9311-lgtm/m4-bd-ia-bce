
"""Flujo ETL de exportaciones: extrae, valida y guarda datos.

Integrantes: Trabajo individual.
Fuente: datos/exportaciones.csv (datos sintéticos de ejemplo).

SI FALLA: Si la fuente no está disponible o los datos presentan
inconsistencias, el proceso se detiene y registra el error.
Se debe informar al responsable de la fuente de información
para que revise y corrija los datos.
"""

import logging
import sys
import os
from datetime import date
import pandas as pd

# ---------- 1. PARAMETROS ----------

RUTA_ENTRADA = "datos/exportaciones.csv"
SALIDA = f"salida/mi_flujo_{date.today().isoformat()}.csv"
FILAS_ESPERADAS = 6
COLUMNAS_ESPERADAS = 2

# ---------- CONFIGURACION DEL REGISTRO ----------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("flujo.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("mi_flujo")


# ---------- 2. FUNCIONES ETL ----------

def extraer():
    """Extrae los datos del archivo CSV de exportaciones."""

    tabla = pd.read_csv(RUTA_ENTRADA)

    log.info("extraidas %d filas", len(tabla))

    return tabla


def transformar(tabla):
    """Valida la cantidad de filas, columnas y valores numericos."""

    if len(tabla) != FILAS_ESPERADAS:
        raise ValueError(
            f"esperaba {FILAS_ESPERADAS} filas y llegaron {len(tabla)}"
        )

    if len(tabla.columns) != COLUMNAS_ESPERADAS:
        raise ValueError(
            f"esperaba {COLUMNAS_ESPERADAS} columnas"
        )

    columna_monto = "monto_mm_usd"

    if columna_monto not in tabla.columns:
        raise ValueError("No existe la columna de montos")

    tabla[columna_monto] = pd.to_numeric(
        tabla[columna_monto], errors="raise"
    )

    if tabla[columna_monto].isna().any():
        raise ValueError("Existen montos vacios")

    if (tabla[columna_monto] < 0).any():
        raise ValueError("Existen montos negativos")

    log.info("transformacion y validaciones correctas")

    return tabla


def cargar(tabla):
    """Guarda los datos validados en un archivo CSV con fecha."""

    os.makedirs("salida", exist_ok=True)

    tabla.to_csv(SALIDA, index=False)

    log.info("guardado %s (%d filas)", SALIDA, len(tabla))


# ---------- 3. EJECUCION DEL FLUJO ----------

if __name__ == "__main__":

    try:
        cargar(transformar(extraer()))
        log.info("FIN OK")

    except Exception as error:
        log.error("EL FLUJO FALLO: %s", error)
        sys.exit(1)

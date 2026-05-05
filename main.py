"""
Perfilador de Datasets CSV

Herramienta que analiza archivos CSV y genera reportes de calidad de datos.
Evalua completitud, tipos de datos, unicidad y valores nulos de cada columna.

Uso:
    python main.py --input data/ventas.csv --output outputs/perfil_ventas.csv
    python main.py -i data/empleados.csv -o outputs/perfil_empleados.csv

Autor: Diego — ESCOM IPN, 2026
"""

import argparse
import csv
import os
import sys


# ============================================================================
# FUNCIONES DE DETECCION
# ============================================================================

def es_valor_nulo(valor):
    """
    Determina si un valor se considera nulo.

    Nulo: None, string vacio, string con solo espacios.
    NO nulo: 0, "0", "null", "None", cualquier otro texto.

    Args:
        valor: El valor a evaluar.

    Returns:
        bool: True si el valor es nulo.
    """
    if valor is None:
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    return False


def es_numerico(valor):
    """
    Verifica si un valor es numerico (entero o decimal).

    Args:
        valor: El valor a evaluar.

    Returns:
        bool: True si el valor se puede convertir a float.
    """
    try:
        float(str(valor).replace(',', '').strip())
        return True
    except (ValueError, TypeError):
        return False


def es_fecha(valor):
    """
    Verifica si un valor tiene formato de fecha YYYY-MM-DD.
    Tambien acepta datetime con formato YYYY-MM-DD HH:MM:SS.

    Args:
        valor: El valor a evaluar.

    Returns:
        bool: True si el valor parece una fecha valida.
    """
    v = str(valor).strip()

    if len(v) < 10:
        return False

    fecha_parte = v[:10]

    if len(fecha_parte) != 10:
        return False
    if fecha_parte[4] != '-' or fecha_parte[7] != '-':
        return False

    try:
        partes = fecha_parte.split('-')
        if len(partes) != 3:
            return False
        anio = int(partes[0])
        mes = int(partes[1])
        dia = int(partes[2])
        if 1900 <= anio <= 2100 and 1 <= mes <= 12 and 1 <= dia <= 31:
            return True
    except (ValueError, IndexError):
        pass

    return False


def es_booleano(valor):
    """
    Verifica si un valor es booleano.

    Args:
        valor: El valor a evaluar.

    Returns:
        bool: True si el valor es un booleano reconocido.
    """
    v = str(valor).strip().lower()
    return v in ['true', 'false', 'yes', 'no', 'si', '1', '0', 't', 'f']


# ============================================================================
# INFERENCIA DE TIPO
# ============================================================================

def inferir_tipo_columna(valores):
    """
    Infiere el tipo de dato de una columna basado en sus valores no nulos.

    Regla: si >80% de los valores corresponden a un tipo, se asigna ese tipo.
    Prioridad: fecha > booleano > numerico > texto.

    Args:
        valores: Lista de valores de la columna.

    Returns:
        str: 'numerico', 'fecha', 'booleano' o 'texto'.
    """
    valores_validos = [v for v in valores if not es_valor_nulo(v)]

    if not valores_validos:
        return "texto"

    total = len(valores_validos)
    umbral = 0.8

    num_fechas = sum(1 for v in valores_validos if es_fecha(v))
    num_booleanos = sum(1 for v in valores_validos if es_booleano(v))
    num_numericos = sum(1 for v in valores_validos if es_numerico(v))

    # Prioridad: fecha > booleano > numerico > texto
    if num_fechas / total >= umbral:
        return "fecha"
    elif num_booleanos / total >= umbral:
        return "booleano"
    elif num_numericos / total >= umbral:
        return "numerico"
    else:
        return "texto"


# ============================================================================
# METRICAS
# ============================================================================

def calcular_porcentaje(parte, total):
    """
    Calcula porcentaje con 2 decimales.

    Args:
        parte: Numerador.
        total: Denominador.

    Returns:
        float: Porcentaje redondeado a 2 decimales.
    """
    if total == 0:
        return 0.00
    return round((parte / total) * 100, 2)


def contar_unicos(valores):
    """
    Cuenta valores unicos excluyendo nulos.

    Args:
        valores: Lista de valores.

    Returns:
        int: Cantidad de valores unicos no nulos.
    """
    valores_no_nulos = [v for v in valores if not es_valor_nulo(v)]
    return len(set(valores_no_nulos))


# ============================================================================
# PERFILADO
# ============================================================================

def perfilar_columna(nombre, valores):
    """
    Genera el perfil completo de una columna.

    Args:
        nombre: Nombre de la columna.
        valores: Lista de valores de la columna.

    Returns:
        dict: Diccionario con las metricas del perfil.
    """
    total = len(valores)
    nulos = sum(1 for v in valores if es_valor_nulo(v))
    valores_no_nulos = [v for v in valores if not es_valor_nulo(v)]
    unicos = len(set(valores_no_nulos))
    ejemplo = valores_no_nulos[0] if valores_no_nulos else ""
    tipo = inferir_tipo_columna(valores)

    return {
        "nombre_columna": nombre,
        "tipo_inferido": tipo,
        "total_registros": total,
        "valores_nulos": nulos,
        "porcentaje_nulos": calcular_porcentaje(nulos, total),
        "valores_unicos": unicos,
        "porcentaje_unicos": calcular_porcentaje(unicos, total),
        "ejemplo_valor": ejemplo
    }


# ============================================================================
# LECTURA Y ESCRITURA DE CSV
# ============================================================================

def leer_csv(ruta_archivo):
    """
    Lee un archivo CSV y retorna encabezados y filas.

    Args:
        ruta_archivo: Ruta al archivo CSV.

    Returns:
        tuple: (encabezados, filas) donde ambos son listas.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo esta vacio o no tiene datos.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontro el archivo: {ruta_archivo}")

    with open(ruta_archivo, 'r', encoding='utf-8', newline='') as archivo:
        lector = csv.reader(archivo)
        filas_todas = list(lector)

    if not filas_todas:
        raise ValueError(f"El archivo esta vacio: {ruta_archivo}")

    encabezados = filas_todas[0]
    filas = filas_todas[1:]

    if not filas:
        raise ValueError(f"El archivo no tiene datos (solo encabezados): {ruta_archivo}")

    return encabezados, filas


def escribir_csv(ruta_archivo, perfiles):
    """
    Escribe los perfiles en un archivo CSV de salida.

    Args:
        ruta_archivo: Ruta donde guardar el CSV.
        perfiles: Lista de diccionarios con los perfiles.
    """
    # Crear directorio de salida si no existe
    directorio = os.path.dirname(ruta_archivo)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    columnas = [
        "nombre_columna", "tipo_inferido", "total_registros",
        "valores_nulos", "porcentaje_nulos", "valores_unicos",
        "porcentaje_unicos", "ejemplo_valor"
    ]

    with open(ruta_archivo, 'w', encoding='utf-8', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)

        for p in perfiles:
            fila = [
                str(p["nombre_columna"]),
                str(p["tipo_inferido"]),
                str(p["total_registros"]),
                str(p["valores_nulos"]),
                f"{p['porcentaje_nulos']:.2f}",
                str(p["valores_unicos"]),
                f"{p['porcentaje_unicos']:.2f}",
                str(p["ejemplo_valor"])
            ]
            escritor.writerow(fila)


# ============================================================================
# FUNCION PRINCIPAL
# ============================================================================

def perfilar_dataset(ruta_entrada):
    """
    Perfila un dataset CSV completo.

    Args:
        ruta_entrada: Ruta al archivo CSV de entrada.

    Returns:
        list: Lista de diccionarios con el perfil de cada columna.
    """
    encabezados, filas = leer_csv(ruta_entrada)
    perfiles = []

    for i, nombre_col in enumerate(encabezados):
        # Extraer valores de esta columna
        valores = []
        for fila in filas:
            if i < len(fila):
                valores.append(fila[i])
            else:
                valores.append("")  # Columna faltante en esta fila
        perfil = perfilar_columna(nombre_col, valores)
        perfiles.append(perfil)

    return perfiles


def mostrar_resumen(perfiles):
    """
    Muestra un resumen del perfil en la consola.

    Args:
        perfiles: Lista de diccionarios con los perfiles.
    """
    print("=" * 70)
    print("PERFIL DEL DATASET")
    print("=" * 70)

    for p in perfiles:
        print(f"\n--- {p['nombre_columna']} ---")
        print(f"  Tipo inferido:      {p['tipo_inferido']}")
        print(f"  Total registros:    {p['total_registros']}")
        print(f"  Valores nulos:      {p['valores_nulos']} ({p['porcentaje_nulos']}%)")
        print(f"  Valores unicos:     {p['valores_unicos']} ({p['porcentaje_unicos']}%)")
        print(f"  Ejemplo:            '{p['ejemplo_valor']}'")

    print("\n" + "=" * 70)


def main():
    """Punto de entrada principal del programa."""
    # Configurar argumentos de linea de comandos
    parser = argparse.ArgumentParser(
        description="Perfilador de Datasets CSV - Genera reportes de calidad de datos"
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Ruta al archivo CSV de entrada"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Ruta al archivo CSV de salida"
    )

    args = parser.parse_args()

    # Validar archivo de entrada
    if not os.path.exists(args.input):
        print(f"Error: No se encontro el archivo de entrada: {args.input}")
        sys.exit(1)

    print(f"Perfilando: {args.input}")

    try:
        # Perfilar dataset
        perfiles = perfilar_dataset(args.input)

        # Mostrar resumen en consola
        mostrar_resumen(perfiles)

        # Escribir CSV de salida
        escribir_csv(args.output, perfiles)
        print(f"\nPerfil guardado en: {args.output}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

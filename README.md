# Perfilador de Datasets

Herramienta de linea de comandos que analiza archivos CSV y genera reportes automaticos de calidad de datos. Evalua completitud, tipos de datos, unicidad y valores nulos de cada columna.

## Requisitos

- Python 3.8 o superior

## Instalacion

### 1. Clonar el repositorio
```bash
git clone https://github.com/DJ-Bus/reto-semana-05.git
cd reto-semana-05
```

### 2. Crear ambiente virtual
```bash
python -m venv .venv
```

### 3. Activar ambiente virtual
```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py --input <archivo_entrada.csv> --output <archivo_salida.csv>
```

### Ejemplos
```bash
python main.py --input data/ventas.csv --output outputs/perfil_ventas.csv
python main.py -i data/empleados.csv -o outputs/perfil_empleados.csv
python main.py -i data/sensores.csv -o outputs/perfil_sensores.csv
```

## Formato de Salida

El perfil generado contiene una fila por columna del CSV analizado:

| Columna | Descripcion |
|---------|-------------|
| nombre_columna | Nombre de la columna |
| tipo_inferido | Tipo detectado: numerico / texto / fecha / booleano |
| total_registros | Total de filas (sin encabezado) |
| valores_nulos | Cantidad de celdas vacias |
| porcentaje_nulos | % de nulos (2 decimales) |
| valores_unicos | Cantidad de valores distintos (sin nulos) |
| porcentaje_unicos | % de unicidad (2 decimales) |
| ejemplo_valor | Primer valor no nulo encontrado |

## Estructura del Proyecto

```
reto-semana-05/
├── main.py                 # Programa principal
├── requirements.txt        # Dependencias (biblioteca estandar)
├── README.md               # Este archivo
├── .gitignore              # Archivos ignorados por git
├── data/                   # CSVs de prueba
│   ├── ventas.csv
│   ├── empleados.csv
│   └── sensores.csv
└── outputs/                # Perfiles generados
    └── (se generan al ejecutar)
```

## Autor

Diego Bustamante — ESCOM IPN, Programacion para Ciencia de Datos, 2026
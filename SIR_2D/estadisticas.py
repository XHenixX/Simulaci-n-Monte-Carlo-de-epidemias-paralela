import csv
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENTRADA = os.path.join(
    BASE_DIR,
    "paralelo",
    "resultados_paralelo.csv"
)

SALIDA = os.path.join(
    BASE_DIR,
    "paralelo",
    "estadisticas_completas.csv"
)

POBLACION = 1000000
INFECTADOS_INICIALES = 1000


# ============================================================
# LEER CSV
# ============================================================

def leer_datos():

    with open(
        ENTRADA,
        "r",
        newline="",
        encoding="utf-8"
    ) as archivo:

        reader = csv.DictReader(archivo)

        datos = list(reader)

    return datos


# ============================================================
# BUSCAR COLUMNAS
# ============================================================

def obtener_columna(fila, nombres):

    for nombre in nombres:

        if nombre in fila:
            return nombre

    return None


# ============================================================
# PROCESAR ESTADÍSTICAS
# ============================================================

def procesar():

    datos = leer_datos()

    if not datos:

        print("El archivo CSV está vacío.")
        return

    print()
    print("=" * 65)
    print("GENERACIÓN DE ESTADÍSTICAS DEL MODELO SIR")
    print("=" * 65)

    print()
    print(f"Archivo de entrada:")
    print(ENTRADA)

    # Detectar nombres de columnas

    primera_fila = datos[0]

    columna_dia = obtener_columna(
        primera_fila,
        [
            "Dia",
            "Día",
            "dia",
            "day",
            "DAY"
        ]
    )

    columna_s = obtener_columna(
        primera_fila,
        [
            "Susceptibles",
            "S",
            "susceptibles"
        ]
    )

    columna_i = obtener_columna(
        primera_fila,
        [
            "Infectados",
            "I",
            "infectados"
        ]
    )

    columna_r = obtener_columna(
        primera_fila,
        [
            "Recuperados",
            "R",
            "recuperados"
        ]
    )

    columna_d = obtener_columna(
        primera_fila,
        [
            "Muertos",
            "D",
            "muertos"
        ]
    )

    print()
    print("Columnas detectadas:")

    print("Día:", columna_dia)
    print("Susceptibles:", columna_s)
    print("Infectados:", columna_i)
    print("Recuperados:", columna_r)
    print("Muertos:", columna_d)

    if columna_i is None:

        print()
        print(
            "ERROR: no se encontró la columna "
            "de infectados."
        )

        print()
        print(
            "Columnas disponibles:"
        )

        print(
            list(primera_fila.keys())
        )

        return

    resultados = []

    infectados_anterior = None

    for indice, fila in enumerate(datos):

        # ----------------------------------------------------
        # DÍA
        # ----------------------------------------------------

        if columna_dia:

            try:
                dia = int(
                    float(
                        fila[columna_dia]
                    )
                )

            except:
                dia = indice

        else:

            dia = indice

        # ----------------------------------------------------
        # ESTADOS
        # ----------------------------------------------------

        try:
            susceptibles = int(
                float(
                    fila[columna_s]
                )
            ) if columna_s else 0

        except:
            susceptibles = 0

        try:
            infectados = int(
                float(
                    fila[columna_i]
                )
            )

        except:
            infectados = 0

        try:
            recuperados = int(
                float(
                    fila[columna_r]
                )
            ) if columna_r else 0

        except:
            recuperados = 0

        try:
            muertos = int(
                float(
                    fila[columna_d]
                )
            ) if columna_d else 0

        except:
            muertos = 0

        # ----------------------------------------------------
        # NUEVOS INFECTADOS
        # ----------------------------------------------------

        if infectados_anterior is None:

            nuevos_infectados = 0

        else:

            nuevos_infectados = (
                susceptibles_anterior
                - susceptibles
            )

            if nuevos_infectados < 0:
                nuevos_infectados = 0

        # ----------------------------------------------------
        # INFECTADOS ACUMULADOS
        # ----------------------------------------------------

        infectados_acumulados = (
            POBLACION - susceptibles
        )

        # ----------------------------------------------------
        # R ESTIMADO
        # ----------------------------------------------------

        if (
            infectados_anterior is not None
            and infectados_anterior > 0
        ):

            r_estimado = (
                nuevos_infectados
                / infectados_anterior
            )

        else:

            r_estimado = 0

        resultados.append({
            "Dia": dia,
            "Susceptibles": susceptibles,
            "Infectados": infectados,
            "Recuperados": recuperados,
            "Muertos": muertos,
            "Nuevos infectados": nuevos_infectados,
            "Infectados acumulados": infectados_acumulados,
            "R0 estimado": r_estimado
        })

        infectados_anterior = infectados
        susceptibles_anterior = susceptibles

    # ========================================================
    # GUARDAR
    # ========================================================

    columnas = [
        "Dia",
        "Susceptibles",
        "Infectados",
        "Recuperados",
        "Muertos",
        "Nuevos infectados",
        "Infectados acumulados",
        "R0 estimado"
    ]

    with open(
        SALIDA,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        writer = csv.DictWriter(
            archivo,
            fieldnames=columnas
        )

        writer.writeheader()

        writer.writerows(
            resultados
        )

    print()
    print("=" * 65)
    print("ESTADÍSTICAS GENERADAS")
    print("=" * 65)

    print()
    print(
        f"Archivo creado:"
    )

    print(SALIDA)

    print()
    print(
        f"Días procesados: "
        f"{len(resultados)}"
    )

    # ========================================================
    # ESTADÍSTICAS GLOBALES
    # ========================================================

    max_infectados = max(
        r["Infectados"]
        for r in resultados
    )

    total_infectados = (
        resultados[-1]
        ["Infectados acumulados"]
    )

    max_r = max(
        r["R0 estimado"]
        for r in resultados
    )

    dia_max_infectados = next(
        r["Dia"]
        for r in resultados
        if r["Infectados"] == max_infectados
    )

    print()
    print("RESUMEN")
    print("-" * 65)

    print(
        f"Máximo de infectados simultáneos: "
        f"{max_infectados}"
    )

    print(
        f"Día del máximo de infectados: "
        f"{dia_max_infectados}"
    )

    print(
        f"Infectados acumulados finales: "
        f"{total_infectados}"
    )

    print(
        f"Máximo R estimado: "
        f"{max_r:.4f}"
    )

    print()
    print("Proceso completado.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    procesar()
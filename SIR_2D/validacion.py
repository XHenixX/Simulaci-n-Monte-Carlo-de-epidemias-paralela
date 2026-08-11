import sys
import os
import numpy as np
import multiprocessing as mp


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SECUENCIAL_DIR = os.path.join(
    BASE_DIR,
    "secuencial"
)

PARALELO_DIR = os.path.join(
    BASE_DIR,
    "paralelo"
)

sys.path.insert(
    0,
    SECUENCIAL_DIR
)

sys.path.insert(
    0,
    PARALELO_DIR
)


# ============================================================
# IMPORTAR VERSIONES
# ============================================================

import importlib.util


def load_module(name, path):

    spec = importlib.util.spec_from_file_location(
        name,
        path
    )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


secuencial = load_module(
    "secuencial",
    os.path.join(
        SECUENCIAL_DIR,
        "sir_secuencial.py"
    )
)

paralelo = load_module(
    "paralelo",
    os.path.join(
        PARALELO_DIR,
        "sir_paralelo.py"
    )
)


# ============================================================
# CONFIGURACIÓN DE LA PRUEBA
# ============================================================

SIZE = 20
DAYS = 10
PROCESSES = 4
INITIAL_INFECTED = 5
SEED = 42


# ============================================================
# SIMULACIÓN SECUENCIAL
# ============================================================

def run_sequential():

    print()
    print("Ejecutando versión SECUENCIAL...")

    grid = secuencial.create_population(
        SIZE,
        INITIAL_INFECTED,
        SEED
    )

    rng = np.random.default_rng(
        SEED + 1
    )

    for day in range(DAYS):

        grid = secuencial.update_day(
            grid,
            rng
        )

    return grid


# ============================================================
# SIMULACIÓN PARALELA
# ============================================================

def run_parallel():

    print(
        "Ejecutando versión PARALELA..."
    )

    grid = paralelo.create_population(
        SIZE,
        INITIAL_INFECTED,
        SEED
    )

    for day in range(DAYS):

        blocks = paralelo.create_blocks(
            grid,
            PROCESSES
        )

        with mp.Pool(
            processes=PROCESSES
        ) as pool:

            results = pool.map(
                process_block,
                blocks
            )

        grid = np.vstack(
            results
        )

    return grid


# ============================================================
# COMPARACIÓN
# ============================================================

def main():

    print("=" * 60)
    print("VALIDACIÓN SECUENCIAL VS PARALELO")
    print("=" * 60)

    print()
    print(f"Tamaño de grilla: {SIZE} x {SIZE}")
    print(f"Personas: {SIZE * SIZE}")
    print(f"Días: {DAYS}")
    print(f"Procesos paralelos: {PROCESSES}")
    print(f"Infectados iniciales: {INITIAL_INFECTED}")
    print(f"Semilla: {SEED}")

    # --------------------------------------------------------
    # EJECUTAR
    # --------------------------------------------------------

    sequential_grid = run_sequential()

    parallel_grid = run_parallel()

    # --------------------------------------------------------
    # COMPARAR
    # --------------------------------------------------------

    equal = np.array_equal(
        sequential_grid,
        parallel_grid
    )

    print()
    print("=" * 60)
    print("RESULTADO DE LA VALIDACIÓN")
    print("=" * 60)

    if equal:

        print()
        print("✓ CORRECTO")
        print()
        print(
            "La versión secuencial y la versión "
            "paralela producen exactamente el "
            "mismo resultado."
        )

    else:

        print()
        print("✗ ERROR")
        print()
        print(
            "Los resultados de la versión secuencial "
            "y paralela son diferentes."
        )

        # Cantidad de celdas diferentes

        differences = np.count_nonzero(
            sequential_grid != parallel_grid
        )

        print()
        print(
            f"Cantidad de celdas diferentes: "
            f"{differences}"
        )

    # --------------------------------------------------------
    # ESTADÍSTICAS FINALES
    # --------------------------------------------------------

    print()
    print("ESTADÍSTICAS FINALES")
    print("-" * 60)

    for name, grid in [
        ("Secuencial", sequential_grid),
        ("Paralelo", parallel_grid)
    ]:

        susceptible = np.count_nonzero(
            grid == 0
        )

        infected = np.count_nonzero(
            grid == 1
        )

        recovered = np.count_nonzero(
            grid == 2
        )

        dead = np.count_nonzero(
            grid == 3
        )

        print()
        print(name)
        print(
            f"Susceptibles: {susceptible}"
        )
        print(
            f"Infectados: {infected}"
        )
        print(
            f"Recuperados: {recovered}"
        )
        print(
            f"Muertos: {dead}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    mp.freeze_support()

    main()
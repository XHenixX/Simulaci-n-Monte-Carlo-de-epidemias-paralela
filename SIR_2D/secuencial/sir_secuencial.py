import numpy as np
import time
import csv
import os


# ============================================================
# CONFIGURACIÓN DEL MODELO
# ============================================================

GRID_SIZE = 1000
DAYS = 365

# Probabilidades del modelo
BETA = 0.20       # Probabilidad de contagio por vecino infectado
GAMMA = 0.05      # Probabilidad de recuperación
MU = 0.01         # Probabilidad de muerte

# Cantidad inicial de infectados
INITIAL_INFECTED = 1000

# Semilla para que los experimentos sean reproducibles
SEED = 42

# Estados
SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2
DEAD = 3


# ============================================================
# CREAR POBLACIÓN
# ============================================================

def create_population(size, initial_infected, seed=42):
    """
    Crea una población completamente susceptible
    y coloca una cantidad determinada de infectados.
    """

    rng = np.random.default_rng(seed)

    grid = np.zeros((size, size), dtype=np.uint8)

    total_cells = size * size

    infected_positions = rng.choice(
        total_cells,
        size=initial_infected,
        replace=False
    )

    grid.flat[infected_positions] = INFECTED

    return grid


# ============================================================
# CONTAR VECINOS INFECTADOS
# ============================================================

def count_infected_neighbors(grid):
    """
    Cuenta los vecinos infectados utilizando una vecindad de Moore:
    los 8 vecinos alrededor de cada persona.

    Los bordes se consideran conectados mediante condiciones periódicas.
    """

    infected = (grid == INFECTED).astype(np.uint8)

    neighbors = (
        np.roll(infected, 1, axis=0)
        + np.roll(infected, -1, axis=0)
        + np.roll(infected, 1, axis=1)
        + np.roll(infected, -1, axis=1)
        + np.roll(np.roll(infected, 1, axis=0), 1, axis=1)
        + np.roll(np.roll(infected, 1, axis=0), -1, axis=1)
        + np.roll(np.roll(infected, -1, axis=0), 1, axis=1)
        + np.roll(np.roll(infected, -1, axis=0), -1, axis=1)
    )

    return neighbors


# ============================================================
# ACTUALIZACIÓN DE UN DÍA
# ============================================================

def update_day(grid, rng):
    """
    Calcula el estado de toda la población para el día siguiente.
    """

    new_grid = grid.copy()

    infected_neighbors = count_infected_neighbors(grid)

    # --------------------------------------------------------
    # SUSCEPTIBLES
    # --------------------------------------------------------

    susceptible = (grid == SUSCEPTIBLE)

    # P(contagio) = 1 - (1 - beta)^k
    infection_probability = (
        1 - np.power(1 - BETA, infected_neighbors)
    )

    random_values = rng.random(grid.shape)

    new_infections = (
        susceptible
        & (infected_neighbors > 0)
        & (random_values < infection_probability)
    )

    new_grid[new_infections] = INFECTED

    # --------------------------------------------------------
    # INFECTADOS
    # --------------------------------------------------------

    infected = (grid == INFECTED)

    random_recovery = rng.random(grid.shape)
    random_death = rng.random(grid.shape)

    deaths = (
        infected
        & (random_death < MU)
    )

    recoveries = (
        infected
        & ~deaths
        & (random_recovery < GAMMA)
    )

    new_grid[deaths] = DEAD
    new_grid[recoveries] = RECOVERED

    return new_grid


# ============================================================
# ESTADÍSTICAS
# ============================================================

def calculate_statistics(grid):
    """
    Calcula la cantidad de personas en cada estado.
    """

    susceptible = np.count_nonzero(grid == SUSCEPTIBLE)
    infected = np.count_nonzero(grid == INFECTED)
    recovered = np.count_nonzero(grid == RECOVERED)
    dead = np.count_nonzero(grid == DEAD)

    return susceptible, infected, recovered, dead


# ============================================================
# SIMULACIÓN
# ============================================================

def simulate(size=GRID_SIZE, days=DAYS, seed=SEED):
    """
    Ejecuta la simulación completa.
    """

    grid = create_population(
        size,
        INITIAL_INFECTED,
        seed
    )

    rng = np.random.default_rng(seed + 1)

    statistics = []

    # Estadísticas del día 0
    s, i, r, d = calculate_statistics(grid)

    statistics.append([
        0,
        s,
        i,
        r,
        d
    ])

    start_time = time.perf_counter()

    for day in range(1, days + 1):

        grid = update_day(grid, rng)

        s, i, r, d = calculate_statistics(grid)

        statistics.append([
            day,
            s,
            i,
            r,
            d
        ])

        if day % 50 == 0:
            print(
                f"Día {day}/{days} - "
                f"S={s}, I={i}, R={r}, D={d}"
            )

    end_time = time.perf_counter()

    total_time = end_time - start_time

    return grid, statistics, total_time


# ============================================================
# GUARDAR CSV
# ============================================================

def save_statistics(statistics, filename):

    os.makedirs(
        os.path.dirname(filename),
        exist_ok=True
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Dia",
            "Susceptibles",
            "Infectados",
            "Recuperados",
            "Muertos"
        ])

        writer.writerows(statistics)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MODELO SIR 2-D - VERSIÓN SECUENCIAL")
    print("=" * 60)

    print(f"Grilla: {GRID_SIZE} x {GRID_SIZE}")
    print(f"Personas: {GRID_SIZE * GRID_SIZE:,}")
    print(f"Días: {DAYS}")
    print(f"Beta: {BETA}")
    print(f"Gamma: {GAMMA}")
    print(f"Mu: {MU}")
    print()

    final_grid, statistics, total_time = simulate()

    output_file = os.path.join(
        os.path.dirname(__file__),
        "resultados_secuencial.csv"
    )

    save_statistics(
        statistics,
        output_file
    )

    print()
    print("=" * 60)
    print("SIMULACIÓN FINALIZADA")
    print("=" * 60)

    print(f"Tiempo total: {total_time:.4f} segundos")
    print(f"Resultados guardados en:")
    print(output_file)
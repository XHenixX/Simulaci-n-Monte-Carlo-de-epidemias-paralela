import numpy as np
import multiprocessing as mp
import time
import csv
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

GRID_SIZE = 1000
DAYS = 365

BETA = 0.20
GAMMA = 0.05
MU = 0.01

INITIAL_INFECTED = 1000

SEED = 42

SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2
DEAD = 3


# ============================================================
# CREAR POBLACIÓN
# ============================================================

def create_population(size, initial_infected, seed=42):

    rng = np.random.default_rng(seed)

    grid = np.zeros(
        (size, size),
        dtype=np.uint8
    )

    positions = rng.choice(
        size * size,
        size=initial_infected,
        replace=False
    )

    grid.flat[positions] = INFECTED

    return grid


# ============================================================
# CONTAR VECINOS
# ============================================================

def count_infected_neighbors(grid):

    infected = (
        grid == INFECTED
    ).astype(np.uint8)

    neighbors = (
        np.roll(infected, 1, axis=0)
        + np.roll(infected, -1, axis=0)
        + np.roll(infected, 1, axis=1)
        + np.roll(infected, -1, axis=1)
        + np.roll(
            np.roll(infected, 1, axis=0),
            1,
            axis=1
        )
        + np.roll(
            np.roll(infected, 1, axis=0),
            -1,
            axis=1
        )
        + np.roll(
            np.roll(infected, -1, axis=0),
            1,
            axis=1
        )
        + np.roll(
            np.roll(infected, -1, axis=0),
            -1,
            axis=1
        )
    )

    return neighbors


# ============================================================
# PROCESAR BLOQUE
# ============================================================

def process_block(args):

    block_with_ghost, real_rows, seed = args

    rng = np.random.default_rng(seed)

    infected_neighbors = (
        count_infected_neighbors(
            block_with_ghost
        )
    )

    new_block = block_with_ghost.copy()

    # --------------------------------------------------------
    # SUSCEPTIBLES
    # --------------------------------------------------------

    susceptible = (
        block_with_ghost == SUSCEPTIBLE
    )

    infection_probability = (
        1 -
        np.power(
            1 - BETA,
            infected_neighbors
        )
    )

    random_values = rng.random(
        block_with_ghost.shape
    )

    new_infections = (
        susceptible
        &
        (infected_neighbors > 0)
        &
        (
            random_values
            < infection_probability
        )
    )

    new_block[
        new_infections
    ] = INFECTED

    # --------------------------------------------------------
    # INFECTADOS
    # --------------------------------------------------------

    infected = (
        block_with_ghost == INFECTED
    )

    random_recovery = rng.random(
        block_with_ghost.shape
    )

    random_death = rng.random(
        block_with_ghost.shape
    )

    deaths = (
        infected
        &
        (random_death < MU)
    )

    recoveries = (
        infected
        &
        ~deaths
        &
        (random_recovery < GAMMA)
    )

    new_block[
        deaths
    ] = DEAD

    new_block[
        recoveries
    ] = RECOVERED

    # Eliminamos las ghost cells
    result = new_block[
        1:1 + real_rows,
        :
    ]

    return result


# ============================================================
# CREAR BLOQUES + GHOST CELLS
# ============================================================

def create_blocks(grid, processes):

    rows = grid.shape[0]

    boundaries = np.linspace(
        0,
        rows,
        processes + 1,
        dtype=int
    )

    blocks = []

    for p in range(processes):

        start = boundaries[p]
        end = boundaries[p + 1]

        real_block = grid[
            start:end,
            :
        ]

        # Ghost superior
        top = grid[
            (start - 1) % rows,
            :
        ]

        # Ghost inferior
        bottom = grid[
            end % rows,
            :
        ]

        block_with_ghost = np.vstack([
            top[np.newaxis, :],
            real_block,
            bottom[np.newaxis, :]
        ])

        blocks.append(
            (
                block_with_ghost,
                end - start,
                SEED + p
            )
        )

    return blocks


# ============================================================
# ESTADÍSTICAS
# ============================================================

def calculate_statistics(grid):

    s = np.count_nonzero(
        grid == SUSCEPTIBLE
    )

    i = np.count_nonzero(
        grid == INFECTED
    )

    r = np.count_nonzero(
        grid == RECOVERED
    )

    d = np.count_nonzero(
        grid == DEAD
    )

    return s, i, r, d


# ============================================================
# SIMULACIÓN PARALELA
# ============================================================

def simulate(
    size=GRID_SIZE,
    days=DAYS,
    processes=4,
    seed=SEED
):

    grid = create_population(
        size,
        INITIAL_INFECTED,
        seed
    )

    statistics = []

    s, i, r, d = (
        calculate_statistics(grid)
    )

    statistics.append([
        0,
        s,
        i,
        r,
        d
    ])

    print(
        f"Ejecutando con "
        f"{processes} procesos..."
    )

    start_time = time.perf_counter()

    with mp.Pool(
        processes=processes
    ) as pool:

        for day in range(
            1,
            days + 1
        ):

            blocks = create_blocks(
                grid,
                processes
            )

            results = pool.map(
                process_block,
                blocks
            )

            grid = np.vstack(
                results
            )

            s, i, r, d = (
                calculate_statistics(
                    grid
                )
            )

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
                    f"S={s}, "
                    f"I={i}, "
                    f"R={r}, "
                    f"D={d}"
                )

    end_time = time.perf_counter()

    total_time = (
        end_time - start_time
    )

    return (
        grid,
        statistics,
        total_time
    )


# ============================================================
# CSV
# ============================================================

def save_statistics(
    statistics,
    filename
):

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

        writer.writerows(
            statistics
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    mp.freeze_support()

    print("=" * 60)
    print(
        "MODELO SIR 2-D - "
        "VERSIÓN PARALELA"
    )
    print("=" * 60)

    processes = 4

    final_grid, statistics, total_time = simulate(
        processes=processes
    )

    output_file = os.path.join(
        os.path.dirname(__file__),
        "resultados_paralelo.csv"
    )

    save_statistics(
        statistics,
        output_file
    )

    print()
    print("=" * 60)
    print("SIMULACIÓN PARALELA FINALIZADA")
    print("=" * 60)

    print(
        f"Procesos utilizados: {processes}"
    )

    print(
        f"Tiempo total: "
        f"{total_time:.4f} segundos"
    )

    print(
        f"Resultados guardados en:"
    )

    print(output_file)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import multiprocessing as mp
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

SIZE = 100
DAYS = 100

BETA = 0.20
GAMMA = 0.05
MU = 0.01

INITIAL_INFECTED = 5
SEED = 42

SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2
DEAD = 3

# Cantidad de procesos utilizados para la animación paralela
PROCESSES = 4


# ============================================================
# CREAR POBLACIÓN
# ============================================================

def create_population():

    rng = np.random.default_rng(SEED)

    grid = np.zeros(
        (SIZE, SIZE),
        dtype=np.uint8
    )

    positions = rng.choice(
        SIZE * SIZE,
        size=INITIAL_INFECTED,
        replace=False
    )

    grid.flat[positions] = INFECTED

    return grid


# ============================================================
# VECINOS - VERSIÓN SECUENCIAL
# ============================================================

def infected_neighbors(grid):

    infected = (
        grid == INFECTED
    ).astype(np.uint8)

    return (
        np.roll(infected, 1, 0)
        + np.roll(infected, -1, 0)
        + np.roll(infected, 1, 1)
        + np.roll(infected, -1, 1)
        + np.roll(
            np.roll(infected, 1, 0),
            1,
            1
        )
        + np.roll(
            np.roll(infected, 1, 0),
            -1,
            1
        )
        + np.roll(
            np.roll(infected, -1, 0),
            1,
            1
        )
        + np.roll(
            np.roll(infected, -1, 0),
            -1,
            1
        )
    )


# ============================================================
# ACTUALIZACIÓN SECUENCIAL
# ============================================================

def update_sequential(
    grid,
    random_infection,
    random_death,
    random_recovery
):

    new_grid = grid.copy()

    neighbors = infected_neighbors(
        grid
    )

    susceptible = (
        grid == SUSCEPTIBLE
    )

    probability = (
        1 -
        (1 - BETA) ** neighbors
    )

    infections = (
        susceptible
        &
        (neighbors > 0)
        &
        (
            random_infection
            < probability
        )
    )

    new_grid[
        infections
    ] = INFECTED

    infected = (
        grid == INFECTED
    )

    deaths = (
        infected
        &
        (
            random_death < MU
        )
    )

    recoveries = (
        infected
        &
        ~deaths
        &
        (
            random_recovery
            < GAMMA
        )
    )

    new_grid[
        deaths
    ] = DEAD

    new_grid[
        recoveries
    ] = RECOVERED

    return new_grid


# ============================================================
# ACTUALIZACIÓN DE UN BLOQUE PARALELO
# ============================================================

def update_block(args):

    (
        grid,
        start,
        end,
        random_infection,
        random_death,
        random_recovery
    ) = args

    rows = grid.shape[0]
    cols = grid.shape[1]

    # --------------------------------------------------------
    # Ghost cells
    # --------------------------------------------------------

    ghost_top = (
        start - 1
    ) % rows

    ghost_bottom = (
        end
    ) % rows

    block = np.vstack(
        (
            grid[ghost_top],
            grid[start:end],
            grid[ghost_bottom]
        )
    )

    infected = (
        block == INFECTED
    ).astype(np.uint8)

    # --------------------------------------------------------
    # Vecindad de Moore utilizando ghost cells
    # --------------------------------------------------------

    neighbors = np.zeros(
        (end - start, cols),
        dtype=np.uint8
    )

    center = infected[1:-1]

    top = infected[:-2]

    bottom = infected[2:]

    neighbors += top
    neighbors += bottom

    neighbors += np.roll(
        center,
        1,
        axis=1
    )

    neighbors += np.roll(
        center,
        -1,
        axis=1
    )

    neighbors += np.roll(
        top,
        1,
        axis=1
    )

    neighbors += np.roll(
        top,
        -1,
        axis=1
    )

    neighbors += np.roll(
        bottom,
        1,
        axis=1
    )

    neighbors += np.roll(
        bottom,
        -1,
        axis=1
    )

    # --------------------------------------------------------
    # Actualización
    # --------------------------------------------------------

    current = grid[
        start:end
    ]

    new_block = current.copy()

    susceptible = (
        current == SUSCEPTIBLE
    )

    probability = (
        1 -
        (1 - BETA) ** neighbors
    )

    infections = (
        susceptible
        &
        (neighbors > 0)
        &
        (
            random_infection
            < probability
        )
    )

    new_block[
        infections
    ] = INFECTED

    infected_mask = (
        current == INFECTED
    )

    deaths = (
        infected_mask
        &
        (
            random_death < MU
        )
    )

    recoveries = (
        infected_mask
        &
        ~deaths
        &
        (
            random_recovery
            < GAMMA
        )
    )

    new_block[
        deaths
    ] = DEAD

    new_block[
        recoveries
    ] = RECOVERED

    return start, end, new_block


# ============================================================
# ACTUALIZACIÓN PARALELA
# ============================================================

def update_parallel(
    grid,
    random_infection,
    random_death,
    random_recovery
):

    rows = grid.shape[0]

    # --------------------------------------------------------
    # Dividir la grilla en bloques
    # --------------------------------------------------------

    boundaries = np.linspace(
        0,
        rows,
        PROCESSES + 1,
        dtype=int
    )

    tasks = []

    for i in range(PROCESSES):

        start = boundaries[i]

        end = boundaries[i + 1]

        tasks.append(
            (
                grid,
                start,
                end,
                random_infection[start:end],
                random_death[start:end],
                random_recovery[start:end]
            )
        )

    # --------------------------------------------------------
    # Procesamiento paralelo
    # --------------------------------------------------------

    with mp.Pool(
        processes=PROCESSES
    ) as pool:

        results = pool.map(
            update_block,
            tasks
        )

    # --------------------------------------------------------
    # Reconstruir grilla
    # --------------------------------------------------------

    new_grid = np.empty_like(
        grid
    )

    for start, end, block in results:

        new_grid[
            start:end
        ] = block

    return new_grid


# ============================================================
# GENERAR SIMULACIONES
# ============================================================

def generate_simulations():

    print()
    print("=" * 65)
    print("GENERANDO SIMULACIONES")
    print("=" * 65)

    # --------------------------------------------------------
    # Misma población inicial
    # --------------------------------------------------------

    initial_grid = create_population()

    sequential_grid = (
        initial_grid.copy()
    )

    parallel_grid = (
        initial_grid.copy()
    )

    # --------------------------------------------------------
    # RNG independiente pero idéntico
    # --------------------------------------------------------

    rng = np.random.default_rng(
        SEED + 1
    )

    sequential_frames = [
        sequential_grid.copy()
    ]

    parallel_frames = [
        parallel_grid.copy()
    ]

    # --------------------------------------------------------
    # Simular días
    # --------------------------------------------------------

    for day in range(1, DAYS):

        print(
            f"\rGenerando día "
            f"{day}/{DAYS - 1}",
            end=""
        )

        # Mismos números aleatorios
        random_infection = (
            rng.random(
                (SIZE, SIZE)
            )
        )

        random_death = (
            rng.random(
                (SIZE, SIZE)
            )
        )

        random_recovery = (
            rng.random(
                (SIZE, SIZE)
            )
        )

        # ----------------------------------------------------
        # Secuencial
        # ----------------------------------------------------

        sequential_grid = (
            update_sequential(
                sequential_grid,
                random_infection,
                random_death,
                random_recovery
            )
        )

        # ----------------------------------------------------
        # Paralelo
        # ----------------------------------------------------

        parallel_grid = (
            update_parallel(
                parallel_grid,
                random_infection,
                random_death,
                random_recovery
            )
        )

        # ----------------------------------------------------
        # Guardar frames
        # ----------------------------------------------------

        sequential_frames.append(
            sequential_grid.copy()
        )

        parallel_frames.append(
            parallel_grid.copy()
        )

    print()
    print()

    # --------------------------------------------------------
    # Validación
    # --------------------------------------------------------

    iguales = np.array_equal(
        sequential_grid,
        parallel_grid
    )

    print(
        "¿Secuencial y paralelo producen "
        "el mismo resultado?",
        iguales
    )

    if iguales:

        print(
            "VALIDACIÓN EXITOSA: "
            "ambas simulaciones son idénticas."
        )

    else:

        print(
            "ADVERTENCIA: "
            "las simulaciones presentan diferencias."
        )

    return (
        sequential_frames,
        parallel_frames
    )


# ============================================================
# CREAR GIF
# ============================================================

def save_gif(
    frames,
    filename,
    title
):

    fig, ax = plt.subplots(
        figsize=(7, 7)
    )

    image = ax.imshow(
        frames[0],
        vmin=0,
        vmax=3,
        interpolation="nearest"
    )

    ax.set_axis_off()

    ax.set_title(
        f"{title} - Día 0"
    )

    def animate(day):

        image.set_data(
            frames[day]
        )

        ax.set_title(
            f"{title} - Día {day}"
        )

        return [
            image
        ]

    animation = FuncAnimation(
        fig,
        animate,
        frames=len(frames),
        interval=100,
        blit=True
    )

    output = os.path.join(
        os.path.dirname(__file__),
        filename
    )

    animation.save(
        output,
        writer=PillowWriter(
            fps=10
        )
    )

    plt.close(fig)

    print(
        f"GIF creado: {output}"
    )


# ============================================================
# CREAR SIDE-BY-SIDE
# ============================================================

def save_side_by_side(
    sequential_frames,
    parallel_frames
):

    print()
    print(
        "Generando comparación "
        "SECUENCIAL | PARALELO..."
    )

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 6)
    )

    image_seq = axes[0].imshow(
        sequential_frames[0],
        vmin=0,
        vmax=3,
        interpolation="nearest"
    )

    image_par = axes[1].imshow(
        parallel_frames[0],
        vmin=0,
        vmax=3,
        interpolation="nearest"
    )

    axes[0].set_title(
        "SECUENCIAL - Día 0"
    )

    axes[1].set_title(
        "PARALELO - Día 0"
    )

    axes[0].set_axis_off()
    axes[1].set_axis_off()

    fig.suptitle(
        "Modelo SIR 2-D: Secuencial vs Paralelo"
    )

    plt.tight_layout()

    def animate(day):

        image_seq.set_data(
            sequential_frames[day]
        )

        image_par.set_data(
            parallel_frames[day]
        )

        axes[0].set_title(
            f"SECUENCIAL - Día {day}"
        )

        axes[1].set_title(
            f"PARALELO - Día {day}"
        )

        return [
            image_seq,
            image_par
        ]

    animation = FuncAnimation(
        fig,
        animate,
        frames=min(
            len(sequential_frames),
            len(parallel_frames)
        ),
        interval=100,
        blit=True
    )

    output = os.path.join(
        os.path.dirname(__file__),
        "brote_side_by_side.gif"
    )

    animation.save(
        output,
        writer=PillowWriter(
            fps=10
        )
    )

    plt.close(fig)

    print(
        f"GIF side-by-side creado: {output}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    sequential_frames, parallel_frames = (
        generate_simulations()
    )

    save_gif(
        sequential_frames,
        "brote_secuencial.gif",
        "Modelo SIR 2-D - SECUENCIAL"
    )

    save_gif(
        parallel_frames,
        "brote_paralelo.gif",
        "Modelo SIR 2-D - PARALELO"
    )

    save_side_by_side(
        sequential_frames,
        parallel_frames
    )

    print()
    print("=" * 65)
    print("PROCESO COMPLETADO")
    print("=" * 65)
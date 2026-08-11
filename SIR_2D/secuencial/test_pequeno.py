import sys
import os

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from sir_secuencial import (
    create_population,
    update_day,
    calculate_statistics,
    SUSCEPTIBLE,
    INFECTED,
    RECOVERED,
    DEAD
)

import numpy as np


def test_population():

    grid = create_population(
        size=10,
        initial_infected=5,
        seed=42
    )

    total_people = grid.size

    assert total_people == 100

    infected = np.count_nonzero(
        grid == INFECTED
    )

    assert infected == 5

    print("✓ Prueba de población: OK")


def test_update():

    grid = create_population(
        size=10,
        initial_infected=5,
        seed=42
    )

    rng = np.random.default_rng(43)

    new_grid = update_day(
        grid,
        rng
    )

    assert new_grid.shape == grid.shape

    assert np.all(
        np.isin(
            new_grid,
            [
                SUSCEPTIBLE,
                INFECTED,
                RECOVERED,
                DEAD
            ]
        )
    )

    print("✓ Prueba de actualización: OK")


def test_statistics():

    grid = np.array([
        [0, 0, 1],
        [1, 2, 2],
        [3, 0, 1]
    ], dtype=np.uint8)

    s, i, r, d = calculate_statistics(grid)

    assert s == 3
    assert i == 3
    assert r == 2
    assert d == 1

    print("✓ Prueba de estadísticas: OK")


if __name__ == "__main__":

    print("=" * 50)
    print("VALIDACIÓN DEL MODELO SECUENCIAL")
    print("=" * 50)

    test_population()
    test_update()
    test_statistics()

    print()
    print("TODAS LAS PRUEBAS PASARON CORRECTAMENTE.")
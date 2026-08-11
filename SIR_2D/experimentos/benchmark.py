import sys
import os
import csv
import time
import multiprocessing as mp

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "paralelo"
    )
)

from sir_paralelo import simulate


def run_benchmark():

    processes_list = [
        1,
        2,
        4,
        8
    ]

    results = []

    print("=" * 60)
    print("EXPERIMENTO DE STRONG SCALING")
    print("=" * 60)

    for processes in processes_list:

        print()
        print(
            f"Ejecutando con "
            f"{processes} procesos..."
        )

        _, _, total_time = simulate(
            size=1000,
            days=365,
            processes=processes,
            seed=42
        )

        results.append([
            processes,
            total_time
        ])

        print(
            f"Tiempo: "
            f"{total_time:.4f} segundos"
        )

    t1 = results[0][1]

    final_results = []

    for processes, time_value in results:

        speedup = (
            t1 / time_value
        )

        efficiency = (
            speedup / processes
        ) * 100

        final_results.append([
            processes,
            time_value,
            speedup,
            efficiency
        ])

    output = os.path.join(
        os.path.dirname(__file__),
        "tiempos.csv"
    )

    with open(
        output,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Procesos",
            "Tiempo",
            "Speedup",
            "Eficiencia"
        ])

        writer.writerows(
            final_results
        )

    print()
    print("=" * 60)
    print("RESULTADOS")
    print("=" * 60)

    print(
        "Procesos | Tiempo | Speedup | Eficiencia"
    )

    for row in final_results:

        print(
            f"{row[0]:8} | "
            f"{row[1]:.4f} | "
            f"{row[2]:.2f} | "
            f"{row[3]:.2f}%"
        )

    print()
    print(
        f"CSV guardado en: {output}"
    )


if __name__ == "__main__":

    mp.freeze_support()

    run_benchmark()
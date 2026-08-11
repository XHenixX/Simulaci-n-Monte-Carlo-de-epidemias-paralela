import pandas as pd
import matplotlib.pyplot as plt
import os


base = os.path.dirname(
    os.path.abspath(__file__)
)

csv_file = os.path.join(
    base,
    "tiempos.csv"
)

df = pd.read_csv(csv_file)

plt.figure(
    figsize=(8, 5)
)

plt.plot(
    df["Procesos"],
    df["Speedup"],
    marker="o",
    label="Speed-up real"
)

plt.plot(
    df["Procesos"],
    df["Procesos"],
    marker="o",
    linestyle="--",
    label="Speed-up ideal"
)

plt.xlabel("Número de procesos")
plt.ylabel("Speed-up")

plt.title(
    "Strong Scaling - Modelo SIR 2-D"
)

plt.xticks(
    [1, 2, 4, 8]
)

plt.grid(True)

plt.legend()

plt.tight_layout()

output = os.path.join(
    base,
    "speedup.png"
)

plt.savefig(
    output,
    dpi=300
)

plt.show()

print(
    f"Gráfica guardada en: {output}"
)
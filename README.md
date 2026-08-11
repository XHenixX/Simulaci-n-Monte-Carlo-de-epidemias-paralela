# Modelo SIR 2-D Paralelo

## Descripción

Este proyecto implementa un modelo epidemiológico SIR en una grilla bidimensional de personas. Cada celda representa una persona que puede encontrarse en uno de cuatro estados: susceptible, infectado, recuperado o muerto.

La simulación permite estudiar la propagación de una enfermedad durante 365 días y comparar una implementación secuencial con una implementación paralela.

## Estados

* 0: Susceptible
* 1: Infectado
* 2: Recuperado
* 3: Muerto

## Parámetros

* Tamaño de la grilla: 1000 × 1000
* Población: 1,000,000 personas
* Duración: 365 días
* β = 0.20
* γ = 0.05
* μ = 0.01
* Infectados iniciales: 1,000

## Modelo

Cada persona susceptible puede contagiarse dependiendo de la cantidad de vecinos infectados.

La probabilidad de contagio utilizada es:

P(contagio) = 1 - (1 - β)^k

donde β representa la probabilidad de contagio por vecino infectado y k representa el número de vecinos infectados.

Las personas infectadas pueden recuperarse con probabilidad γ o morir con probabilidad μ.

## Implementación secuencial

La versión secuencial procesa toda la grilla en cada día de simulación.

Se utiliza una matriz actual y una matriz nueva para evitar modificar los estados mientras se realiza el cálculo del mismo día.

## Implementación paralela

La versión paralela divide la grilla en bloques horizontales. Cada proceso recibe un bloque de la población y dos filas adicionales llamadas ghost cells.

Las ghost cells permiten que cada proceso tenga acceso a los vecinos ubicados en los límites de los bloques.

Después de procesar cada bloque, los resultados son reunidos para formar nuevamente la grilla completa.

## Strong Scaling

Se realizan experimentos utilizando:

* 1 proceso
* 2 procesos
* 4 procesos
* 8 procesos

El speed-up se calcula mediante:

Speedup = T1 / Tp

donde T1 es el tiempo utilizando un proceso y Tp es el tiempo utilizando p procesos.

## Estructura

```text
SIR_2D/
├── secuencial/
├── paralelo/
├── experimentos/
├── animacion/
├── datos/
└── README.md
```

## Ejecución

Versión secuencial:

```bash
python secuencial/sir_secuencial.py
```

Versión paralela:

```bash
python paralelo/sir_paralelo.py
```

Benchmark:

```bash
python experimentos/benchmark.py
```

Gráfica:

```bash
python experimentos/grafica_speedup.py
```

Animación:

```bash
python animacion/generar_animacion.py
```

## Reproducibilidad

Se utiliza una semilla fija para generar la población inicial y permitir la repetición de los experimentos.

## Resultados

Los tiempos obtenidos y los valores de speed-up se almacenan en `experimentos/tiempos.csv`.

La gráfica correspondiente se encuentra en `experimentos/speedup.png`.

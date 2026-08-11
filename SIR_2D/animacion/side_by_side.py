from PIL import Image, ImageDraw
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ANIMACION_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SECUENCIAL = os.path.join(
    ANIMACION_DIR,
    "secuencial.gif"
)

PARALELO = os.path.join(
    ANIMACION_DIR,
    "paralelo.gif"
)

SALIDA = os.path.join(
    ANIMACION_DIR,
    "comparacion_secuencial_paralelo.gif"
)


# ============================================================
# CARGAR GIF
# ============================================================

gif_seq = Image.open(
    SECUENCIAL
)

gif_par = Image.open(
    PARALELO
)


# ============================================================
# NÚMERO DE FRAMES
# ============================================================

frames_seq = getattr(
    gif_seq,
    "n_frames",
    1
)

frames_par = getattr(
    gif_par,
    "n_frames",
    1
)

frames = min(
    frames_seq,
    frames_par
)


# ============================================================
# CREAR FRAMES
# ============================================================

resultado = []

for i in range(frames):

    gif_seq.seek(i)
    gif_par.seek(i)

    izquierda = gif_seq.convert(
        "RGB"
    )

    derecha = gif_par.convert(
        "RGB"
    )

    # Mantener mismo tamaño

    ancho = max(
        izquierda.width,
        derecha.width
    )

    alto = max(
        izquierda.height,
        derecha.height
    )

    izquierda = izquierda.resize(
        (ancho, alto)
    )

    derecha = derecha.resize(
        (ancho, alto)
    )

    # Crear imagen combinada

    canvas = Image.new(
        "RGB",
        (
            ancho * 2,
            alto + 50
        ),
        "white"
    )

    canvas.paste(
        izquierda,
        (0, 50)
    )

    canvas.paste(
        derecha,
        (ancho, 50)
    )

    # Texto

    draw = ImageDraw.Draw(
        canvas
    )

    draw.text(
        (ancho // 2 - 50, 15),
        "SECUENCIAL",
        fill="black"
    )

    draw.text(
        (ancho + ancho // 2 - 40, 15),
        "PARALELO",
        fill="black"
    )

    resultado.append(
        canvas
    )


# ============================================================
# GUARDAR
# ============================================================

if resultado:

    resultado[0].save(
        SALIDA,
        save_all=True,
        append_images=resultado[1:],
        duration=100,
        loop=0
    )

    print()
    print("=" * 60)
    print("ANIMACIÓN SIDE-BY-SIDE GENERADA")
    print("=" * 60)

    print()
    print(SALIDA)

else:

    print(
        "No se pudieron generar frames."
    )
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

VECTOR_STEP = 1  
MAP_COLOR = "viridis" 
ARROWS_COLOR = "white"
IMAGE_SAVE_NAME = "result.png"


def read_flo_file(flo_file):
    """Lee un archivo .flo"""
    with open(flo_file, "rb") as f:
        magic = np.fromfile(f, np.float32, count=1)
        if magic.size == 0 or magic[0] != 202021.25:
            raise ValueError(".flo file not valid or incorrect magic number.")
        w, h = np.fromfile(f, np.int32, count=2)
        data = np.fromfile(f, np.float32, count=2 * w * h)
        flow = data.reshape((h, w, 2))
    return flow


def graph_flo_file(flow, flo_file):
    """Visualiza contornos de magnitud y vectores quiver.
    Se debió haber ejecutado la función ####read_flo_file#### antes"""
    h, w = flow.shape[:2]
    x, y = np.meshgrid(np.arange(0, w), np.arange(0, h))
    u = flow[:, :, 0]
    v = flow[:, :, 1]
    mag = np.sqrt(u**2 + v**2)
    fig, ax = plt.subplots(figsize=(12, 9))
    # Capa 1: Contornos de magnitud
    cf = ax.contourf(x, y, mag, levels=20, cmap=MAP_COLOR)
    fig.colorbar(cf, ax=ax, label="Velocity magnitude")
    # Capa 2: Vectores
    skip = (
        slice(None, None, VECTOR_STEP),
        slice(None, None, VECTOR_STEP),
    )
    ax.quiver(
        x[skip],
        y[skip],
        u[skip],
        -v[skip],
        color=ARROWS_COLOR,
        pivot="mid",
        scale_units="xy",
        alpha=0.8,
    )
    ax.set_aspect("equal")
    ax.invert_yaxis() 
    ax.set_title(f"Flow visualization: {flo_file}")
    ax.set_xlabel("X [pixels]")
    ax.set_ylabel("Y [pixels]")

    plt.show()


def export_to_csv(flo_file, step=VECTOR_STEP, f_save_name="reduced_flow.csv"):
    """
    Exporta a CSV solo los puntos que se ven en la gráfica según el 'step'
    """

    flow = read_flo_file(flo_file)

    reduced_flow = flow[::step, ::step, :]
    h, w = reduced_flow.shape[:2]

    #Crear coordenadas X e Y correspondientes a esos saltos
    x, y = np.meshgrid(
        np.arange(0, flow.shape[1], step), 
        np.arange(0, flow.shape[0], step)
    )

    #Extraer U y V del flujo ya recortado
    u = reduced_flow[:, :, 0]
    v  = reduced_flow[:, :, 1]

    #Aplanar y apilar
    datos = np.column_stack((x.flatten(), y.flatten(), u.flatten(), v.flatten()))

    header = "x,y,u,v"

    #Formato que la interfaz puede interpretar
    np.savetxt(
        f_save_name,
        datos,
        delimiter=",",
        comments="",
        fmt=["%d", "%d", "%.4f", "%.4f"],
    )
#    print(f"Exportación proporcional completada.")
#    print(f"Puntos exportados: {datos.shape[0]} (usando paso de {paso})")

    return f_save_name

def validate_csv(csv_name="reduced_flow.csv"):
    """
        Función sin uso en la interfaz, se usó para verificar que el archivo csv coincidiera con su archivo csv generado
    """
    try:
        #Cargar CSV
        df = pd.read_csv(csv_name)

        x = df[0]
        y = df[1]
        u = df[2]
        v = df[3]

        plt.figure(figsize=(12, 12))

        q = plt.quiver(x, y, u, -v, color="blue", units="xy", scale=1, alpha=0.8)

        plt.gca().set_aspect("equal")
        plt.gca().invert_yaxis()
        plt.title(f"Data validation: Vectors file {csv_name}")
        plt.xlabel("X [pixels]")
        plt.ylabel("Y [pixels]")
        plt.grid(True, linestyle="--", alpha=0.5)
        #print(f"Graficando {len(df)} vectores desde el CSV...")
        plt.show()
    except FileNotFoundError:
        print(f"Error: File {csv_name} not found")
    except Exception as e:
        print(f"An error has ocurred: {e}")

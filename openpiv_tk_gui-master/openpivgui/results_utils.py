import pandas as pd
import numpy as np
import openpivgui.flo_utils as flo_utils
#import flo_utils
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

def map_refCSV_to_vec_grid(csv_file:str, vec_file:str, gridded_csv_name:str) -> str:
    """Mallar el archivo con el comportamiento original del flujo al del generado
        por el método en curso

    Args:
        csv_file (_type_): Archivo CSV del comportamiento original del flujo
        vec_file (_type_): Archivo VEC del comportamiento del flujo una vez analizado por el método X
        gridded_csv_name (str): Archivo generado, resultado de mallar csv_file hacia vec_file.

    Returns:
        str: nombre del archivo csv generado, gridded_csv_name.
    """

    # Leer archivos
    csv_data = pd.read_csv(csv_file, header=None, names=['x','y','u','v'])
    vec_data = pd.read_csv(vec_file, sep=r'\s+', header=None,
                           names=['x','y','u','v','mask','sig2noise'])
    
    #Mallar CSV al estilo de VEC
    gridded_csv = pd.merge(csv_data, vec_data[['x','y']], on=['x', 'y'], how='inner')

    # Guardar  archivo
    gridded_csv.to_csv(gridded_csv_name, index=False)
    
    return gridded_csv_name

#def interpolate_vec_to_ref(csv_file, vec_file, interpolated_vec_name:str):

    csv = pd.read_csv(csv_file, header=None)
    csv.columns = ["x", "y", "u", "v"]

    x_ref = csv["x"].values
    y_ref = csv["y"].values

    x_unique = np.unique(x_ref)
    y_unique = np.unique(y_ref)

    X_ref, Y_ref = np.meshgrid(x_unique, y_unique)

    vec = pd.read_csv(vec_file, header=None, sep=r"\s+")
    vec.columns = ["x", "y", "u", "v", "mask", "sig2noise"]

    x = vec["x"].values
    y = vec["y"].values
    u = vec["u"].values
    v = vec["v"].values
    mask = vec["mask"].values
 
    valid = mask == 0

    points = np.column_stack((x[valid], y[valid]))

    # Matriz A → U
    U_grid = griddata(points, u[valid], (X_ref, Y_ref), method="cubic")

    # Matriz B → V
    V_grid = griddata(points, v[valid], (X_ref, Y_ref), method="cubic")

    U_near = griddata(points, u[valid], (X_ref, Y_ref), method="nearest")
    V_near = griddata(points, v[valid], (X_ref, Y_ref), method="nearest")

    U_grid = np.where(np.isnan(U_grid), U_near, U_grid)
    V_grid = np.where(np.isnan(V_grid), V_near, V_grid)

    result = pd.DataFrame(
        {
            "x": X_ref.flatten(),
            "y": Y_ref.flatten(),
            "u": U_grid.flatten(),
            "v": V_grid.flatten(),
        }
    )

    np.savetxt(
    interpolated_vec_name,
    result.values,
    fmt=["%d", "%d", "%.4f", "%.4f"],
    delimiter=" "
    )

    #print(resultado)

#    print("-----ARCHIVO VEC INTERPOLADO-----")

    return interpolated_vec_name

def read_vec(vec_file):
    with open(vec_file, "r") as f:
        lines = f.readlines()

    data_lines = [line for line in lines if not line.startswith("#")]

    data = [list(map(float, line.split())) for line in data_lines]

    n_cols = len(data[0])

    #Archivo vec interpolado
    if n_cols == 4:
        df = pd.DataFrame(data, columns=["x", "y", "u", "v"])
    #Archivo vec sin interpolar (original)
    elif n_cols == 6:
        df = pd.DataFrame(data, columns=["x", "y", "u", "v", "mask", "sig2noise"])
    else:
        raise ValueError(f"Incorrect format: {n_cols} columns")

#    print("-----ARCHIVO VEC LEIDO-----")

    return df

def calculate_E(reference_CSV_file:str, 
                vec_file:str,
                flo_fname: str) -> float:
    # Detectar si es un CSV gridded
    if reference_CSV_file.endswith("gridded.csv"):
        # CSV gridded → tiene header
        ref = pd.read_csv(reference_CSV_file)
    else:
        # CSV normal → sin header
        ref = pd.read_csv(reference_CSV_file, header=None)
        ref.columns = ["x", "y", "u", "v"]

    # Forzar a float para evitar problemas con NumPy
    ref = ref.astype(float)

    # Leer .vec
    vec_file = read_vec(vec_file)
    vec_file[['x','y','u','v']] = vec_file[['x','y','u','v']].astype(float)

    # Verificar que x,y coincidan
    if not (np.allclose(ref["x"], vec_file["x"]) and
            np.allclose(ref["y"], vec_file["y"])):
        raise ValueError("Interpolate .flo file first: (x,y) points don't match")

    # Vectores
    u_reference = ref["u"].values
    v_reference = ref["v"].values
    u_algorithm = vec_file["u"].values
    v_algorithm = vec_file["v"].values

    # Producto punto y magnitudes
    dot = u_reference * u_algorithm + v_reference * v_algorithm
    mag_ref = np.sqrt(u_reference**2 + v_reference**2)
    mag_alg = np.sqrt(u_algorithm**2 + v_algorithm**2)

    # Coseno del ángulo evitando división por cero
    valid = (mag_ref > 0) & (mag_alg > 0)
    cos_alpha = np.zeros_like(dot)
    cos_alpha[valid] = dot[valid] / (mag_ref[valid] * mag_alg[valid])

    E_all = cos_alpha[valid]

    if "turbulence" in flo_fname:
        #filter_lesser_0_8 =  E_all < 0.8
        #E_filtered = E_all[filter_lesser_0_8]
        filter_greaterEQ_0_6 = E_all >= 0.6
        E_filtered = E_all[filter_greaterEQ_0_6]

    else:
        #filter_lesser_0_5 =  E_all < 0.5
        #E_filtered = E_all[filter_lesser_0_5]
        filter_greaterEQ_0_9 = E_all >= 0.9
        E_filtered = E_all[filter_greaterEQ_0_9]

    #print("----------", flo_fname, "----------")

    E = np.mean(cos_alpha[valid])

    return E_filtered, E

def calculate_E_KLT(reference_CSV_file: str, 
                    vec_file: str, 
                    features_tracked: int,
                    flo_fname: str) -> float:
    
    #Leer CSV del mapa vectorial original
    column_names = ['x', 'y', 'u', 'v']
    csv_df = pd.read_csv(reference_CSV_file, sep=',', header=None, names=column_names)

    #Leer VEC del mapa vectorial KLT
    column_names = ['x', 'y', 'u', 'v', 'mask', 'sig2noise']
    vec_df = pd.read_csv(vec_file, sep='\t', header=None, names=column_names)

    dot = 0

    #print(csv_df)

    #print(vec_df[['x','y']].head(10))

    #Tener solo los píxeles de KLT en el flujo real/original
    csv_vec_values = pd.merge(csv_df, vec_df, on=['x', 'y'], suffixes=('_ref', '_alg'))

    # Vectores
    u_reference = csv_vec_values["u_ref"].values
    v_reference = csv_vec_values["v_ref"].values
    u_algorithm = csv_vec_values["u_alg"].values
    v_algorithm = csv_vec_values["v_alg"].values

    # Producto punto y magnitudes
    dot = u_reference * u_algorithm + v_reference * v_algorithm
    mag_ref = np.sqrt(u_reference**2 + v_reference**2)
    mag_alg = np.sqrt(u_algorithm**2 + v_algorithm**2)

    # Coseno del ángulo evitando división por cero
    valid = (mag_ref > 0) & (mag_alg > 0)
    cos_alpha = np.zeros_like(dot)
    cos_alpha[valid] = dot[valid] / (mag_ref[valid] * mag_alg[valid])

    #print("features_tracked:", features_tracked)
    #print("len merged:", len(csv_vec_values))
    #print("valid count:", np.sum(valid))
    #print("sum cos_alpha[valid]:", np.sum(cos_alpha[valid]))

    E_all = cos_alpha[valid]

    if "turbulence" in flo_fname:
        #filter_lesser_0_8 =  E_all < 0.8
        #E_filtered = E_all[filter_lesser_0_8]
        filter_greaterEQ_0_5 = E_all >= 0.6
        E_filtered = E_all[filter_greaterEQ_0_5]

    else:
        #filter_lesser_0_5 =  E_all < 0.5
        #E_filtered = E_all[filter_lesser_0_5]
        filter_greaterEQ_0_9 = E_all >= 0.9
        E_filtered = E_all[filter_greaterEQ_0_9]


    #print("----------", flo_fname, "----------")

    #print("Less than 0.8:", len(E_filtered))

    

    #print("Greater (or equal) than 0.8:", len(E_filtered))

    #print("------------------------------")

    E =  np.sum(cos_alpha[valid]) / features_tracked
    
    return E_filtered, E

#reference_CSV = '1_flujo_reducido.csv'
#vec_file = '0_KLT_openpiv.vec'
#n_features_tracked = 1681
#_, E = calculate_E_KLT(reference_CSV, vec_file, n_features_tracked)
#
#print("E=", E)

#flo_file = "resultados/backstep_Re1500_00996_flow.flo"
##flo_flow= flo_utils.read_flo_file(flo_file)
#flo_to_CSV = flo_utils.export_to_csv(flo_file)
#
#vec_file = "0_KLT_openpiv.vec"
#
#ipl_vec_file = interpolate_vec(flo_to_CSV, vec_file)
#
#print(ipl_vec_file)
#
#E = calculate_E(flo_to_CSV, ipl_vec_file)
#print(f'E = {E} END OF THE PROJECT :)')
#
##flo_utils.graph_flo_file(flo_flow, flo_file)


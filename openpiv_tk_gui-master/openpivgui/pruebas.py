import pandas as pd

# Leer CSV y vec
csv_data = pd.read_csv('0_flujo_reducido.csv', header=None, names=['x','y','u','v'])
vec_data = pd.read_csv('0_OpenPIV_openpiv.vec', delim_whitespace=True, header=None,
                       names=['x','y','u','v','a','b'])

# Obtener los valores únicos de x e y en el vec
vec_x = vec_data['x'].unique()
vec_y = vec_data['y'].unique()

# Filtrar CSV para que solo tome los x e y del vec
filtered_csv = csv_data[csv_data['x'].isin(vec_x) & csv_data['y'].isin(vec_y)]

# Guardar CSV remuestreado
filtered_csv.to_csv('csv_remuestreado.csv', index=False)

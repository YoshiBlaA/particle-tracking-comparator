#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parallel Processing of PIV images."""

import openpivgui.flo_utils as flo_utils
import openpivgui.results_utils as results_utils
#import openpivgui.vec_utils as vec_utils

from openpivgui.PreProcessing import gen_background, process_images
from openpivgui.open_piv_gui_tools import create_save_vec_fname, _round
import numpy as np
import time
import openpiv.smoothn as piv_smt
import openpiv.scaling as piv_scl
import openpiv.filters as piv_flt
import openpiv.validation as piv_vld
import openpiv.windef as piv_wdf
import openpiv.tools as piv_tls
import subprocess

from pathlib import Path
import os
import pandas as pd
import re
import math

import matplotlib.pyplot as plt
from scipy.interpolate import griddata

__licence__ = '''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__email__ = 'vennemann@fh-muenster.de'


class MultiProcessing(piv_tls.Multiprocesser):
    """
        Parallel processing, based on the corrresponding OpenPIV class.

        Do not run from the interactive shell or within IDLE! Details at:
        https://docs.python.org/3.6/library/multiprocessing.html#using-a-pool-of-workers

        Parameters
        ----------
        params : OpenPivParams
            A parameter object.
    """

    def __init__(self, gui, processing_type):
        """
            Standard initialization method.

            For separating GUI and PIV code, the output filenames are
            generated here and not in OpenPivGui. In this way, this object
            might also be useful independently from OpenPivGui.
        """
        self.p = gui.p
        self.GUI = gui
        
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================

        self.processing_type = processing_type
        self.E_fname = gui.E_fname
        
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================

        # generate background if needed
        if self.p['background_subtract']\
                and self.p['background_type'] != 'minA - minB':
            self.background = gen_background(self.p)
        else:
            self.background = None

        # custom image sequence with (1+[1+x]), (2+[2+x]) and ((1+[1+x]),
        # (3+[3+x]))
        if self.p['sequence'] == '(1+2),(2+3)':
            step = 1
        else:
            step = 2
        self.files_a = self.p['fnames'][0::step]
        self.files_b = self.p['fnames'][self.p['skip']::step]

        # making sure files_a is the same length as files_b
        diff = len(self.files_a) - len(self.files_b)
        if diff != 0:
            for i in range(diff):
                self.files_a.pop(len(self.files_b))
                
        self.flo_files = gui.flo_files
        self.counter_flo = 0

        #print("-----------------------------------------------------------------")
        #print("-----------------------------------------------------------------")
        #print("-----------------------------------------------------------------")
        #print('MULTIPROCESSING Number of a files: ' + str(len(self.files_a)))
        #print(self.files_a)
        #print("-----------------------------------------------------------------")
        #print('MULTIPROCESSING Number of b files: ' + str(len(self.files_b)))
        #print(self.files_b)
        #print("-----------------------------------------------------------------")
        #print(self.flo_files)
        #print("-----------------------------------------------------------------")
        #print("-----------------------------------------------------------------")
        #print("-----------------------------------------------------------------")

        if self.p['swap_files']:
            self.files_a, self.files_b = self.files_b, self.files_a

        self.n_files = len(self.files_a)
        self.save_fnames = []

        self.file_list = []

        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        #======================================================CONTRIBUCIÓN==============================================================
        
        if self.processing_type == 'Pivelocimetry':
            evaluation_method = "Pivelocimetry"

        elif self.processing_type == 'AdaptivePIV':
            evaluation_method = "AdaptivePIV"
            
        elif self.processing_type == 'KLT':
            evaluation_method = "KLT"

        else:
            evaluation_method = 'OpenPIV'

        
        self.results_dict = {evaluation_method : []}
            
#        postfix = '_piv_' + evaluation_method + '_'
        #self.delete_flist(processing_type=evaluation_method)
        """file_list = []
            counter = 0

            while counter <  self.n_files:
                file_name =(f'{counter}_{evaluation_method}_openpiv')

                if not os.path.isfile(f'{file_name}.vec'):
                ##Termina en el momento en que no encuentra un archivo
                    break

                file_list.append(file_name)
                counter += 1

            for file in file_list:
                self.save_fnames.append(
                    create_save_vec_fname(postfix=f'/{file}'))"""
                                      
#        else:
#
#            for n in range(self.n_files):
#                self.save_fnames.append(
#                    create_save_vec_fname(path=self.files_a[n],
#                                        basename=self.p['vec_fname'],
#                                        postfix=postfix,
#                                        count=n,
#                                        max_count=self.n_files))
#                
        
                
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================
        #======================================================FIN DE LA CONTRIBUCIÓN====================================================

        # setup widgets so the user could still use the GUI when processing
        self.parameter = {}
        for key in self.p.param:
            key_type = self.p.type[key]
            if key_type not in ['labelframe',
                                'sub_labelframe',
                                'h-spacer',
                                'sub_h-spacer',
                                'dummy']:
                if 1030 < self.p.index[key] < 4000:
                    self.parameter[key] = self.p[key]

    def get_results_dict(self):
        return self.results_dict

    def get_save_fnames(self):
        """
            Return a list of result filenames.

            Returns:
                str[]: List of filenames with resulting PIV data.
        """
        return self.save_fnames

    def get_num_frames(self) -> int:
        """
            Return the amount of image pairs that will be processed.

            Returns:
                int: The number of image pairs to be processed
        """
        return len(self.files_a)

    def process(self, args):
        """
            Process chain as configured in the GUI.

            Parameters
            ----------
            args : tuple
                Tuple as expected by the inherited run method:
                file_a (str) -- image file a
                file_b (str) -- image file b
                counter (int) -- index pointing to an element of the filename
                                 list
        """

        file_a, file_b, counter = args
        frame_a = piv_tls.imread(file_a)
        frame_b = piv_tls.imread(file_b)

        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================
        #======================================================CONTRIBUCIÓN==========================================================

        dim_a = frame_a.shape
        #dim_b = frame_b.shape

        def update_flist(processing_type = "OpenPIV"):

            file_name =(f'{counter}_{processing_type}_openpiv')

            #self.file_list.append(file_name)

            self.save_fnames.append(
                create_save_vec_fname(postfix=f'/{file_name}'))
            
            flo_file = self.flo_files[self.counter_flo]
            vec_file = create_save_vec_fname(postfix=f'/{file_name}')

            self.counter_flo += 1

            return flo_file, vec_file

        def update_E_dict(flo_file: str, vec_file: str, features_tracked:int = 0) -> tuple[np.ndarray, float]:
            """Actualizar el diccionario self.results_dict con los  resultados de E_filter

            Args:
                flo_file (str): nombre del archivo flo.
                vec_file (str): nombre del archivo vec generado por un método de procesamiento.
                features_tracked (int, optional): Partículas rastreadas correctamente, se usa solo para KLT. Por defecto es 0.

            Returns:
                tuple[np.ndarray, float]: 
                                            E_filtered (np.ndarray): arreglo 1D con los valores de la métrica E filtrados a partir de 0.8 en adelante para el método
                                                                     en ejecución.
                                            E_mean (float): E promedio del método en ejecución.
            """

            flo_to_CSV = flo_utils.export_to_csv(flo_file, f_save_name = f'{counter}_flujo_reducido.csv')

            if self.processing_type == "KLT":
                E_filtered, E_mean = results_utils.calculate_E_KLT(flo_to_CSV, vec_file, features_tracked, flo_file)
            else:
                #print("GRIDEANDO.....")
                gridded_csv_file = results_utils.map_refCSV_to_vec_grid(flo_to_CSV, vec_file, gridded_csv_name = f'{counter}_{self.processing_type}_ref_gridded.csv')
                #print("CALCULANDO E.....")
                E_filtered, E_mean = results_utils.calculate_E(gridded_csv_file, vec_file, flo_file)
                #print("TERMINA EL CÁLCULO PARA E....")

            n_files_result = (flo_file, vec_file)
            n_result = (n_files_result, E_filtered, E_mean)
            self.results_dict[self.processing_type].append(n_result)

            #print("E =", E)



            return E_filtered, E_mean

        if self.processing_type == "AdaptivePIV":
            exe_AdaptivePIV = "../AdaptivePIV_3.7/AdaptivePIV/dist/example/example"
            p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11 = \
                                                str(self.p['adaptive_piv_init_WS']), \
                                                str(self.p['adaptive_piv_final_WS']), \
                                                str(self.p['adaptive_piv_WOR']), \
                                                str(self.p['adaptive_piv_n_iter_main']), \
                                                str(self.p['adaptive_piv_n_iter_ref']), \
                                                str(self.p['adaptive_piv_vec_val']), \
                                                str(self.p['adaptive_piv_interp']), \
                                                str(dim_a), \
                                                file_a, \
                                                file_b, \
                                                str(counter)             
                
            result = subprocess.run(
                [exe_AdaptivePIV, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11],
                capture_output=True,
                text=True
            )

            print(result.stdout)
            print(result.stderr)

            if result.returncode != 0:
                with open('piv_failed.txt', 'w') as f:
                    f.write(f'AdaptivePIV failed on counter {counter}')
                return
            
            flo_file, vec_file = update_flist(processing_type="AdaptivePIV")

            update_E_dict(flo_file, vec_file)

            return                  
        
        elif self.processing_type == "Pivelocimetry":
                
            exe_Pivelocimetry = "../Pivelocimetry/build/piv"

            p1, p2, p3, p4, p5, p6, p7, p8, p9 , p10 = \
                                                str(self.p['pivelocimetry_n_peaks']), \
                                                str(self.p['pivelocimetry_overlap_x']), \
                                                str(self.p['pivelocimetry_overlap_y']), \
                                                str(self.p['pivelocimetry_IW_x']), \
                                                str(self.p['pivelocimetry_IW_y']), \
                                                str(self.p['pivelocimetry_PD_x']), \
                                                str(self.p['pivelocimetry_PD_y']), \
                                                file_a, \
                                                file_b, \
                                                str(counter)

            result = subprocess.run([exe_Pivelocimetry, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10],
                    capture_output=True, 
                    text=True
            )

            #print(result.stdout) 
            #print(result.stderr)

            if result.returncode != 0:
                with open('piv_failed.txt', 'w') as f:
                    f.write(f'Pivelocimetry failed on counter {counter}')
                return

            flo_file, vec_file = update_flist(processing_type="Pivelocimetry")
            update_E_dict(flo_file, vec_file)
            return
        
        elif self.processing_type == "KLT":

            exe_KLT = "../KLT/example1"

            print('Se tiene el nombre del ejecutable listo')
            p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26 , p27= \
                        str(self.p['klt_nFeatures']), \
                        file_b, \
                        file_a, \
                        str(self.p['klt_mindist']), \
                        str(self.p['klt_window_size']), \
                        str(int(self.p['klt_sequentialMode'])), \
                        str(int(self.p['klt_smoothBeforeSelecting'])), \
                        str(int(self.p['klt_writeInternalImages'])), \
                        str(int(self.p['klt_lighting_insensitive'])), \
                        str(self.p['klt_min_eigenvalue']), \
                        str(self.p['klt_min_determinant']), \
                        str(self.p['klt_max_iterations']), \
                        str(self.p['klt_min_displacement']), \
                        str(self.p['klt_max_residue']), \
                        str(self.p['klt_grad_sigma']), \
                        str(self.p['klt_smooth_sigma_fact']), \
                        str(self.p['klt_pyramid_sigma_fact']), \
                        str(self.p['klt_step_factor']), \
                        str(self.p['klt_nSkippedPixels']), \
                        str(self.p['klt_affineConsistencyCheck']), \
                        str(self.p['klt_affine_window_size']), \
                        str(self.p['klt_affine_max_iterations']), \
                        str(self.p['klt_affine_max_residue']), \
                        str(self.p['klt_affine_min_displacement']), \
                        str(self.p['klt_affine_max_displacement_differ']), \
                        str(self.p['klt_search_range']), \
                        str(counter)

            result = subprocess.run([exe_KLT, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15,
                            p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27],
                            capture_output=True, 
                            text=True
            )
            
            #Obtener el mensaje de salida de KLT (se encuentra en stderr)
            str_KLT = result.stderr

            lineas_split = str_KLT.splitlines()

            features_tracked = 0

            #Linea que imprime KLT donde se especifica el número de partículas rastreadas
            patron = r"(\d+) features successfully tracked\.$"

            #Iterar sobre las líneas de salida para buscar donde coincide el patrón
            for counter_linea, linea in enumerate(lineas_split):
                linea = linea.strip()
                coincidencia = re.search(patron, linea)

                #Guardar el número de partículas rastreadas en una variable si coincide con el patrón
                if coincidencia:
                    print("El número de partículas es =", coincidencia.group(1))
                    #Devuelve el número de (\d+) que son las partículas rastreadas
                    features_tracked = int(coincidencia.group(1))

            #Mensaje de error para informar en cuál par de imágenes falló (normalmente se debe a que los arhivos no son en formato PGM)
            if result.returncode != 0:
                with open('piv_failed.txt', 'w') as f:
                    f.write(f'KLT failed on counter {counter}')
                return

            #Si no hay error, crea los nombres para el archivo flo original y el vec del método, actualizando la lista de archivos
            #que se mostrarán en la interfaz usando sólo los vec de cada método, los flo se usarán después para el cálculo de la métrica de similitud
            flo_file, vec_file = update_flist(processing_type="KLT")

            import pandas as pd

            #Leer el archivo vec de KLT
            column_names = ['x', 'y', 'u', 'v', 'mask', 'sig2noise']
            df = pd.read_csv(vec_file, sep='\t', names=column_names)

            #Filtrar por vectores identificados correctamente.
            filter_condition = (df['x'] >= 0) & (df['mask'] == 0)
            filtered_df = df[filter_condition]

            #Ordenar datos de mayor a menor segun 'x' y despues 'y'
            sorted_df = filtered_df.sort_values(by=['x', 'y'])


            #Guardar el archivo
            sorted_df.to_csv(vec_file, header=False, index=False, sep='\t', columns=['x', 'y', 'u', 'v', 'mask', 'sig2noise'], float_format='%.4f')
            sorted_df.to_csv(f'{vec_file[:-4]}_copia.vec', header=False, index=False, sep='\t', columns=['x', 'y', 'u', 'v', 'mask', 'sig2noise'], float_format='%.4f')

            #Función que actualiza un diccionario E (medida de similitud) del estilo {'metodo de procesamiento' : [((archivo flo, archivo vec), E)]}
            #donde el arhicvo flo contiene el comportamiento real del flujo y el vec contiene el comportamiento del flujo determinado por el método
            # y la métrica E, resultado de comparar la similitud entre el vec y el flo.
            update_E_dict(flo_file, vec_file, features_tracked=features_tracked)

            x = sorted_df['x'].values
            y = sorted_df['y'].values
            u = sorted_df['u'].values
            v = sorted_df['v'].values

            if len(sorted_df) >= 4:
                n_puntos = max(int(np.sqrt(len(sorted_df))), 10)

                xi = np.linspace(x.min(), x.max(), n_puntos)
                yi = np.linspace(y.min(), y.max(), n_puntos)
                xi_grid, yi_grid = np.meshgrid(xi, yi)

                ui_grid = griddata((x, y), u, (xi_grid, yi_grid), method='linear')
                vi_grid = griddata((x, y), v, (xi_grid, yi_grid), method='linear')

                x_flat = xi_grid.flatten()
                y_flat = yi_grid.flatten()
                u_flat = np.nan_to_num(ui_grid.flatten())
                v_flat = np.nan_to_num(vi_grid.flatten())

                interp_df = pd.DataFrame({
                    'x': x_flat, 'y': y_flat,
                    'u': u_flat, 'v': v_flat,
                    'mask': 0.0, 'sig2noise': 0.0
                })

                interp_df.to_csv(vec_file, header=False, index=False, sep='\t',
                                 columns=['x', 'y', 'u', 'v', 'mask', 'sig2noise'],
                                 float_format='%.4f') 

            return
        
#            from scipy.interpolate import griddata
#
#            puntos_originales = sorted_df[['x', 'y']].values
#            valores_u = sorted_df['u'].values
#            valores_v = sorted_df['v'].values
#            valores_mask = sorted_df['mask'].values
#            valores_sig2noise = sorted_df['sig2noise'].values
#
#            sqrt_features_tracked = math.sqrt(features_tracked)
#            paso = 2**(int(math.log2(sqrt_features_tracked)))
#            print("Paso obtenido como", paso)
#
#            x_min = sorted_df['x'].min()
#            x_max = sorted_df['x'].max()
#            y_min = sorted_df['y'].min()
#            y_max = sorted_df['y'].max()
#
#            grid_x, grid_y = np.mgrid[x_min:x_max+1:paso, 
#                                      y_min:y_max+1:paso]
#            
#            res_u = griddata(puntos_originales, valores_u, (grid_x, grid_y), method='cubic')
#            res_v = griddata(puntos_originales, valores_v, (grid_x, grid_y), method='cubic')
#            res_mask  = griddata(puntos_originales, valores_mask, (grid_x, grid_y), method='nearest')
#            res_sig2noise = griddata(puntos_originales, valores_sig2noise, (grid_x, grid_y), method='nearest')
#
#            gridded_df = pd.DataFrame({
#                'x': grid_x.flatten(),
#                'y': grid_y.flatten(),
#                'u': res_u.flatten(),
#                'v': res_v.flatten(),
#                'mask': res_mask.flatten(),
#                'sig2noise': res_sig2noise.flatten()
#            }).fillna(0)
#            #Guardar el archivo en el mismo formato del .flo (x,y,u,v)
#            gridded_df.to_csv(vec_file, header=False, index=False, sep='\t', columns=['x', 'y', 'u', 'v', 'mask', 'sig2noise'], float_format='%.4f')
#
#            return

        # Smoothning script borrowed from openpiv.windef
        s = self.p['smoothn_val']

        def smoothn(u, s):
            s = s
            u, _, _, _ = piv_smt.smoothn(
                u, s=s, isrobust=self.p['robust'])
            return(u)

        # delimiters placed here for safety
        delimiter = self.p['separator']
        if delimiter == 'tab':
            delimiter = '\t'
        if delimiter == 'space':
            delimiter = ' '

        # preprocessing
        print('\nPre-pocessing image pair: {}'.format(counter + 1))
        if self.p['background_subtract'] \
                and self.p['background_type'] == 'minA - minB':
            self.background = gen_background(self.p, frame_a, frame_b)

        frame_a = frame_a.astype(np.int32)
        frame_a = process_images(self, frame_a, self.GUI.preprocessing_methods,
                                 background=self.background)
        frame_b = frame_b.astype(np.int32)
        frame_b = process_images(self, frame_b, self.GUI.preprocessing_methods,
                                 background=self.background)

        print('Evaluating image pair: {}'.format(counter + 1))

        # evaluation first pass
        start = time.time()
        passes = 1
        # setup custom windowing if selected
        if self.parameter['custom_windowing']:
            corr_window_0 = self.parameter['corr_window_1']
            overlap_0 = self.parameter['overlap_1']
            for i in range(2, 8):
                if self.parameter['pass_%1d' % i]:
                    passes += 1
                else:
                    break

        else:
            passes = self.parameter['coarse_factor']
            if self.parameter['grid_refinement'] == 'all passes' \
                    and self.parameter['coarse_factor'] != 1:
                corr_window_0 = self.parameter['corr_window'] * \
                    2**(self.parameter['coarse_factor'] - 1)
                overlap_0 = self.parameter['overlap'] * \
                    2**(self.parameter['coarse_factor'] - 1)

            # Refine all passes after first when there are more than 1 pass.
            elif self.parameter['grid_refinement'] == '2nd pass on' \
                    and self.parameter['coarse_factor'] != 1:
                corr_window_0 = self.parameter['corr_window'] * \
                    2**(self.parameter['coarse_factor'] - 2)
                overlap_0 = self.parameter['overlap'] * \
                    2**(self.parameter['coarse_factor'] - 2)

            # If >>none<< is selected or something goes wrong, the window
            # size would remain the same.
            else:
                corr_window_0 = self.parameter['corr_window']
                overlap_0 = self.parameter['overlap']
        overlap_percent = overlap_0 / corr_window_0
        sizeX = corr_window_0

        u, v, sig2noise = piv_wdf.extended_search_area_piv(
            frame_a.astype(np.int32),
            frame_b.astype(np.int32),
            window_size=corr_window_0,
            overlap=overlap_0,
            search_area_size=corr_window_0,
            width=self.parameter['s2n_mask'],
            subpixel_method=self.parameter['subpixel_method'],
            sig2noise_method=self.parameter['sig2noise_method'],
            correlation_method=self.parameter['corr_method'],
            normalized_correlation=self.parameter['normalize_correlation'])

        x, y = piv_wdf.get_rect_coordinates(frame_a.shape,
                                            corr_window_0,
                                            overlap_0)

        # validating first pass
        mask = np.zeros_like(x, dtype=bool)
        u = np.ma.copy(u)
        v = np.ma.copy(v)

        if self.parameter['fp_vld_global_threshold']:
            Mask = piv_vld.global_val(
                u, v,
                u_thresholds=(self.parameter['fp_MinU'],
                              self.parameter['fp_MaxU']),
                v_thresholds=(self.parameter['fp_MinV'],
                              self.parameter['fp_MaxV']))
            # consolidate effects of mask
            mask += Mask

        if self.parameter['fp_local_med']:
            Mask = piv_vld.local_median_val(
                u, v,
                u_threshold=self.parameter['fp_local_med'],
                v_threshold=self.parameter['fp_local_med'],
                size=self.parameter['fp_local_med_size'])
            mask += Mask

        if self.parameter['adv_repl']:
            u, v = piv_flt.replace_outliers(
                u, v, mask,
                method=self.parameter['adv_repl_method'],
                max_iter=self.parameter['adv_repl_iter'],
                kernel_size=self.parameter['adv_repl_kernel'])
        print('Validated first pass result of image pair: {}.'
              .format(counter + 1))

        # smoothning  before deformation if 'each pass' is selected
        if self.parameter['smoothn_each_pass']:
            if self.parameter['smoothn_first_more']:
                s *= 2
            u = smoothn(u, s)
            v = smoothn(v, s)
            print('Smoothned pass 1 for image pair: {}.'.format(counter + 1))
            s = self.parameter['smoothn_val1']

        print('Finished pass 1 for image pair: {}.'.format(counter + 1))
        print("window size: " + str(corr_window_0))
        print('overlap: ' + str(overlap_0), '\n')

        # evaluation of all other passes
        if passes != 1:
            iterations = passes - 1
            for i in range(2, passes + 1):
                # setting up the windowing of each pass
                if self.parameter['custom_windowing']:
                    corr_window = self.parameter['corr_window_%1d' % i]
                    overlap = int(corr_window * overlap_percent)

                else:
                    if self.parameter['grid_refinement'] == 'all passes' or \
                            self.parameter['grid_refinement'] == '2nd pass on':
                        corr_window = self.parameter['corr_window'] * \
                            2**(iterations - 1)
                        overlap = self.parameter['overlap'] * \
                            2**(iterations - 1)

                    else:
                        corr_window = self.parameter['corr_window']
                        overlap = self.parameter['overlap']
                sizeX = corr_window

                # translate settings to windef settings object
                piv_wdf_settings = piv_wdf.PIVSettings()
                piv_wdf_settings.correlation_method = \
                    self.parameter['corr_method']
                piv_wdf_settings.normalized_correlation = \
                    self.parameter['normalize_correlation']
                piv_wdf_settings.windowsizes = (corr_window,) * (passes + 1)
                piv_wdf_settings.overlap = (overlap,) * (passes + 1)
                piv_wdf_settings.num_iterations = passes
                piv_wdf_settings.subpixel_method = \
                    self.parameter['subpixel_method']
                piv_wdf_settings.deformation_method = \
                    self.parameter['deformation_method']
                piv_wdf_settings.interpolation_order = \
                    self.parameter['interpolation_order']
                piv_wdf_settings.sig2noise_validate = True,
                piv_wdf_settings.sig2noise_method = \
                    self.parameter['sig2noise_method']
                piv_wdf_settings.sig2noise_mask = self.parameter['s2n_mask']

                # do the correlation
                x, y, u, v, sig2noise, mask = piv_wdf.multipass_img_deform(
                    frame_a.astype(np.int32),
                    frame_b.astype(np.int32),
                    i,  # current iteration
                    x, y, u, v,
                    piv_wdf_settings)

                # validate other passes
                if self.parameter['sp_vld_global_threshold']:
                    Mask = piv_vld.global_val(
                        u, v,
                        u_thresholds=(self.parameter['sp_MinU'],
                                      self.parameter['sp_MaxU']),
                        v_thresholds=(self.parameter['sp_MinV'],
                                      self.parameter['sp_MaxV']))
                    mask += Mask  # consolidate effects of mask

                if self.parameter['sp_vld_global_threshold']:
                    Mask = piv_vld.global_std(
                        u, v,
                        std_threshold=self.parameter['sp_std_threshold'])
                    mask += Mask

                if self.parameter['sp_local_med_validation']:
                    Mask = piv_vld.local_median_val(
                        u, v,
                        u_threshold=self.parameter['sp_local_med'],
                        v_threshold=self.parameter['sp_local_med'],
                        size=self.parameter['sp_local_med_size'])
                    mask += Mask

                if self.parameter['adv_repl']:
                    u, v = piv_flt.replace_outliers(
                        u, v, mask,
                        method=self.parameter['adv_repl_method'],
                        max_iter=self.parameter['adv_repl_iter'],
                        kernel_size=self.parameter['adv_repl_kernel'])
                print('Validated pass {} of image pair: {}.'
                      .format(i, counter + 1))

                # smoothning each individual pass if 'each pass' is selected
                if self.parameter['smoothn_each_pass']:
                    u = smoothn(u, s)
                    v = smoothn(v, s)
                    print('Smoothned pass {} for image pair: {}.'
                          .format(i, counter + 1))

                print('Finished pass {} for image pair: {}.'
                      .format(i, counter + 1))
                print("window size: " + str(corr_window))
                print('overlap: ' + str(overlap), '\n')
                iterations -= 1

        if self.p['flip_u']:
            u = np.flipud(u)

        if self.p['flip_v']:
            v = np.flipud(v)

        if self.p['invert_u']:
            u *= -1

        if self.p['invert_v']:
            v *= -1

        # scaling
        u = u / self.parameter['dt']
        v = v / self.parameter['dt']
        x, y, u, v = piv_scl.uniform(x, y, u, v,
                                     scaling_factor=self.parameter['scale'])
        end = time.time()

        # =====================================================================
        flo_file, vec_file = update_flist(processing_type="OpenPIV") 

        # save data to file.
        out = np.vstack([m.ravel() for m in [x, y, u, -v, mask, sig2noise]])
        np.savetxt(self.save_fnames[counter], out.T, fmt='%8.4f',
                   delimiter=delimiter)
        
        update_E_dict(flo_file, vec_file)
        
        print('Processed image pair: {}'.format(counter + 1))
        # =====================================================================

        sizeY = sizeX
        sizeX = ((int(frame_a.shape[0] - sizeX)
                  // (sizeX - (sizeX * overlap_percent))) + 1)
        sizeY = ((int(frame_a.shape[1] - sizeY)
                  // (sizeY - (sizeY * overlap_percent))) + 1)

        time_per_vec = _round((((end - start) * 1000)
                               / ((sizeX * sizeY) - 1)), 3)

        print('Process time: {} second(s)'.format((_round((end - start), 3))))
        print('Number of vectors: {}'.format(int((sizeX * sizeY) - 1)))
        print('Time per vector: {} millisecond(s)'.format(time_per_vec))


#    def delete_flist(self, processing_type = "OpenPIV"):
#        counter = 0
#
#        while counter < self.n_files:
#            file_name = f'{counter}_{processing_type}_openpiv'
#            file_path = f'{file_name}.vec'
#
#            # Termina cuando no encuentra un archivo
#            if not os.path.isfile(file_path):
#                break
#
#            # Elimina el archivo
#            os.remove(file_path)
#
#            counter += 1

    def delete_flist(self, processing_type = "OpenPIV"):
        import glob
        for file_path in glob.glob("[0-9]*_*.vec"):
            os.remove(file_path)
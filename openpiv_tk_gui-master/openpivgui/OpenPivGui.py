#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple GUI for OpenPIV."""
import openpivgui.vec_plot as vec_plot

# from . import vec_plot
from openpivgui.open_piv_gui_tools import str2list, str2dict, get_dim, _round

# from .open_piv_gui_tools import str2list, str2dict, get_dim, _round

from openpivgui.ErrorChecker import (
    check_PIVprocessing,
    check_processing,
    check_postprocessing,
)

# from .ErrorChecker import check_PIVprocessing, check_processing, \
#    check_postprocessing

from openpivgui.PostProcessing import PostProcessing

# from . import PostProcessing

from openpivgui.PreProcessing import gen_background, process_images

# from .PreProcessing import gen_background, process_images

from openpivgui.MultiProcessing import MultiProcessing

# from . import MultiProcessing

from openpivgui.CreateToolTip import CreateToolTip

# from . import CreateToolTip

from openpivgui.OpenPivParams import OpenPivParams

# from . import OpenPivParams

import openpivgui.AddInHandler as AddInHandler

# from . import AddInHandler

from scipy.ndimage import gaussian_filter, gaussian_laplace
from matplotlib.figure import Figure as Fig
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import openpiv.tools as piv_tls
import pandas as pd
import numpy as np
from tkinter import colorchooser
from datetime import datetime
import threading
import shutil
import webbrowser
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter as tk
import inspect
import json
import sys
import re
import os

# ==================================================CONTRIBUCIÓN======================================================================
# ==================================================CONTRIBUCIÓN======================================================================
# ==================================================CONTRIBUCIÓN======================================================================
# ==================================================CONTRIBUCIÓN======================================================================
# ==================================================CONTRIBUCIÓN======================================================================
import shutil
from PIL import Image, ImageTk
from tkinter import ttk, Toplevel
from PIL import Image, ImageTk
from openpivgui.CropWindow import CropWindow
import ast
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import ast
import matplotlib.ticker as mtick
# ====================================================FIN DE LA CONTRIBUCIÓN========================================================
# ====================================================FIN DE LA CONTRIBUCIÓN========================================================
# ====================================================FIN DE LA CONTRIBUCIÓN========================================================
# ====================================================FIN DE LA CONTRIBUCIÓN========================================================
# ====================================================FIN DE LA CONTRIBUCIÓN========================================================

import multiprocessing
import logging

logger = multiprocessing.log_to_stderr()
logger.setLevel(multiprocessing.SUBDEBUG)

__version__ = "0.4.15"

__licence__ = """
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
"""

__email__ = "vennemann@fh-muenster.de"


class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.show = tk.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)

        self.toggle_button = ttk.Checkbutton(
            self.title_frame,
            width=2,
            text="+",
            command=self.toggle,
            variable=self.show,
            style="Toolbutton",
        )
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text="-")
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text="+")


class OpenPivGui(tk.Tk):
    """
    Simple OpenPIV GUI

    Usage:

    1. Press »File« and then »Import files« or »Import directory«.
       Either select some image pairs (Ctrl + Shift) or a directory
       that contains image files.

    2. Click on the links in the file-list on the right to inspect
       the images.

    3. Walk through the drop-down-menues »General«, »Preprocessing«,
       and »Analysis« and edit the parameters.

    4. Press the »start processing« butten (bottom left), to
       start the processing chain.

    5. Inspect the results by clicking on the links in the file-list.
       Use the »Plot« drop-down menu for changing the plot parameters.

    6. Use the »back« and »forward« buttons to go back to the images,
       in case you want to repeat the evaluation.

    7. For post-processing, use the »back« and »forward« buttons«
       to list the vector files. Modify the Post-Processing
       parameters and hit the »start post-processing« button.

    See also:

    https://github.com/OpenPIV/openpiv_tk_gui
    """

    buttons = {}
    preprocessing_methods = {}
    postprocessing_methods = {}
    plotting_methods = {}

    def __init__(self):
        """
        Standard initialization method.
        """
        print("Initializing GUI")
        self.VERSION = __version__
        self.TITLE = "Simple OpenPIV GUI"
        tk.Tk.__init__(self)
        # path of gui folder
        self.path = os.path.dirname(os.path.abspath(__file__))
        # path for image or icon
        self.icon_path = os.path.join(self.path, "res/icon.png")
        # convert .png into a usable icon photo
        self.iconphoto(False, tk.PhotoImage(file=self.icon_path))
        self.title(self.TITLE + " " + self.VERSION)
        # handle for user closing GUI through window manager
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        # the parameter object
        self.p = OpenPivParams()
        self.p.load_settings(self.p.params_fname)
        # background variable for widget data:
        self.tkvars = {}
        # handle for settings frames on riders
        self.set_frame = []
        # handle for text-area objects
        self.ta = {}
        # handle for list-box
        self.lb = None

        # ==================================================CONTRIBUCIÓN================================================================
        # ==================================================CONTRIBUCIÓN================================================================
        # ==================================================CONTRIBUCIÓN================================================================
        # ==================================================CONTRIBUCIÓN================================================================
        # ==================================================CONTRIBUCIÓN================================================================

        self.flo_files = []
        self.crop_box = None
        self.all_results_dict = {}
        self.E_fname = "E_results.txt"
        self.E_algorithm_dict = {}
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

        print("Initializing widgets")
        # Initializing the addin parameters and methods
        AddInHandler.init_add_ins(self)
        self.__init_widgets()
        self.set_settings()
        self.log(
            timestamp=True,
            text="--------------------------------"
            + "\nTkinter OpenPIV session started.",
        )
        self.log(text="OpenPivGui version: " + self.VERSION)
        print("Initialized GUI, ready for processing")

        #        tabs = self.nb.tabs()
        #        print("Número total de pestañas:", len(tabs))
        #        for idx, tab_id in enumerate(tabs):
        #            print(f"Pestaña {idx}: ID interno = {tab_id}")
        #            tab_widget = self.nametowidget(tab_id)
        #            print(f"  Widget asociado: {tab_widget}")
        #            tab_text = self.nb.tab(tab_id, option='text')
        #
        #            print(f"  Texto etiqueta: {tab_text}")

        #        unique_types = list({v[1] for v in self.p.default.values()})
        #        print(unique_types)

        self.mainloop()

    def validate_pairs(self, fnames):
        folder = os.path.dirname(fnames[0])
    
        flo_folder = os.path.join(folder, "flo")
    
        # Obtener prefijos de todos los .flo
        flo_prefix = {
            os.path.splitext(f)[0].rsplit("_", 1)[0]
            for f in os.listdir(flo_folder) if f.endswith(".flo")
        }
    
        pair_groups = defaultdict(list)
    
        for fname in fnames:
            f_name = os.path.basename(fname)
            f_name_no_extesion = os.path.splitext(f_name)[0]
            prefix = f_name_no_extesion.rsplit("_", 1)[0]
    
            pair_groups[prefix].append(fname)
    
        valid_pairs = []
        invalid_pairs = []
        flo_missing_flag = 0
    
        for prefix, imgs in pair_groups.items():
            if len(imgs) >= 2:
                imgs.sort()
                par = (imgs[0], imgs[1])
    
                if prefix in flo_prefix:
                    valid_pairs.append(par)
                else:
                    flo_missing_flag = 1
                    invalid_pairs.append(par)
    
        return (
            valid_pairs,
            invalid_pairs,
            flo_missing_flag,
        )


    def obtain_flo_pairs(self, valid_pair_files):

        if not valid_pair_files:
            return {}

        print("ACCEDIENDO A DIRECTORIO...")

        carpeta = os.path.dirname(valid_pair_files[0][0])
    
        flo_folder = os.path.join(carpeta, "flo")

        print("DIRECTORIO ACCEDIDO....")
        resultado = defaultdict(list)

        print("ENTRANDO A FOR....")
        for archivo in valid_pair_files:
            nombre = os.path.basename(archivo[0])
            prefijo = os.path.splitext(nombre)[0].rsplit("_", 1)[0]

            for f in os.listdir(flo_folder):
                if f.startswith(prefijo) and f.endswith(".flo"):
                    ruta_flo = os.path.join(flo_folder, f)
                    resultado[ruta_flo].append(archivo)
                    break

        #print("EL RESULTADO DICCIONARIO ES...", resultado)

#        for key, value in resultado.items():
#            key_clean = os.path.basename(key)
#            value_clean = [tuple(os.path.basename(x) for x in par) for par in value]
#
#            print(key_clean, ":", value_clean)
#            print("-------------------------------------------------")


        return dict(resultado)


#    def obtain_flo_pairs(self, valid_pairs):
#        from typing import Dict, Tuple
#        resultado: Dict[Tuple, str] = {}
#
#        if not valid_pairs:
#            return {}
#
#        carpeta = os.path.dirname(valid_pairs[0][0])
#        resultado = {tuple: str}
#
#        for img1, img2 in valid_pairs:
#            nombre = os.path.basename(img1)
#            prefijo = os.path.splitext(nombre)[0].rsplit("_", 1)[0]
#
#            for f in os.listdir(carpeta):
#                if f.startswith(prefijo) and f.endswith(".flo"):
#                    ruta_flo = os.path.join(carpeta, f)
#                    ######################################################
#                    ######################################################
#                    #resultado.setdefault((img1, img2), []).append(ruta_flo)
#                    resultado[(img1, img2)] = ruta_flo
#                    break
#
#        return resultado

    def start_processing(self, processing_type="OpenPIV"):

        def flo_error_window(root, mensaje):
            ventana = tk.Toplevel(root)
            ventana.title("Error Message")
            ventana.geometry("600x300")

            ventana.transient(root)
            ventana.grab_set()

            label = tk.Label(ventana, text=mensaje, wraplength=550, justify="left")
            label.pack(padx=20, pady=20)

            boton = tk.Button(ventana, text="OK", command=ventana.destroy)
            boton.pack(pady=10)

            ventana.focus_force()

        """Wrapper function to start processing in a separate thread."""
        try:

            fnames = self.tkvars["fnames"].get()
            fnames = ast.literal_eval(fnames)
            valid_pairs, invalid_pairs, flo_missing_flag = self.validate_pairs(fnames)
            # nombres_validos = [(os.path.basename(a), os.path.basename(b)) for a, b in valid_pairs]
            nombres_invalidos = [
                (os.path.basename(a), os.path.basename(b)) for a, b in invalid_pairs
            ]

            if flo_missing_flag:

                files = "\n".join(
                    [
                        f"{counter+1}. {par}"
                        for counter, par in enumerate(nombres_invalidos)
                    ]
                )

                message = (
                    "The following file pairs don't have a .flo file:\n\n"
                    f"{files}\n\n"
                    "Please provide one or remove pair from the analysis."
                )

                flo_error_window(self, message)

                raise Exception(message)

            else:
                # {(img_i, img_i+1) : flo_file}
                flo_dict = self.obtain_flo_pairs(valid_pairs)

                # print(flo_dict)
                # print(type(flo_dict))

                #Variable sin uso, contiene los archivos flo de cada par de imágenes
                self.flo_files = list(flo_dict.keys())

            self.get_settings()
            check_processing(self)  # simple error checking.
            check_PIVprocessing(self.p, processing_type)

            # ==================================================CONTRIBUCIÓN================================================================
            # ==================================================CONTRIBUCIÓN================================================================
            # ==================================================CONTRIBUCIÓN================================================================
            # ==================================================CONTRIBUCIÓN================================================================
            # ==================================================CONTRIBUCIÓN================================================================
            if processing_type == "ALL":
                # print("Método que compara")
                self.processing_thread = threading.Thread(target=self.processing_all)
            elif processing_type is not None:
                self.processing_thread = threading.Thread(
                    target=self.processing, args=([], processing_type)
                )
            else:
                self.processing_thread = threading.Thread(
                    target=self.processing, args=([],)
                )
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

            self.processing_thread.start()
        except Exception as e:
            print("PIV evaluation thread stopped. " + str(e))

    def processing_all(self):

        self.E_algorithm_dict.clear()

        os.system('cls' if os.name == 'nt' else 'clear')

        import glob
        for file_path in glob.glob("[0-9]*_*"):
            os.remove(file_path)

        self.all_results_dict.clear()
        

        def format_file_name(path: str, extension=".flo") -> str:

            f_name = os.path.basename(path)

            # Quitar la extensión
            if f_name.endswith(extension):
                f_name = f_name[: -len(extension)]

            return f_name

        results = {}
        self.algorithms = ("KLT", "Pivelocimetry", "AdaptivePIV", "OpenPIV")

        # Diccionario para guardar los archivos generados por cada algoritmo
        algorithm_files = {alg: [] for alg in self.algorithms}

        for algorithm in self.algorithms:
            print(f"#######-----Running {algorithm} ... -----######")

            temp_flist = []

            self.processing(
                flist=temp_flist, processing_type=algorithm, multiple_eval=True
            )

            print(f" {algorithm} finished")

            algorithm_files[algorithm] = list(temp_flist)

            if not temp_flist:
                del self.all_results_dict[algorithm]
                # results[algorithm] = 0.0
                print(f"{algorithm}: No files generated")

        all_files = []
        for fl in algorithm_files.values():
            all_files.extend(fl)

        self.tkvars["fnames"].set(all_files)
        self.p["fnames"] = list(all_files)
        self.num_label.config(text=len(all_files))

        print(f"All processing completed. Total files: {len(all_files)}")

        # Obtener un diccionario con el nombre del archivo como llave y los resultados de los metodos como su valor
        first_key = next(iter(self.all_results_dict))
        first_method_results = self.all_results_dict[
            first_key
        ]  # lista de ((flo, vec), E)

        self.xy_graph_dict = {
            format_file_name(flo_path): []
            for ((flo_path, vec_path), E_all, E_mean) in first_method_results
        }

        for key_all_results in self.all_results_dict:
            id = 0
            for key_xy_graph in self.xy_graph_dict:
                E = self.all_results_dict[key_all_results][id][1]
                self.xy_graph_dict[key_xy_graph].append(E)
                id += 1

        print("xy_graph keys:", self.xy_graph_dict.keys())

        self.E_algorithm_df = pd.DataFrame(self.E_algorithm_dict, index=list(self.xy_graph_dict.keys()))
        fname = f'all_algorithms_df.csv'
        self.E_algorithm_df.to_csv(fname, sep='\t', float_format='%.4f')

        # Mostrar ventana de comparación en base a la comparación del archivo .vec generado por cada algoritmo contra el archivo .flo original
        self.after(0, self.show_comparison_window_against_flo)

        return

    def parse_filename(self, name):
        n_match = re.search(r"n(\d+)", name)
        d_match = re.search(r"d(\d+)", name)

        n = int(n_match.group(1)) if n_match else None
        d = int(d_match.group(1)) if d_match else None

        tipo = re.split(r"_n\d+|_flow", name)[0]

        return tipo, n, d

    def show_comparison_window_against_flo(self):

        algorithms_length = len(self.algorithms)

        for index in range(len(self.xy_graph_dict)):
        #Obtener los datos de la primera llave
            n_key = list(self.xy_graph_dict.keys())[index]
            E_algs_metrics = self.xy_graph_dict[n_key]

            if "turbulence" in n_key:
                x_inf, x_sup = 0.6, 1.0
            else:
                x_inf, x_sup = 0.9, 1.0

            bins = np.linspace(x_inf, x_sup, 13)

            fig, axs = plt.subplots(2, 2, figsize=(16,9), tight_layout=True, sharey=True)

            fig.subplots_adjust(hspace=-0.1)

            axs_flat = axs.flatten()

            #Dibujar cada histograma
            for i in range(algorithms_length):
                n_key = list(self.xy_graph_dict.keys())[index]
                axs_flat[i].hist(E_algs_metrics[i], bins=bins, color='orange', edgecolor='black')
                axs_flat[i].set_title(f'{self.algorithms[i]} - {n_key[:-5]}', y=0.9, x=0.01, fontsize=15, loc='left')
                axs_flat[i].set_xlabel('E (similitud)', fontsize=15)
                if i%2 == 0:
                    axs_flat[i].set_ylabel('Frecuencia', fontsize=15)
                axs_flat[i].set_xlim(x_inf, x_sup)
                axs_flat[i].set_xticks(bins)
                axs_flat[i].xaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
                axs_flat[i].tick_params(axis='both', which='major', labelsize=14)

            fluid_type_formated = str(n_key).replace("/", "_").replace("\\", "_")
            save_path_name = os.path.join("graficas", f"comparacion_{fluid_type_formated}.png")
            
            plt.savefig(save_path_name, dpi=300, bbox_inches='tight')

            plt.show()
#    def show_comparison_window_against_flo(self):
#        files = list(self.xy_graph_dict.keys())          # archivo1, ..., archivoN
#        x = np.arange(len(files))                        # 0..N-1
#
#        methods = list(self.all_results_dict.keys())     # E1..En
#
#        fig, ax = plt.subplots()
#
#        colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))
#
#        all_E = []  # para calcular min y max global
#
#        for j, method in enumerate(methods):
#            y = [self.xy_graph_dict[file][j] for file in files]
#            all_E.extend(y)
#            ax.plot(x, y, marker="o", color=colors[j], label=method)
#
#        # etiquetas X
#        ax.set_xticks(x)
#        ax.set_xticklabels(files, rotation=45, ha="right")
#
#        # rango Y = [min, max] de todos los puntos, con pequeño margen
#        y_min = min(all_E)
#        y_max = max(all_E)
#        margin = (y_max - y_min) * 0.05 if y_max > y_min else 0.01
#        ax.set_ylim(y_min - margin, y_max + margin)
#
#        ax.set_xlabel("Archivo")
#        ax.set_ylabel("E")
#        ax.grid(True, alpha=0.3)
#
#        ax.legend(title="Método", loc="best")
#
#        plt.tight_layout()
#        plt.show()

    def show_comparison_window_invalid_vectors(self, results):
        if not results:
            return

        win = tk.Toplevel(self.master)
        win.title("ALL Algorithms - Invalid Vectors Comparison")
        win.geometry("700x500")
        win.resizable(True, True)

        tk.Label(
            win, text="Invalid Vectors Comparison", font=("Arial", 16, "bold")
        ).pack(pady=10)

        algorithms = list(results.keys())
        percentages = list(results.values())

        fig = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(
            algorithms, percentages, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        )

        for bar, perc in zip(bars, percentages):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{perc}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        ax.set_ylabel("Invalid Vectors (%)", fontsize=12)
        ax.set_title("Performance Comparison", fontsize=14)
        ax.set_ylim(0, max(percentages) * 1.15 if percentages else 10)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
        ax.grid(axis="y", alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

        button_frame = tk.Frame(win)
        button_frame.pack(pady=8)

        tk.Button(
            button_frame,
            text="Close",
            command=win.destroy,
            width=12,
            font=("Arial", 10),
        ).pack(side="left", padx=5)

        def save_figure():
            from tkinter import filedialog
            from datetime import datetime

            default_name = f"invalid_vectors_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            file_path = filedialog.asksaveasfilename(
                parent=win,
                title="Save graph as...",
                defaultextension=".png",
                initialfile=default_name,
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg *.jpeg")],
            )

            if file_path:
                try:
                    fig.savefig(file_path, dpi=300, bbox_inches="tight")
                    print(f"Graph saved in: {file_path}")

                    tk.messagebox.showinfo("Saves", f"Graph saved in:\n{file_path}")
                except Exception as e:
                    print(f"Graph saving error: {e}")
                    tk.messagebox.showerror("Error", f"Graph couldn't saved:\n{str(e)}")

        tk.Button(
            button_frame,
            text="Save",
            command=save_figure,
            width=15,
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
        ).pack(side="left", padx=5)

        print("Bar graph comparison window opened.")

    def get_invalid_percent(self, fnames):
        if not fnames:
            return 0.0

        if isinstance(fnames, str):
            fnames = [fnames]

        percentages = []

        for fname in fnames:
            try:
                data = self.load_pandas(fname)
                data = data.to_numpy().astype(float)

                try:
                    invalid = data[:, 4].astype(bool)
                except:
                    invalid = np.ones(len(data), dtype=bool)

                invalid_count = np.count_nonzero(invalid)
                percent = _round((invalid_count / len(data)) * 100, 4)
                percentages.append(percent)

            except Exception as e:
                print(f"Could not calculate invalid vectors for {fname}: {e}")

        if not percentages:
            return 0.0

        avg_percent = _round(sum(percentages) / len(percentages), 4)
        return avg_percent

    def processing(self, flist: list, processing_type="OpenPIV", multiple_eval=False):

        if multiple_eval is False:
            self.E_algorithm_dict.clear()            
            self.all_results_dict.clear()

        try:
            result_to_return = []

            self.log(
                timestamp=True,
                text="-----------------------------" + "\nPre processing finished.",
                group=self.p.PREPROC,
            )
            """Start the processing chain.



            This is the place to implement additional function calls.
            """

            # parallel PIV evaluation:
            print("Starting evaluation.")
            self.progressbar.start()

            self.get_settings()

            mp = MultiProcessing(self, processing_type)

            number_of_frames = mp.get_num_frames()
            self.process_type.config(
                text="Processing {} PIV image pair(s)".format(number_of_frames)
            )

            # keep number of cores in check
            # if there are no cored available, then raise exception
            if os.cpu_count() == 0:
                raise Exception("Warning: no available threads to process in.")
            # allow for automatic or manual core selection
            if self.p["manual_select_cores"]:
                cpu_count = self.p["cores"]

            else:
                cpu_count = os.cpu_count()

            if "idlelib" in sys.modules:
                self.log("Running as a child of IDLE: " "Deactivated multiprocessing.")
                cpu_count = 1

            if cpu_count >= os.cpu_count():
                raise Exception(
                    "Please lower the amount of cores "
                    + "or deselect >manually select cores<."
                )

            print(
                "Cores left: {} of {}.".format(
                    (os.cpu_count() - cpu_count), os.cpu_count()
                )
            )

            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================

            mp.processing_type = processing_type

            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

            mp.run(func=mp.process, n_cpus=cpu_count)

            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================

            return_fnames = mp.get_save_fnames()

            if os.path.exists("piv_failed.txt"):
                with open("piv_failed.txt", "r") as f:
                    print(f.read())
                os.remove("piv_failed.txt")
                success = False
            else:
                success = True

            # ==================================================CONTRIBUCIÓN======================================================================
            if "return_fnames" not in locals():
                return_fnames = []
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

            if success:

                # ==================================================CONTRIBUCIÓN======================================================================

                # update file list with result vector files:
                if not multiple_eval:
                    self.tkvars["fnames"].set(return_fnames)
                    result_to_return = None
                else:
                    if isinstance(return_fnames, (list, tuple)):
                        flist.extend(return_fnames)
                    else:
                        flist.append(return_fnames)

                    result_to_return = flist

                # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

                self.log(
                    timestamp=True,
                    text=f'\n{processing_type or "OpenPIV"} PIV evaluation finished.',
                    group=self.p.PIVPROC,
                )

                self.process_type.config(
                    text=f"Processed {number_of_frames} PIV image pair(s)"
                )

                # update GUI count
                self.get_settings()
                self.num_label.config(text=len(self.p["fnames"]))
            # ==================================================CONTRIBUCIÓN======================================================================


            else:
                result_to_return = flist if multiple_eval else None

            self.progressbar.stop()

            self.all_results_dict.update(mp.get_results_dict())

            algorithm_items = self.all_results_dict[processing_type]

            flo_fnames, E_means = zip(*[(flo, E_mean) for ( (flo, vec), E_all, E_mean ) in algorithm_items])
            
            flo_fnames = list(flo_fnames)
            E_means = list(E_means)

            self.E_algorithm_dict[processing_type] = E_means

            if multiple_eval is False:
                self.E_algorithm_df = pd.DataFrame(self.E_algorithm_dict, index=flo_fnames)
                fname = f'{processing_type}_df.csv'
                self.E_algorithm_df.to_csv(fname, sep='\t', float_format='%.4f')


#            print("-------------------------------------------------------")
#            print(mp.get_results_dict())
#            print("-------------------------------------------------------")

            return result_to_return
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

        except Exception as e:
            print("PIV evaluation thread stopped. " + str(e))
            self.progressbar.stop()
            self.process_type.config(text="Failed to process image pair(s)")
            return flist if "flist" in locals() and multiple_eval else None

    def start_postprocessing(self):
        """Wrapper function to start processing in a separate thread."""
        try:
            # if os.cpu_count() == 0:  # if there are no cored available,
            # then raise exception
            #    raise Exception('Warning: no available threads to
            #    process in.')
            check_processing(self)
            check_postprocessing(self.p)  # simple error checking
            self.postprocessing_thread = threading.Thread(target=self.postprocessing)
            self.postprocessing_thread.start()
        except Exception as e:
            print("Post-processing thread stopped. " + str(e))

    def postprocessing(self):
        try:
            self.progressbar.start()
            self.process_type.config(
                text="Processing {} PIV result(s)".format(len(self.p["fnames"]))
            )

            print("Starting validation. Please wait for validation to finish")

            # used to include the validation methods of addins loaded
            boolean_vars_of_add_ins = []
            for func in self.postprocessing_methods:
                # check rather func is an validation or postprocessing addin
                if self.postprocessing_methods[func][0] == "validation":
                    self.get_settings()
                    boolean_var = self.postprocessing_methods[func][1]
                    boolean_vars_of_add_ins.append(self.p[str(boolean_var)])
                    # check for checkbox which variable name is stored in
                    # boolean_var
                    if self.p[str(boolean_var)]:
                        post_proc = PostProcessing(self.p)
                        self.tkvars["fnames"].set(
                            self.postprocessing_methods[func][2](
                                self, post_proc.delimiter
                            )
                        )

            # standard deviation validation
            self.get_settings()
            if self.p["vld_sig2noise"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).sig2noise())

            # standard deviation validation
            self.get_settings()
            if self.p["vld_global_std"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).global_std())

            # global threshold validation
            self.get_settings()
            if self.p["vld_global_thr"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).global_val())

            # local median validation
            self.get_settings()
            if self.p["vld_local_med"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).local_median())

            # log validation parameters
            if (
                True in boolean_vars_of_add_ins
                or self.p["vld_sig2noise"]
                or self.p["vld_global_std"]
                or self.p["vld_global_thr"]
                or self.p["vld_local_med"]
            ):
                self.log(
                    timestamp=True,
                    text="\nValidation finished.",
                    group=self.p.VALIDATION,
                )
            print("Finished validation. Please wait for postprocessing " "to finish.")

            # used to include the postprocess methods of addins loaded
            boolean_vars_of_add_ins = []
            for func in self.postprocessing_methods:
                # check rather func is an validation or postprocessing addin
                if self.postprocessing_methods[func][0] == "postprocessing":
                    self.get_settings()
                    boolean_var = self.postprocessing_methods[func][1]
                    boolean_vars_of_add_ins.append(self.p[str(boolean_var)])
                    # check for checkbox which variable name is stored in
                    # boolean_var
                    if self.p[str(boolean_var)]:
                        post_proc = PostProcessing(self.p)
                        self.tkvars["fnames"].set(
                            self.postprocessing_methods[func][2](
                                self, post_proc.delimiter
                            )
                        )

            # post processing
            self.get_settings()
            if self.p["repl"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).repl_outliers())

            # smooth post processing
            self.get_settings()
            if self.p["smoothn"]:
                self.tkvars["fnames"].set(PostProcessing(self.p).smoothn_r())

            # average all ressults
            # self.get_settings()
            # if self.p['average_results']:
            #    self.tkvars['fnames'].set(
            #        PostProcessing(self.p).average())

            # log parameters
            if (
                True in boolean_vars_of_add_ins
                or self.p["repl"]
                or self.p["smoothn"]
                or self.p["average_results"]
            ):
                self.log(
                    timestamp=True,
                    text="\nPost processing finished.",
                    group=self.p.POSTPROC,
                )
            print("Finished postprocessing.")

            self.progressbar.stop()
            self.process_type.config(
                text="Processed {} PIV result(s)".format(len(self.p["fnames"]))
            )

            # update file count
            self.get_settings()
            self.num_label.config(text=len(self.p["fnames"]))
        except Exception as e:
            print("Postprocessing thread stopped. " + str(e))
            self.progressbar.stop()
            self.process_type.config(text="Failed to postprocess results(s)")

    def __init_widgets(self):
        """Creates a widget for each variable in a parameter object."""
        self.__init_buttons()
        f = ttk.Frame(self)
        f.pack(side="left", fill="both", expand="True")
        # holds riders for parameters
        self.__init_notebook(f)
        # plotting area
        self.__init_fig_canvas(f)
        # variable widgets:
        for key in sorted(self.p.index, key=self.p.index.get):
            if self.p.type[key] == "dummy":
                pass
            elif self.p.type[key] == "bool":
                self.__init_checkbutton(key)
            elif self.p.type[key] == "str[]":
                self.__init_listbox(key)
            elif self.p.type[key] == "text":
                self.__init_text_area(key)
            elif self.p.type[key] == "labelframe":
                self.__init_labelframe(key)
            elif self.p.type[key] == "label":
                self.__init_label(key)
            elif self.p.type[key] == "post_button":
                self.__init_post_button(key)
            elif self.p.type[key] == "h-spacer":
                self.__init_horizontal_spacer(key)
            elif self.p.type[key] == "sub_bool":
                self.__init_sub_checkbutton(key)
            elif self.p.type[key] == "sub_labelframe":
                self.__init_sub_labelframe(key)
            elif self.p.type[key] == "sub_h-spacer":
                self.__init_sub_horizontal_spacer(key)

            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================
            # ==================================================CONTRIBUCIÓN======================================================================

            # ==================================================AdaptivePIV======================================================================
            # ==================================================AdaptivePIV======================================================================
            # ==================================================AdaptivePIV======================================================================

            elif self.p.type[key] == "adaptive_piv_post_button":
                self.__init_adaptive_piv_post_button(key)

            # ==================================================Pivelocimetry======================================================================
            # ==================================================Pivelocimetry======================================================================
            # ==================================================Pivelocimetry======================================================================

            elif self.p.type[key] == "pivelocimetry_post_button":
                self.__init_pivelocimetry_post_button(key)

            # ================================================== K L T ======================================================================
            # ================================================== K L T ======================================================================
            # ================================================== K L T ======================================================================

            elif self.p.type[key] == "klt_post_button":
                self.__init_klt_post_button(key)

            # ======================================= TODOS LOS MÉTODOS (COMPARACIÓN DE MÉTODOS)=============================================
            # ======================================= TODOS LOS MÉTODOS (COMPARACIÓN DE MÉTODOS)=============================================
            # ======================================= TODOS LOS MÉTODOS (COMPARACIÓN DE MÉTODOS)=============================================

            elif self.p.type[key] == "all_post_button":
                self.__init_all_post_button(key)

            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
            # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

            elif self.p.type[key] is None:
                self.__add_tab(key)

            else:
                self.__init_entry(key)

            # create widgets that are not in OpenPivParams
            if self.p.index[key] == 3500:
                self.__init_analysisframe(key)
            if self.p.index[key] == 8120:
                self.__init_vec_colorpicker(key)

    def __init_fig_canvas(self, mother_frame):
        """
        Creates a plotting area for matplotlib.

        Parameters
        ----------
        mother_frame : ttk.Frame
            A frame to place the canvas in.
        """
        self.fig = Fig()  # Enlargended canvas to my preference
        self.fig_frame = ttk.Frame(mother_frame)
        self.fig_frame.pack(side="left", fill="both", expand="True")

        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.fig_frame)
        self.fig_canvas.draw()

        self.fig_canvas.get_tk_widget().pack(side="left", fill="x", expand="True")
        fig_toolbar = NavigationToolbar2Tk(self.fig_canvas, self.fig_frame)
        fig_toolbar.update()

        ttk.Button(
            self.fig_frame, text="start processing", command=self.start_processing
        ).pack(side="left")
        ttk.Button(
            self.fig_frame,
            text="start postprocessing",
            command=self.start_postprocessing,
        ).pack(side="left")
        ttk.Button(
            self.fig_frame,
            text="% invalid vectors",
            command=self.calculate_invalid_vectors,
        ).pack(side="left")

        self.progressbar = ttk.Progressbar(
            self.fig_frame, orient="horizontal", length=200, mode="indeterminate"
        )
        self.progressbar.pack(side="right")

        self.process_type = ttk.Label(self.fig_frame, text=" ")
        self.process_type.pack(side="right")

        self.fig_canvas._tkcanvas.pack(side="top", fill="both", expand="True")
        self.fig_canvas.mpl_connect(
            "key_press_event",
            lambda: key_press_handler(event, self.fig_canvas, fig_toolbar),
        )

    def __fig_toolbar_key_pressed(self, event):
        """Handles matplotlib toolbar events."""
        key_press_handler(event, self.fig_canvas, self.fig_toolbar)

    def __init_notebook(self, mother_frame):
        """The notebook is the root widget for tabs or riders."""
        style = ttk.Style()
        style.layout("TNotebook.Tab", [])
        self.nb = ttk.Notebook(mother_frame, width=260)
        self.nb.pack(side="right", fill="both", expand="False")

    def __add_tab(self, key):
        """Add an additional rider to the notebook."""
        self.set_frame.append(ttk.Frame(self.nb))
        self.nb.add(self.set_frame[-1], text=self.p.label[key])

    def __init_buttons(self):
        """Add buttons and bind them to methods."""
        f = ttk.Frame(self)
        files = ttk.Menubutton(f, text="File")
        options = tk.Menu(files, tearoff=0)
        files.config(menu=options)
        options.add_command(label="Import files", command=self.select_image_files)
        options.add_command(label="Import directory", command=self.open_directory)
        options.add_separator()
        options.add_command(
            label="Save session",
            command=lambda: self.p.dump_settings(filedialog.asksaveasfilename()),
        )
        options.add_command(label="Load session", command=self.load_settings)
        options.add_command(label="Reset session", command=self.reset_params)
        options.add_separator()
        options.add_command(label="Move files", command=self.move_files)
        options.add_command(label="Delete files", command=self.delete_files)
        options.add_separator()
        options.add_command(label="Crop Image", command=self.crop_image)
        options.add_separator()
        options.add_command(
            label="Select Add Ins", command=lambda: AddInHandler.select_add_ins(self)
        )
        options.add_command(label="Exit", command=self.destroy)
        files.pack(side="left", fill="x")

        general = ttk.Menubutton(f, text="General")
        options1 = tk.Menu(general, tearoff=0)
        general.config(menu=options1)
        options1.add_command(
            label="General settings", command=lambda: self.selection(0)
        )
        general.pack(side="left", fill="x")

        preproc = ttk.Menubutton(f, text="Preprocessing")
        options2 = tk.Menu(preproc, tearoff=0)
        preproc.config(menu=options2)
        options2.add_command(label="Preprocessing", command=lambda: self.selection(1))
        preproc.pack(side="left", fill="x")

        piv = ttk.Menubutton(f, text="Analysis")
        options2 = tk.Menu(piv, tearoff=0)
        piv.config(menu=options2)
        options2.add_command(
            label="Algorithms/Calibration", command=lambda: self.selection(2)
        )
        options2.add_command(label="Windowing", command=lambda: self.selection(3))
        options2.add_command(label="Validation", command=lambda: self.selection(4))
        options2.add_command(
            label="Pass Postprocessing", command=lambda: self.selection(5)
        )

        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================

        # ==================================================AdaptivePIV======================================================================
        # ==================================================AdaptivePIV======================================================================
        # ==================================================AdaptivePIV======================================================================

        options2.add_command(label="AdaptivePIV", command=lambda: self.selection(6))

        # ==================================================Pivelocimetry====================================================================
        # ==================================================Pivelocimetry====================================================================
        # ==================================================Pivelocimetry====================================================================

        options2.add_command(label="Pivelocimetry", command=lambda: self.selection(7))

        # ================================================== K L T =========================================================================
        # ================================================== K L T =========================================================================
        # ================================================== K L T =========================================================================

        options2.add_command(label="KLT", command=lambda: self.selection(8))

        options2.add_command(
            label="Start algorithms comparison", command=lambda: self.selection(9)
        )

        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================

        options2.add_command(label="Start Analysis", command=self.start_processing)

        piv.pack(side="left", fill="x")

        postproc = ttk.Menubutton(f, text="Postprocess")
        options3 = tk.Menu(postproc, tearoff=0)
        postproc.config(menu=options3)
        options3.add_command(label="Postprocess", command=lambda: self.selection(10))
        options3.add_command(
            label="Start Postprocessing", command=self.start_postprocessing
        )
        postproc.pack(side="left", fill="x")

        plot = ttk.Menubutton(f, text="Plotting")
        options4 = tk.Menu(plot, tearoff=0)
        plot.config(menu=options4)
        options4.add_command(label="Plotting", command=lambda: self.selection(11))
        options4.add_command(
            label="Modify Appearance", command=lambda: self.selection(12)
        )
        plot.pack(side="left", fill="x")
        lab_func = ttk.Menubutton(f, text="Lab Book")
        options6 = tk.Menu(lab_func, tearoff=0)
        lab_func.config(menu=options6)
        options6.add_command(label="Show Lab Book", command=lambda: self.selection(13))
        lab_func.pack(side="left", fill="x")

        usage_func = ttk.Menubutton(f, text="Usage")
        options7 = tk.Menu(usage_func, tearoff=0)
        usage_func.config(menu=options7)
        options7.add_command(
            label="Usage",
            command=lambda: messagebox.showinfo(
                title="Help", message=inspect.cleandoc(OpenPivGui.__doc__)
            ),
        )
        usage_func.pack(side="left", fill="x")

        web_func = ttk.Menubutton(f, text="Web")
        options8 = tk.Menu(web_func, tearoff=0)
        web_func.config(menu=options8)
        options8.add_command(label="Web", command=self.readme)
        web_func.pack(side="left", fill="x")

        addin_func = ttk.Menubutton(f, text="Add_In Functions")
        addin_func_options = tk.Menu(addin_func, tearoff=0)
        addin_func.config(menu=addin_func_options)
        addin_func.pack(side="left", fill="x")

        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================

        for button in self.buttons:
            self.buttons[button](self, addin_func_options)
        addin_func.pack(side="left", fill="x")
        f.pack(side="top", fill="x")

        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN========================================================

    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================

    def crop_image(self):
        """Función que abre la ventana secundaria al pulsar el menú"""

        try:
            import ast

            lista_de_archivos = ast.literal_eval(self.tkvars["fnames"].get())
            if not lista_de_archivos:
                print("Error: No hay imágenes cargadas")
                return
            image_path = lista_de_archivos[0]
        except Exception as e:
            print(f"Error accediendo a la lista de archivos: {e}")
            return

        top = Toplevel(self)
        top.title("Seleccionar área de recorte")

        top.transient(self)
        top.grab_set()

        cw = CropWindow(top, self, image_path)

        # Esperar a que la ventana termine de cerrase (cuando el usuario haya terminado de recortar la imagen) para que se cargue la lista
        #   de archivos en la siguiente línea. Si esto no se hace, la lista se queda en blanco y no cargará los arhivos, sin embargo, los
        #   archivos sí serán creados.
        self.wait_window(top)

        if cw.result is False:
            return
        else:
            return_cfnames = cw.get_cimages_list()
            print("return_fnames = ", return_cfnames)
            self.tkvars["fnames"].set(return_cfnames)
            self.num_label.config(text=len(self.p["fnames"]))

        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

        return

    def selection(self, num):
        self.nb.select(num)

    def calculate_invalid_vectors(self):
        try:
            self.get_settings()
            data = self.load_pandas(self.p["fnames"][self.index])
            data = data.to_numpy().astype(float)
            try:
                invalid = data[:, 4].astype("bool")
            except BaseException:
                invalid = np.asarray([True for i in range(len(data))])
                print("No typevectors found")

            invalid = np.count_nonzero(invalid)
            percent = _round(((invalid / len(data[:, 0])) * 100), 4)
            message = "Percent invalid vectors for result index {}: {}%".format(
                self.index, percent
            )

            if self.p["pop_up_info"]:
                messagebox.showinfo(title="Statistics", message=message)
            print(message)

        except Exception as e:
            print("Could not read file for calculating percent of" " invalid vectors.")
            print("Reason: " + str(e))

    def reset_params(self):
        """Reset parameters to default values."""
        answer = messagebox.askyesno(
            title="Reset session", message="Reset all parameters to default values?"
        )
        if answer:
            self.p = OpenPivParams()
            self.set_settings()

    def readme(self):
        """Opens https://github.com/OpenPIV/openpiv_tk_gui."""
        webbrowser.open("https://github.com/OpenPIV/openpiv_tk_gui")

    def delete_files(self):
        """Delete files currently listed in the file list."""
        answer = messagebox.askyesno(
            title="Delete files",
            message="Are you sure you want to delete selected files?",
        )
        if answer:
            files = self.p["fnames"][:]
            for f in files:
                os.remove(f)
            self.navigate("back")

    def move_files(self):
        """Move files to a new place."""
        files = self.p["fnames"][:]
        dir = filedialog.askdirectory(mustexist=False)
        if len(dir) > 0:
            if not os.path.exists(dir):
                os.mkdir(dir)
            for src in files:
                dst = dir + os.path.sep + os.path.basename(src)
                shutil.move(src, dst)
            self.navigate("back")

    def load_settings(self):
        """Load settings from a JSON file."""
        settings = filedialog.askopenfilename()
        if len(settings) > 0:
            self.p.load_settings(settings)
            self.set_settings()

    def load_pandas(self, fname):
        """
        Load files in a pandas data frame.

        On the rider named General, the parameters for loading
        the data frames can be specified.
        No parameters have to be set for image processing.

        Parameters
        ----------
        fname :
            A filename.

        Returns
        -------
        pandas.DataFrame :
            In case of an error, the errormessage is returned (str).
        """

        ext = fname.split(".")[-1]
        if ext in ["txt", "dat", "jvc", "vec", "csv"]:
            file = pd.read_csv(fname)
            for column in file:
                for line in file[column]:
                    if "\t" in line:
                        sep = "\t"
                        if "," in line:
                            decimal = ","
                        else:
                            decimal = "."
                    elif ";" in line:
                        sep = ";"
                        if "," in line:
                            decimal = ","
                        else:
                            decimal = "."
                    elif ", " in line:
                        sep = ","
                        decimal = "."
                    else:
                        sep = " "
                        if "," in line:
                            decimal = ","
                        else:
                            decimal = "."
            skip_rows = 0
            names = None
            for line in file.keys():
                entries = str(line).split(sep)
                for entry in entries:
                    try:
                        float(entry)
                    except BaseException:
                        skip_rows += 1
                        break
            if names is None:
                for num, line in file.iterrows():
                    for char in line:
                        entries = str(char).split(sep)
                        for entry in entries:
                            try:
                                float(entry)
                            except BaseException:
                                skip_rows += 1
                                break
                        names = ["x", "y", "vx", "vy"]
                        for part in range(1, len(entries) - 3):
                            names.append("val-{}".format(part))

            data = pd.read_csv(
                fname,
                decimal=decimal,
                skiprows=skip_rows - 1 if skip_rows != 0 else 0,
                sep=sep,
                header=0 if skip_rows != 0 else None,
                names=names,
            )
        else:
            data = "File could not be read. Possibly it is an image file."
        return data

    def __init_listbox(self, key):
        """
        Creates an interactive list of filenames.

        Parameters
        ----------
        key : str
            Key of a settings object.
        """
        # root widget
        f = ttk.Frame(self)
        f.pack(side="bottom", fill="both", expand="True")
        # filter hint
        hint_frame = ttk.Frame(f)
        hint_title = ttk.Label(hint_frame, text=" filter: ")
        self.filter_hint = ttk.Label(hint_frame, text="None")
        hint_title.pack(anchor="nw", side="left")
        self.filter_hint.pack(anchor="nw")
        hint_frame.pack(side="top", fill="x", expand="False")

        # number of files
        num_frame = ttk.Frame(f)
        num_label = ttk.Label(num_frame, text=" number of files: ")
        self.num_label = ttk.Label(num_frame, text=len(self.p["fnames"]))
        num_label.pack(anchor="nw", side="left")
        self.num_label.pack(anchor="nw")
        num_frame.pack(side="top", fill="x", expand="False")

        # scrolling
        sbx = ttk.Scrollbar(f, orient="horizontal")
        sbx.pack(side="top", fill="x")
        sby = ttk.Scrollbar(f, orient="vertical")
        sby.pack(side="right", fill="y")
        self.lb = tk.Listbox(f, yscrollcommand=sbx.set)
        self.lb = tk.Listbox(f, yscrollcommand=sby.set)
        sbx.config(command=self.lb.xview)
        sby.config(command=self.lb.yview)
        self.lb["width"] = 25

        # background variable
        self.tkvars.update({key: tk.StringVar()})
        self.tkvars[key].set(self.p["fnames"])
        self.lb["listvariable"] = self.tkvars[key]

        # interaction
        self.lb.bind("<<ListboxSelect>>", self.__listbox_selection_changed)
        self.lb.pack(side="top", fill="y", expand="True")

        # navigation buttons
        f = ttk.Frame(f)
        ttk.Button(f, text="< back", command=lambda: self.navigate("back")).pack(
            side="left", fill="x"
        )
        ttk.Button(f, text="forward >", command=lambda: self.navigate("forward")).pack(
            side="left", fill="x"
        )

        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================
        # ==================================================CONTRIBUCIÓN======================================================================

        ttk.Button(f, text="Save Files", command=lambda: self.save_images()).pack(
            side="right", fill="x"
        )

        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
        # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

        f.pack()

    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================

    def save_images(self):

        i = 0
        file_list = self.lb.get(0, tk.END)
        path = os.getcwd()
        f_path = os.path.join(path, f"experiment_{i}")

        while os.path.exists(f_path):
            i += 1
            f_path = os.path.join(path, f"experiment_{i}")

        try:
            os.mkdir(f_path)
        except Exception as e:
            print("An error has occurred: ", e)

        try:
            for file in file_list:
                shutil.copy(file, f_path)
        except FileNotFoundError:
            print("Some file doesn't exist")
        except Exception as e:
            print("An error has occurred while saving file(s)", e)

        messagebox.showinfo(
            title="Files Saved", message=f"Files saved in the following path {f_path}"
        )

    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

    def get_filelistbox(self):
        """
        Return a handle to the file list widget.

        Returns
        -------
        tkinter.Listbox
            A handle to the listbox widget holding the filenames
        """
        return self.lb

    def navigate(self, direction):
        """
        Navigate through processing steps.

        Display a filtered list of files of the current
        directory. This function cycles through the filters
        specified by the key 'navi_pattern' in the settings object.

        Parameters
        ----------
        direction : str
            'back' or 'forward'.
        """
        pattern_lst = str2list(self.p["navi_pattern"])
        dirname = os.path.dirname(self.p["fnames"][0])
        files = os.listdir(dirname)
        if direction == "back":
            self.p.navi_position -= 1
            if self.p.navi_position == -1:
                self.p.navi_position = len(pattern_lst) - 1
        elif direction == "forward":
            self.p.navi_position += 1
            if self.p.navi_position == len(pattern_lst):
                self.p.navi_position = 0
        filtered = self.file_filter(files, pattern_lst[self.p.navi_position])
        if filtered:
            filtered = sorted([dirname + os.sep + f for f in filtered])
            self.tkvars["fnames"].set(filtered)
            self.get_settings()

        # try next filter, if result is empty
        else:
            self.navigate(direction)

        # update file count
        self.num_label.config(text=len(self.p["fnames"]))

    def file_filter(self, files, pattern):
        """
        Filter a list of files to  match a pattern.

        Parameters
        ----------
        files : str[]
            A list of pathnames.
        pattern : str
            A regular expression for filtering the list.

        Returns
        -------
        str[]
            List items that match the pattern.
        """
        filtered = []
        self.filter_hint.config(text=pattern)
        print("file filter: " + pattern)
        p = re.compile(pattern)
        for f in files:
            if p.search(f):
                filtered.append(f)
        return filtered

    def __init_text_area(self, key):
        """
        Init a text area, here used as a lab-book, for example.

        The content is saved automatically to the parameter object,
        when the mouse leaves the text area.
        """
        self.ta.update({key: (tk.Text(self.set_frame[-1], undo=True))})
        ta = self.ta[list(self.ta)[-1]]
        ta.pack()
        ta.bind("<Leave>", (lambda _: self.__get_text(key, ta)))
        ttk.Button(
            self.set_frame[-1], text="clear", command=lambda: ta.delete("1.0", tk.END)
        ).pack(fill="x")
        ttk.Button(
            self.set_frame[-1], text="undo", command=lambda: ta.edit_undo()
        ).pack(fill="x")
        ttk.Button(
            self.set_frame[-1], text="redo", command=lambda: ta.edit_redo()
        ).pack(fill="x")

    def __get_text(self, key, text_area):
        """Get text from text_area and copy it to parameter object."""
        self.p[key] = text_area.get("1.0", tk.END)

    def __listbox_selection_changed(self, event):
        """Handles selection change events of the file listbox."""
        try:
            self.index = event.widget.curselection()[0]
        except IndexError:
            pass  # nothing selected
        else:
            self.get_settings()
            self.show(self.p["fnames"][self.index])

            if self.p["data_information"]:
                self.show_information(self.p["fnames"][self.index])

    def __init_labelframe(self, key):
        """Add a label frame for widgets."""
        f = ttk.Frame(self.set_frame[-1])
        self.pane = ttk.Panedwindow(f, orient="vertical", width=400)
        self.lf = tk.LabelFrame(self.pane, text=self.p.label[key])
        self.lf.config(borderwidth=2, width=400, relief="groove")
        self.pane.add(self.lf)
        self.pane.pack(side="left", fill="both")
        f.pack(fill="both")

    def __init_sub_labelframe(self, key):
        """Add a label frame for widgets."""
        self.sub_lf = tk.LabelFrame(self.lf, text=self.p.label[key])
        self.sub_lf.config(borderwidth=2, width=400, relief="groove")
        self.sub_lf.pack(fill="both", pady=4, padx=4)

    def __init_post_button(self, event):
        f = ttk.Frame(self.lf)
        f.pack(fill="both")
        ttk.Button(
            f, text="start postprocessing", command=self.start_postprocessing
        ).pack(side="top")

    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================
    # ==================================================CONTRIBUCIÓN======================================================================

    # ==================================================AdaptivePIV=======================================================================
    # ==================================================AdaptivePIV=======================================================================
    # ==================================================AdaptivePIV=======================================================================

    def __init_adaptive_piv_post_button(self, key):
        f = ttk.Frame(self.lf)
        f.pack(fill="both")
        ttk.Button(
            f,
            text="start AdaptivePIV",
            command=lambda: self.start_processing("AdaptivePIV"),
        ).pack(side="top")

    # ==================================================Pivelocimetry=====================================================================
    # ==================================================Pivelocimetry=====================================================================
    # ==================================================Pivelocimetry=====================================================================

    def __init_pivelocimetry_post_button(self, key):
        f = ttk.Frame(self.lf)
        f.pack(fill="both")
        ttk.Button(
            f,
            text="start Pivelocimetry",
            command=lambda: self.start_processing(
                "Pivelocimetry",
            ),
        ).pack(side="top")

    # ================================================== K L T ==========================================================================
    # ================================================== K L T ==========================================================================
    # ================================================== K L T ==========================================================================

    def __init_klt_post_button(self, key):
        f = ttk.Frame(self.lf)
        f.pack(fill="both")
        ttk.Button(
            f,
            text="start KLT",
            command=lambda: self.start_processing(
                "KLT",
            ),
        ).pack(side="top")

    # ================================================== TODOS LOS MÉTODOS (COMPARAR)==================================================
    # ================================================== TODOS LOS MÉTODOS (COMPARAR)==================================================
    # ================================================== TODOS LOS MÉTODOS (COMPARAR)==================================================
    def __init_all_post_button(self, key):
        f = ttk.Frame(self.lf)
        f.pack(fill="both")
        ttk.Button(
            f, text="Compare algorithms", command=lambda: self.start_processing("ALL")
        ).pack(side="top")

    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================
    # ====================================================FIN DE LA CONTRIBUCIÓN====================================================

    def __init_horizontal_spacer(self, key):
        """Add a horizontal spacer line for widgets."""
        f = ttk.Frame(self.lf)
        hs = ttk.Separator(f)
        hs.pack(fill="x")
        f.pack(fill="both")

    def __init_sub_horizontal_spacer(self, key):
        """Add a horizontal spacer line for widgets"""
        f = ttk.Frame(self.sub_lf)
        hs = ttk.Separator(f)
        hs.pack(fill="x")
        f.pack(fill="both")

    def __init_label(self, key):
        f = ttk.Frame(self.lf)
        label1 = ttk.Label(f, text=self.p.label[key])
        label1.pack(side="left")
        f.pack()

    def __init_entry(self, key):
        """
        Creates a label and an entry in a frame.

        A corresponding tk background textvariable is also crated. An
        option menu is created instead of en entry, if a hint is given
        in the parameter object. The help string in the parameter object
        is used for creating a tooltip.

        Parameter
        ---------
        key : str
            Key of a parameter obj.
        """
        padding = 2
        # sub label frames
        if (
            self.p.type[key] == "sub_int"
            or self.p.type[key] == "sub_float"
            or self.p.type[key] == "sub"
        ):
            f = ttk.Frame(self.sub_lf)
            f.pack(fill="x")
            l = ttk.Label(f, text=self.p.label[key])
            CreateToolTip(l, self.p.help[key])
            l.pack(side="left", padx=padding, pady=padding)
            if self.p.type[key] == "sub_int":
                self.tkvars.update({key: tk.IntVar()})
            elif self.p.type[key] == "sub_float":
                self.tkvars.update({key: tk.DoubleVar()})
            elif self.p.type[key] == "sub":
                self.tkvars.update({key: tk.StringVar()})
            if self.p.hint[key] is not None:
                e = ttk.OptionMenu(f, self.tkvars[key], "spacer", *self.p.hint[key])
            else:
                e = ttk.Entry(f, width=17)
                e["textvariable"] = self.tkvars[key]
            CreateToolTip(e, self.p.help[key])
            e.pack(side="right", padx=padding, pady=padding)

        else:
            f = ttk.Frame(self.lf)
            f.pack(fill="x")
            l = ttk.Label(f, text=self.p.label[key])
            CreateToolTip(l, self.p.help[key])
            l.pack(side="left", padx=padding, pady=padding)
            if self.p.type[key] == "int":
                self.tkvars.update({key: tk.IntVar()})
            elif self.p.type[key] == "float":
                self.tkvars.update({key: tk.DoubleVar()})
            else:
                self.tkvars.update({key: tk.StringVar()})
            if self.p.hint[key] is not None:
                e = ttk.OptionMenu(f, self.tkvars[key], "spacer", *self.p.hint[key])
            else:
                e = ttk.Entry(f, width=17)
                e["textvariable"] = self.tkvars[key]
            CreateToolTip(e, self.p.help[key])
            e.pack(side="right", padx=padding, pady=padding)

    def __init_checkbutton(self, key):
        """Create a checkbutton with label and tooltip."""
        f = ttk.Frame(self.lf)
        f.pack(fill="x")
        self.tkvars.update({key: tk.BooleanVar()})
        self.tkvars[key].set(bool(self.p[key]))
        cb = ttk.Checkbutton(f)
        cb["variable"] = self.tkvars[key]
        cb["onvalue"] = True
        cb["offvalue"] = False
        cb["text"] = self.p.label[key]
        CreateToolTip(cb, self.p.help[key])
        cb.pack(side="left")

    def __init_sub_checkbutton(self, key):
        """
        Create a checkbutton with label and tooltip.
        """
        f = ttk.Frame(self.sub_lf)
        f.pack(fill="x")
        self.tkvars.update({key: tk.BooleanVar()})
        self.tkvars[key].set(bool(self.p[key]))
        cb = ttk.Checkbutton(f)
        cb["variable"] = self.tkvars[key]
        cb["onvalue"] = True
        cb["offvalue"] = False
        cb["text"] = self.p.label[key]
        CreateToolTip(cb, self.p.help[key])
        cb.pack(side="left")

    def __init_vec_colorpicker(self, key):
        whitespace = "                                 "
        f = ttk.Frame(self.lf)
        l = ttk.Label(f, text="invalid vector color")
        CreateToolTip(l, self.p.help[key])
        l.pack(side="left")
        self.invalid_color = tk.Button(
            f,
            text=whitespace,
            bg=self.p["invalid_color"],
            relief="groove",
            command=self.invalid_colorpicker,
        )
        self.invalid_color.pack(side="right")
        f.pack(fill="x")

        f = ttk.Frame(self.lf)
        l = ttk.Label(f, text="valid vector color")
        CreateToolTip(l, self.p.help[key])
        l.pack(side="left")
        print(self.p["valid_color"])
        self.valid_color = tk.Button(
            f,
            text=whitespace,
            bg=self.p["valid_color"],
            relief="groove",
            command=self.valid_colorpicker,
        )
        self.valid_color.pack(side="right")
        f.pack(fill="x")

    def invalid_colorpicker(self):
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.p["invalid_color"] = color
            self.invalid_color.config(bg=self.p["invalid_color"])

    def valid_colorpicker(self):
        color = colorchooser.askcolor()[1]
        if color is not None:
            self.p["valid_color"] = color
            self.valid_color.config(bg=self.p["valid_color"])

    def log(self, columninformation=None, timestamp=False, text=None, group=None):
        """
        Add an entry to the lab-book.

        The first initialized text-area is assumed to be the
        lab-book.
        It is internally accessible by self.ta[0].

        Parameters
        ----------
        timestamp : bool
            Print current time.
            Pattern: yyyy-mm-dd hh:mm:ss.
            (default: False)
        text : str
            Print a text, a linebreak is appended.
            (default None)
        group : int
            Print group of parameters.
            (e.g. OpenPivParams.PIVPROC)
        columninformation : list
            Print column information of the selected file.

        Example
        -------
        log(text='processing parameters:',
            group=OpenPivParams.POSTPROC)
        """
        if text is not None:
            self.ta["lab_book_content"].insert(tk.END, text + "\n")
        if timestamp:
            td = datetime.today()
            s = (
                "-".join((str(td.year), str(td.month), str(td.day)))
                + " "
                + ":".join((str(td.hour), str(td.minute), str(td.second)))
            )
            self.log(text=s)
        if group is not None:
            self.log(text="Parameters:")
            for key in self.p.param:
                key_type = self.p.type[key]
                if key_type not in [
                    "labelframe",
                    "sub_labelframe",
                    "h-spacer",
                    "sub_h-spacer",
                    "post_button",
                ]:
                    if group < self.p.index[key] < group + 1000:
                        s = key + ": " + str(self.p[key])
                        self.log(text=s)
        if columninformation is not None:
            self.ta["lab_book_content"].insert(tk.END, str(columninformation) + "\n")

    def show_information(self, fname):
        """
        Shows the column names of the chosen file in the labbook.

        Parameters
        ----------
        fname : str
            A filename.
        """
        data = self.load_pandas(fname)
        if isinstance(data, str):
            self.log(text=data)
        else:
            self.log(columninformation=list(data.columns.values))

    def get_settings(self):
        """Copy widget variables to the parameter object."""
        for key in self.tkvars:
            if self.p.type[key] == "str[]":
                self.p[key] = str2list(self.tkvars[key].get())
            elif self.p.type[key] == "[]":
                self.p[key] = self.p[key]
            else:
                self.p[key] = self.tkvars[key].get()
        for key in self.ta:
            self.__get_text(key, self.ta[key])

    def set_settings(self):
        """Copy values of the parameter object to widget variables."""
        for key in self.tkvars:
            self.tkvars[key].set(self.p[key])
        for key in self.ta:
            self.ta[key].delete("1.0", tk.END)
            self.ta[key].insert("1.0", self.p[key])

    def select_image_files(self):
        """Show a file dialog to select one or more filenames."""
        print("Use Ctrl + Shift to select multiple files.")
        files = filedialog.askopenfilenames(multiple=True)
        if len(files) > 0:
            self.p["fnames"] = list(files)
            self.tkvars["fnames"].set(self.p["fnames"])

        # update file count
        self.num_label.config(text=len(self.p["fnames"]))

    def open_directory(self):
        """Show a dialog for opening a directory."""
        dir = filedialog.askdirectory()
        if len(dir) > 0:
            files = [dir + os.sep + file for file in os.listdir(dir)]
            self.p["fnames"] = list(files)
            self.tkvars["fnames"].set(self.p["fnames"])
        self.navigate("back")

        # update file count
        self.num_label.config(text=len(self.p["fnames"]))

    def show(self, fname):
        """
        Display a file.

        This method distinguishes vector data (file extensions
        txt, dat, jvc,vec and csv) and images (all other file extensions).

        Parameters
        ----------
        fname : str
            A filename.
        """
        ext = fname.split(".")[-1]
        self.fig.clear()
        data = self.load_pandas(fname)
        if ext in ["txt", "dat", "jvc", "vec", "csv"]:
            if self.p["plot_type"] == "vectors":
                vec_plot.vector(
                    data,
                    self.p,
                    self.fig,
                    invert_yaxis=self.p["invert_yaxis"],
                    scale=self.p["vec_scale"],
                    width=self.p["vec_width"],
                    valid_color=self.p["valid_color"],
                    invalid_color=self.p["invalid_color"],
                )
            elif self.p["plot_type"] == "profiles":
                vec_plot.profiles(
                    data,
                    self.p,
                    fname,
                    self.fig,
                    orientation=self.p["profiles_orientation"],
                )
            elif self.p["plot_type"] == "scatter":
                vec_plot.scatter(data, self.fig)
            elif self.p["plot_type"] == "contour":
                vec_plot.contour(data, self.p, self.fig)

            elif self.p["plot_type"] == "contour + vectors":
                vec_plot.contour_and_vector(
                    data,
                    self.p,
                    self.fig,
                    scale=self.p["vec_scale"],
                    width=self.p["vec_width"],
                )
            else:
                for i in self.plotting_methods:
                    if self.p["plot_type"] in self.plotting_methods[i][2]:
                        self.plotting_methods[i][3](data, self.p, self.fig)

        else:
            self.show_img(fname)
        self.fig.canvas.draw()

    def show_img(self, fname):
        """
        Display an image.

        Parameters
        ----------
        fname : str
        Pathname of an image file.
        """
        img = piv_tls.imread(fname)
        print("\nimage data type: {}".format(img.dtype))
        print("max count: {}".format(img.max()))
        print("min count {}:".format(img.min()))
        if "int" not in str(img.dtype):
            print(
                "Warning: For PIV processing, "
                + "image will be normalized and converted to uint8. "
                + "This may cause a loss of precision."
            )

        print("Processing image.")

        img = img.astype(np.int32)
        # generate background if needed
        if self.p["background_subtract"] and self.p["background_type"] != "minA - minB":
            background = gen_background(self.p)

        elif (
            self.p["background_subtract"] and self.p["background_type"] == "minA - minB"
        ):
            if fname == self.p["fnames"][-1]:
                img2 = self.p["fnames"][-2]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img2, img)
            else:
                img2 = self.p["fnames"][self.index + 1]
                img2 = piv_tls.imread(img2)
                background = gen_background(self.p, img, img2)
        else:
            background = None
        # preprocessing method became parameter due to the AddInHandler
        img = process_images(
            self, img, self.preprocessing_methods, background=background
        )
        img = img.astype(np.int32)

        print("Processed image.")
        print("max count: {}".format(img.max()))
        print("min count {}:".format(img.min()))

        self.fig.add_subplot(111).matshow(
            img, cmap=plt.cm.Greys_r, vmax=self.p["matplot_intensity"]
        )

        self.fig.canvas.draw()

    def get_parameters(self):
        return self.p

    def destroy_for_new_addins(self) -> None:
        """
        used to destroy the active object of the GUI and reinitialize
        it for inserting the addin methods and buttons

        :return: None
        """
        print("Updating GUI")
        # reset the plot_type because the chosen one might not longer exist
        self.p["plot_type"] = "contour + vectors"
        # save old gui status
        self.p.dump_settings(self.p.params_fname)
        # destroy old gui
        tk.Tk.destroy(self)
        # initialize a new one
        self.__init__()

    def destroy(self):
        """Destroy the OpenPIV GUI.

        Settings are automatically saved.
        """
        if messagebox.askyesno("Exit Manager", "Are you sure you want to exit?"):
            print("Saving settings")
            self.get_settings()
            self.p.dump_settings(self.p.params_fname)
            print("Destroying GUI")
            tk.Tk.destroy(self)
            # sometimes the GUI closes, but the main thread still runs
            print("Destorying main thread")
            sys.exit()
            print("Destroyed main thread.")
            # This should not execute if the thread is destroyed.
            # Could cause possible issue in the future.

if __name__ == "__main__":
    openPivGui = OpenPivGui()
    # a good starting size for the GUI
    openPivGui.geometry("1150x850")
    openPivGui.mainloop()

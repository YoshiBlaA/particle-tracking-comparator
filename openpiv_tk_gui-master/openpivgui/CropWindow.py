import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk, ImageOps
from pathlib import Path
import os

class CropWindow:
    def __init__(self, top, gui, image_path):

        self.top = top
        self.GUI = gui
        self.p = gui.p
        self.cropped_images_list = []
        self.result = False

        # 1. Obtener dimensiones de la pantalla para limitar el tamaño
        # Usamos el 80% para dejar espacio a la barra de tareas y botones
        max_w = self.top.winfo_screenwidth() * 0.8
        max_h = self.top.winfo_screenheight() * 0.8

        # 2. Cargar imagen y añadir borde
        self.img_pil_original = Image.open(image_path)
        self.padding_px = 4
        self.img_pil_padded = ImageOps.expand(self.img_pil_original, border=self.padding_px, fill='black')

        orig_w, orig_h = self.img_pil_padded.size

        # 3. CALCULAR ESCALA DINÁMICA
        # Calculamos el ratio necesario para que quepa en el ancho y en el alto
        ratio_w = max_w / orig_w
        ratio_h = max_h / orig_h

        # Elegimos el menor ratio para asegurar que la imagen quepa entera en pantalla
        self.factor_escala = min(ratio_w, ratio_h)

        # OPCIONAL: Si la imagen es muy pequeña, no dejar que se agrande más de 4 veces
        # para evitar que se vea demasiado pixelada:
        # self.factor_escala = min(self.factor_escala, 4.0)

        self.display_width = int(orig_w * self.factor_escala)
        self.display_height = int(orig_h * self.factor_escala)

        # 4. Redimensionar para mostrar
        self.img_pil_display = self.img_pil_padded.resize(
            (self.display_width, self.display_height), Image.Resampling.LANCZOS
        )
        self.tk_image = ImageTk.PhotoImage(self.img_pil_display)

        self.top.title(f"Crop window")

        # 5. Configurar Canvas
        self.canvas = tk.Canvas(self.top, width=self.display_width, height=self.display_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        # 6. Inicializar rectángulo de selección
        self.left = 2
        self.top_edge = 2
        self.right = self.display_width - 2
        self.bottom = self.display_height - 2

        self.rect = self.canvas.create_rectangle(
            self.left, self.top_edge, self.right, self.bottom,
            outline='red', width=3
        )

        # 7. Variables de estado y Bindings
        self.drag_data = {"edge": None, "x": 0, "y": 0}
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 8. Botones
        btn = tk.Button(self.top, text="Apply Crop", command=self.confirm)
        btn.pack(pady=10)

        self.top.update()
    
        message = 'Drag borders to select crop area'
        messagebox.showwarning(title='How to usee',
                                   message=message,
                                   parent=self.top)     


    def _get_edge(self, x, y):
        margin = 15 
        if abs(x - self.left) < margin: return "left"
        if abs(x - self.right) < margin: return "right"
        if abs(y - self.top_edge) < margin: return "top"
        if abs(y - self.bottom) < margin: return "bottom"
        return None

    def on_click(self, event):
        self.drag_data["edge"] = self._get_edge(event.x, event.y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        edge = self.drag_data["edge"]
        if not edge: return

        if edge == "left": self.left = max(0, event.x)
        elif edge == "right": self.right = min(self.display_width, event.x)
        elif edge == "top": self.top_edge = max(0, event.y)
        elif edge == "bottom": self.bottom = min(self.display_height, event.y)
        
        self.canvas.coords(self.rect, self.left, self.top_edge, self.right, self.bottom)

    def on_release(self, event):
        self.drag_data["edge"] = None

    def confirm(self) -> list:
        # CAMBIO AQUÍ: Usar self.factor_escala en lugar de self.scale
        padded_left = int(self.left / self.factor_escala)
        padded_top = int(self.top_edge / self.factor_escala)
        padded_right = int(self.right / self.factor_escala)
        padded_bottom = int(self.bottom / self.factor_escala)
        
        # El resto del cálculo se mantiene igual y funcionará perfecto
        orig_left = max(0, padded_left - self.padding_px)
        orig_top = max(0, padded_top - self.padding_px)
        orig_right = min(self.img_pil_original.width, padded_right - self.padding_px)
        orig_bottom = min(self.img_pil_original.height, padded_bottom - self.padding_px)
        
        crop_box = (orig_left, orig_top, orig_right, orig_bottom)
        print(f"Crop box con los siguientes valores: {crop_box}")

        

        image_path_list = self.p['fnames'][:]
        
        for image_path in image_path_list:
            try:
                # Asumimos que esta función existe y acepta la caja
                cropped_image = self.crop_image(image_path, crop_box)
            
                # Asumimos que esta función guarda la imagen y devuelve la ruta
                cropped_image_path = self.save_cropped_image(cropped_image, image_path)
            
                self.cropped_images_list.append(cropped_image_path)
                #print(f"Recortada: {image_path}")
            except Exception as e:
                print(f"Error procesando {image_path}: {e}")

        print("Proceso de recorte por lotes finalizado.")

        self.result = True

        self.top.destroy()


    def crop_image(self, image_path, crop_box):
        img = Image.open(image_path)
        return img.crop(crop_box)
    
    def save_cropped_image(self, image, original_path):
        # 1. Nombre base + extensión
        original_file_name = os.path.basename(original_path)
        base_name, extension = os.path.splitext(original_file_name)
        new_file_name = f"{base_name}_cropped{extension}"

        try:
            script_path = Path(self.p['fnames'][0]).resolve()

            source_dir = script_path.parent         
            folder_name = f'{source_dir.name}_cropped'            

            target_dir = Path(os.getcwd()) / folder_name   

            target_dir.mkdir(parents=True, exist_ok=True)  

            final_path = target_dir / new_file_name  

            image.save(final_path)

        except Exception as e:
            print(f"An error occurred: {e}")

        print(f"Files saved in folder {final_path}")
        return str(final_path)
    
    def get_cimages_list(self):
        return self.cropped_images_list
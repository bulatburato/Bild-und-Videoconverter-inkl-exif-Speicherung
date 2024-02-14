import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter, JpegImagePlugin, ExifTags
import cv2
import numpy as np
import os
import json
import piexif

class App:
    def __init__(self, root, design_file):
        self.root = root

        # Bild-/Videoauswahl-Button
        self.btn_open = tk.Button(root, text='Bilder/Videos auswählen', command=self.open_files)
        self.btn_open.pack()

        # TextBox für den Dateinamen
        self.filename_entry = tk.Entry(root)
        self.filename_entry.pack()

        # TextBox für den Autor
        self.author_label = tk.Label(root, text="Autor")
        self.author_label.pack()
        self.author_entry = tk.Entry(root)
        self.author_entry.pack()

        # TextBox für das Copyright
        self.copyright_label = tk.Label(root, text="Copyright")
        self.copyright_label.pack()
        self.copyright_entry = tk.Entry(root)
        self.copyright_entry.pack()

        # TextBox für die Software
        self.software_label = tk.Label(root, text="Software")
        self.software_label.pack()
        self.software_entry = tk.Entry(root)
        self.software_entry.pack()

        # ListBox für Auflösungen
        self.listbox = tk.Listbox(root, exportselection=0)
        self.listbox.insert(1, "320x320")
        self.listbox.insert(2, "640x640")
        self.listbox.insert(3, "720x720")
        self.listbox.insert(4, "1080x1080")
        self.listbox.insert(5, "1920x1920")
        self.listbox.insert(6, "2048x2048")
        self.listbox.insert(7, "3840x3840")
        self.listbox.insert(8, "426x240")  # Web
        self.listbox.insert(9, "640x360")  # Wide
        self.listbox.insert(10, "854x480")  # WVGA
        self.listbox.insert(11, "1280x720")  # HD
        self.listbox.insert(12, "1920x1080")  # FHD
        self.listbox.insert(13, "2560x1440")  # QHD
        self.listbox.insert(14, "3840x2160")  # 4K UHD
        self.listbox.pack()

        # ListBox für Filter
        self.filterbox = tk.Listbox(root, exportselection=0)
        self.filterbox.insert(1, "Kein Filter")
        self.filterbox.insert(2, "Schwarz-Weiß")
        self.filterbox.insert(3, "Sepia")
        self.filterbox.pack()

        # Speicherbutton
        self.btn_save = tk.Button(root, text='Speichern', command=self.save_files)
        self.btn_save.pack()

        # PictureBox
        self.picture_box = tk.Label(root)
        self.picture_box.pack()

        # Laden Sie das Design
        self.load_design(design_file)

    def apply_design(self, design):
        for key, value in design.items():
            if key == 'bg':
                self.root.configure(background=value)
            elif key == 'picture_box':
                self.picture_box.configure(background=value)
            elif key == 'listbox':
                self.listbox.configure(background=value)
            elif key == 'filterbox':
                self.filterbox.configure(background=value)
            elif key == 'btn_open':
                self.btn_open.configure(background=value)
            elif key == 'btn_save':
                self.btn_save.configure(background=value)
            elif key == 'btn_save_font':
                self.btn_save.configure(font=(value, 12)) 
            elif key == 'filename_entry_bg':
                self.filename_entry.configure(background=value)
            elif key == 'filename_entry_fg':
                self.filename_entry.configure(foreground=value)
            # Fügen Sie hier weitere Designparameter hinzu

    def load_design(self, design_file):
        with open(design_file, 'r') as f:
            design = json.load(f)
        self.apply_design(design)

    def open_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[('Image Files', '*.png;*.jpg;*.jpeg'), ('Video Files', '*.mp4;*.avi;*.mov')])
        if self.file_paths:
            file_path = self.file_paths[0]
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(file_path)
                photo = ImageTk.PhotoImage(image)
                self.picture_box.config(image=photo)
                self.picture_box.image = photo
            elif file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                # Hier können Sie Code hinzufügen, um ein Vorschaubild des Videos anzuzeigen
                pass

    def save_files(self):
        if self.listbox.curselection():
            resolution = self.listbox.get(self.listbox.curselection())
            width, height = map(int, resolution.split('x'))
        else:
            messagebox.showinfo('Information','Bitte wählen Sie eine Auflösung aus der Liste aus.')
            return

        if self.filterbox.curselection():
            filter_selected = self.filterbox.get(self.filterbox.curselection())
        else:
            messagebox.showinfo('Information','Bitte wählen Sie einen Filter aus der Liste aus.')
            return

        base_filename = self.filename_entry.get()
        if not base_filename:
            messagebox.showinfo('Information','Bitte geben Sie einen Dateinamen ein.')
            return

        # Ordnerauswahl-Dialog
        folder_selected = filedialog.askdirectory()

        for i, file_path in enumerate(self.file_paths, start=1):
            new_filename = f"{base_filename}{i}"
            new_file_path = os.path.join(folder_selected, new_filename + os.path.splitext(file_path)[1])

            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Bearbeiten und Speichern des Bildes mit Pillow
                image = Image.open(file_path)
                image = image.resize((width, height))
                
                # Anwenden des ausgewählten Filters
                if filter_selected == "Schwarz-Weiß":
                    image = image.convert("L")
                elif filter_selected == "Sepia":
                    image = ImageOps.colorize(image.convert("L"), "#3A200D", "#704214")

                from enum import IntEnum

                class Base(IntEnum):
                    Artist = 0x013B
                    Copyright = 0x8298
                    ProcessingSoftware = 0x000B
                # Erstellen Sie ein EXIF-Datenwörterbuch
                exif_data = {
                    "0th": {
                    Base.Artist: self.author_entry.get(),
                    Base.Copyright: self.copyright_entry.get(),
                    Base.ProcessingSoftware: self.software_entry.get()
                }
                }

                # Konvertieren Sie das EXIF-Datenwörterbuch in Bytes
                exif_bytes = piexif.dump(exif_data)
                
              
                # Speichern Sie das Bild mit den EXIF-Daten
                image.save(new_file_path, exif=exif_bytes)

            elif file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                # Bearbeiten und Speichern des Videos mit OpenCV
                cap = cv2.VideoCapture(file_path)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(new_file_path, fourcc, 20.0, (width, height))

                while(cap.isOpened()):
                    ret, frame = cap.read()
                    if ret==True:
                        frame = cv2.resize(frame, (width, height))
                        
                        # Anwenden des ausgewählten Filters
                        if filter_selected == "Schwarz-Weiß":
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        elif filter_selected == "Sepia":
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame = Image.fromarray(frame)
                            frame = ImageOps.colorize(frame.convert("L"), "#FF962E", "#FF5E5E", "#FFFF33")
                            frame = np.array(frame)
                            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                        out.write(frame)
                    else:
                        break

                cap.release()
                out.release()

            # Aktualisieren der PictureBox
            if os.path.splitext(new_file_path)[1] in ['.png', '.jpg', '.jpeg']:
                image = Image.open(new_file_path)
                photo = ImageTk.PhotoImage(image)
                self.picture_box.config(image=photo)
                self.picture_box.image = photo

# Erstellen Sie eine Instanz der App-Klasse
root = tk.Tk()
app = App(root, 'design.json')

# Starten Sie die Tkinter-Schleife
root.mainloop()

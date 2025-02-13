import customtkinter as ctk
import threading
import os
import pandas as pd
from PIL import Image
from fpdf import FPDF
import pyperclip
from youtube_to_text import youtube_a_texto
from procesador_texto import procesar_transcripcion

# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")  # Modo oscuro
ctk.set_default_color_theme("blue")  # Tema de colores

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube a Texto y Traducción")
        self.geometry("700x600")
        self.resizable(False, False)

        # Cargar imágenes de los botones
        self.icon_transcribe = ctk.CTkImage(light_image=Image.open("icons/transcribe.png"), size=(25, 25))
        self.icon_download = ctk.CTkImage(light_image=Image.open("icons/download.png"), size=(25, 25))
        self.icon_copy = ctk.CTkImage(light_image=Image.open("icons/copy.png"), size=(25, 25))

        # Etiqueta de título
        self.label = ctk.CTkLabel(self, text="🎙️ Ingresa la URL del video de YouTube:", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Entrada de URL
        self.url_entry = ctk.CTkEntry(self, width=500, font=("Arial", 14), placeholder_text="Pega aquí la URL...")
        self.url_entry.pack(pady=10)

        # Botón de transcripción con ícono
        self.transcribe_button = ctk.CTkButton(self, text="Transcribir y Traducir", 
                                               image=self.icon_transcribe, 
                                               command=self.iniciar_proceso, 
                                               font=("Arial", 14, "bold"),
                                               fg_color="#3b82f6", hover_color="#2563eb")
        self.transcribe_button.pack(pady=20)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)  # Inicialmente en 0%

        # Caja de texto para mostrar la transcripción
        self.text_box = ctk.CTkTextbox(self, width=650, height=250, font=("Arial", 12), wrap="word", corner_radius=10)
        self.text_box.pack(pady=10)

        # Contenedor de botones de acciones
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        # Botón de copiar texto
        self.copy_button = ctk.CTkButton(self.button_frame, text="Copiar Texto", 
                                         image=self.icon_copy, 
                                         command=self.copiar_al_portapapeles, 
                                         font=("Arial", 12),
                                         fg_color="#6b7280", hover_color="#4b5563")
        self.copy_button.pack(side="left", padx=10)

        # Botón de descargar original
        self.download_original_button = ctk.CTkButton(self.button_frame, text="Descargar TXT", 
                                                      image=self.icon_download, 
                                                      command=self.descargar_original, 
                                                      font=("Arial", 12),
                                                      fg_color="#10b981", hover_color="#059669")
        self.download_original_button.pack(side="left", padx=10)

        # Botón de descargar traducción
        self.download_translation_button = ctk.CTkButton(self.button_frame, text="Descargar Traducción", 
                                                         image=self.icon_download, 
                                                         command=self.descargar_traduccion, 
                                                         font=("Arial", 12),
                                                         fg_color="#f59e0b", hover_color="#d97706")
        self.download_translation_button.pack(side="left", padx=10)

        # Botón de exportar a PDF
        self.export_pdf_button = ctk.CTkButton(self.button_frame, text="Exportar PDF", 
                                               image=self.icon_download, 
                                               command=self.exportar_a_pdf, 
                                               font=("Arial", 12),
                                               fg_color="#ef4444", hover_color="#b91c1c")
        self.export_pdf_button.pack(side="left", padx=10)

        # Botón de exportar a CSV
        self.export_csv_button = ctk.CTkButton(self.button_frame, text="Exportar CSV", 
                                               image=self.icon_download, 
                                               command=self.exportar_a_csv, 
                                               font=("Arial", 12),
                                               fg_color="#3b82f6", hover_color="#2563eb")
        self.export_csv_button.pack(side="left", padx=10)

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12, "italic"), text_color="#94a3b8")
        self.status_label.pack(pady=5)

    def iniciar_proceso(self):
        """Inicia el proceso en un hilo separado para no congelar la interfaz"""
        self.status_label.configure(text="⌛ Procesando... Espere unos segundos.", text_color="#facc15")
        self.progress_bar.set(0.2)  # Avance inicial de la barra
        self.text_box.delete("1.0", "end")  # Limpia la caja de texto
        threading.Thread(target=self.procesar_video, daemon=True).start()

    def procesar_video(self):
        """Ejecuta la transcripción y traducción y actualiza la UI"""
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="⚠️ Introduce una URL válida.", text_color="#f87171")
            return

        self.progress_bar.set(0.5)  # Progreso a la mitad

        # Transcripción
        transcripcion = youtube_a_texto(url)

        self.progress_bar.set(0.8)  # Casi completo

        # Traducción y formateo
        texto_final = procesar_transcripcion()

        # Mostrar en la UI
        self.text_box.insert("1.0", texto_final)
        self.progress_bar.set(1)  # Completo
        self.status_label.configure(text="✅ Proceso completado con éxito.", text_color="#10b981")

    def copiar_al_portapapeles(self):
        """Copia el texto al portapapeles"""
        texto = self.text_box.get("1.0", "end").strip()
        if texto:
            pyperclip.copy(texto)
            self.status_label.configure(text="📋 Texto copiado al portapapeles.", text_color="#10b981")
        else:
            self.status_label.configure(text="⚠️ No hay texto para copiar.", text_color="#f87171")

    def descargar_original(self):
        """Descarga la transcripción original"""
        if os.path.exists("transcripcion.txt"):
            os.startfile("transcripcion.txt")
        else:
            self.status_label.configure(text="⚠️ No se encontró la transcripción original.", text_color="#f87171")

    def descargar_traduccion(self):
        """Descarga la transcripción traducida"""
        if os.path.exists("transcripcion_procesada.txt"):
            os.startfile("transcripcion_procesada.txt")
        else:
            self.status_label.configure(text="⚠️ No se encontró la transcripción traducida.", text_color="#f87171")

    def exportar_a_pdf(self):
        """Exporta la transcripción a PDF"""
        texto = self.text_box.get("1.0", "end").strip()
        if texto:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, texto)
            pdf.output("transcripcion.pdf")
            os.startfile("transcripcion.pdf")
        else:
            self.status_label.configure(text="⚠️ No hay texto para exportar.", text_color="#f87171")

    def exportar_a_csv(self):
        """Exporta la transcripción a CSV"""
        texto = self.text_box.get("1.0", "end").strip()
        if texto:
            df = pd.DataFrame({"Transcripción": [texto]})
            df.to_csv("transcripcion.csv", index=False)
            os.startfile("transcripcion.csv")
        else:
            self.status_label.configure(text="⚠️ No hay texto para exportar.", text_color="#f87171")

if __name__ == "__main__":
    app = App()
    app.mainloop()

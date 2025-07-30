import yt_dlp
import glob
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import sys # Importar sys para manejar errores de stdout/stderr

# --- Funciones de Descarga (Lógica Central) ---

def get_random_cookie_file():
    """
    Selecciona un archivo de cookies aleatorio de la carpeta 'sources/cookies'.
    Retorna la ruta completa al archivo o None si no se encuentran archivos.
    """
    # Construye la ruta absoluta a la carpeta de cookies
    cookies_folder = os.path.join(os.getcwd(), 'sources', 'cookies')
    
    if not os.path.exists(cookies_folder):
        # print(f"Advertencia: La carpeta de cookies no existe en: {cookies_folder}")
        return None

    cookies = glob.glob(os.path.join(cookies_folder, '*.txt'))
    
    return random.choice(cookies) if cookies else None

def descargar_mp3(url, carpeta_destino="downloads", progress_callback=None, status_callback=None, use_browser_cookies=False, browser_name=None):
    """
    Descarga el audio de un video de YouTube en formato MP3.

    Args:
        url (str): La URL del video de YouTube.
        carpeta_destino (str): La carpeta donde se guardará el archivo MP3.
        progress_callback (callable): Función para actualizar la barra de progreso de la GUI.
        status_callback (callable): Función para actualizar los mensajes de estado de la GUI.
        use_browser_cookies (bool): Indica si se deben intentar cargar las cookies desde un navegador.
        browser_name (str): El nombre del navegador a usar si 'use_browser_cookies' es True (ej. 'chrome', 'firefox').

    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario.
    """
    # Asegura que la carpeta de destino exista
    os.makedirs(carpeta_destino, exist_ok=True)

    # Opciones de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best', # Mejor formato de audio disponible
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # Calidad de MP3 (kbps)
        }],
        'outtmpl': os.path.join(carpeta_destino, '%(title)s.%(ext)s'), # Plantilla de nombre de archivo
        'quiet': True,  # Suprime la salida a la consola de yt-dlp, la GUI maneja el estado
        'ffmpeg_location': os.path.join(os.getcwd(), 'sources', 'ffmpeg', 'ffmpeg.exe'), # Ruta absoluta a ffmpeg
        'extract_flat': True, # Para listas de reproducción, solo extrae información de nivel superior (no descarga si es una playlist completa)
                              # Considera cambiar a False si quieres descargar todos los videos de una playlist.
        'sleep_interval': 5,  # Espera mínima entre descargas (para evitar baneos)
        'max_sleep_interval': 15, # Espera máxima
        'retries': 10, # Intentos de reintento para descargas fallidas
        'fragment-retries': 10, # Intentos de reintento para fragmentos
        'http_headers': { # Simula un navegador para evitar bloqueos
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        },
        'progress_hooks': [progress_callback], # Hook para actualizar la GUI con el progreso
    }

    # Lógica para el manejo de cookies
    if use_browser_cookies and browser_name:
        try:
            ydl_opts['cookiesfrombrowser'] = (browser_name,) # yt-dlp espera una tupla
            if status_callback:
                status_callback(f"Intentando usar cookies de {browser_name}...")
        except Exception as e:
            if status_callback:
                status_callback(f"Error al configurar cookies de navegador ({browser_name}): {str(e)}")
            print(f"Error al configurar cookies de navegador ({browser_name}): {str(e)}")
            # Continuar sin cookies del navegador si falla la configuración
            if 'cookiesfrombrowser' in ydl_opts:
                del ydl_opts['cookiesfrombrowser']
            ydl_opts['cookiefile'] = get_random_cookie_file() # Volver al método de archivo si falla
    else:
        # Si no se usan cookies del navegador, intenta cargar de archivo
        cookie_file = get_random_cookie_file()
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file
            if status_callback:
                status_callback(f"Usando archivo de cookies: {os.path.basename(cookie_file)}")
        else:
            if status_callback:
                status_callback("No se encontraron archivos de cookies en 'sources/cookies'. Continuando sin ellos.")

    try:
        if status_callback:
            status_callback("Preparando descarga...")
        
        # Redirigir stdout/stderr de yt_dlp para no interferir con la GUI si 'quiet' no funciona 100%
        # Esto es más un truco para depuración, 'quiet: True' debería ser suficiente.
        # original_stdout = sys.stdout
        # original_stderr = sys.stderr
        # sys.stdout = open(os.devnull, 'w')
        # sys.stderr = open(os.devnull, 'w')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url]) # Pasa la URL como una lista

        if status_callback:
            status_callback("¡Descarga completada con éxito!")
        return True
    except yt_dlp.utils.DownloadError as e:
        # Errores específicos de descarga de yt-dlp
        error_message = f"Error de descarga: {e.exc_info[1].msg if e.exc_info and e.exc_info[1] else str(e)}"
        if status_callback:
            status_callback(error_message)
        print(f"ERROR: {error_message}") # También imprime en consola para depuración
        return False
    except Exception as e:
        # Otros errores inesperados (ej. problemas de ffmpeg, permisos)
        error_message = f"Error inesperado durante el proceso: {str(e)}"
        if status_callback:
            status_callback(error_message)
        print(f"ERROR: {error_message}")
        return False
    # finally:
        # Restaurar stdout/stderr si fueron redirigidos
        # sys.stdout = original_stdout
        # sys.stderr = original_stderr

# --- Interfaz Gráfica de Usuario (GUI) con Tkinter ---

def set_app_icon(window, icon_path=None):
    """
    Cambia el icono de la ventana principal de la aplicación.
    Si icon_path es None, no hace nada.
    """
    if not icon_path:
        return
    if not os.path.exists(icon_path):
        try:
            from tkinter import messagebox
            messagebox.showwarning("Icono no encontrado", f"No se encontró el icono en: {icon_path}\nLa aplicación funcionará sin icono personalizado.")
        except Exception:
            print(f"Advertencia: No se encontró el icono en: {icon_path}")
        return
    try:
        # Para Windows, usar .ico
        window.iconbitmap(icon_path)
    except Exception as e:
        try:
            # Si falla, intentar con PhotoImage (.png)
            img = tk.PhotoImage(file=icon_path)
            window.iconphoto(True, img)
        except Exception as e2:
            try:
                from tkinter import messagebox
                messagebox.showwarning("Error de icono", f"No se pudo establecer el icono personalizado.\nError: {e}\n{e2}")
            except Exception:
                print(f"No se pudo establecer el icono personalizado. Error: {e} {e2}")

# --- Cambiar el icono de la aplicación ---
ICON_PATH = os.path.join(os.getcwd(), "sources", "icon.ico")  # Cambia la ruta si tu icono está en otro lugar

def set_icon_on_root(root):
    set_app_icon(root, ICON_PATH)

class YtMp3DownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Descargador YouTube a MP3")
        master.geometry("650x500") # Tamaño más grande
        master.resizable(False, False)

        # Estilos para widgets ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Marco principal con padding
        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Leyenda de recomendación de navegador ---
        self.recommend_label = ttk.Label(self.main_frame, text="⚠️ Recomendación: funciona mejor si tienes Firefox instalado y abierto.", foreground="#00b300", font=("Segoe UI", 9, "italic"))
        self.recommend_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # --- Sección de URL (ahora multilinea) ---
        self.url_label = ttk.Label(self.main_frame, text="Ingresa una o varias URLs de YouTube (una por línea):")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.url_text = tk.Text(self.main_frame, width=75, height=6, wrap=tk.WORD)
        self.url_text.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 10))

        # --- Sección de Carpeta de Destino ---
        self.folder_label = ttk.Label(self.main_frame, text="Carpeta de destino:")
        self.folder_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.download_folder = tk.StringVar()
        # Establece la carpeta de 'downloads' en el directorio de ejecución del script como predeterminada
        self.download_folder.set(os.path.join(os.getcwd(), "downloads")) 
        
        self.folder_entry = ttk.Entry(self.main_frame, textvariable=self.download_folder, width=50, state='readonly')
        self.folder_entry.grid(row=3, column=0, sticky="we", pady=(0, 10))

        self.browse_button = ttk.Button(self.main_frame, text="Examinar...", command=self.browse_folder)
        self.browse_button.grid(row=3, column=1, sticky=tk.W, padx=(5,0), pady=(0,10))


        # --- Sección de Navegador (sin casilla de cookies) ---
        self.browser_frame = ttk.Frame(self.main_frame)
        self.browser_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        self.browser_label = ttk.Label(self.browser_frame, text="Navegador para cookies:")
        self.browser_label.pack(side=tk.LEFT)

        self.browser_options = ["firefox", "chrome", "edge", "brave", "opera", "safari"]
        self.browser_selected = ttk.Combobox(self.browser_frame, values=self.browser_options, state="readonly", width=12)
        self.browser_selected.set("firefox")  # Valor predeterminado
        self.browser_selected.pack(side=tk.LEFT)


        # --- Botones de Descarga y Cancelar ---
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=(15, 15))
        self.download_button = ttk.Button(self.button_frame, text="Descargar MP3", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        self.cancel_button = ttk.Button(self.button_frame, text="Cancelar", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)


        # --- Barra de Progreso ---
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=450, mode="determinate")
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # --- Área de Mensajes de Estado ---
        # wraplength para que el texto se ajuste si es muy largo
        self.status_label = ttk.Label(self.main_frame, text="Listo para descargar...", wraplength=480, justify=tk.LEFT)
        self.status_label.grid(row=7, column=0, columnspan=2, sticky=('we'))

        # --- Leyenda de recomendación de navegador ---
        self.recommend_label = ttk.Label(self.main_frame, text="⚠️ Recomendación: funciona mejor si tienes Firefox instalado y abierto.", foreground="#00b327", font=("Segoe UI", 9, "italic"))
        self.recommend_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Configurar la expansión de columnas para que el entry de URL y folder se expandan
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0) # El botón de examinar no se expande

    def browse_folder(self):
        """Abre un diálogo para que el usuario seleccione una carpeta de destino."""
        folder_selected = filedialog.askdirectory(initialdir=self.download_folder.get())
        if folder_selected:
            self.download_folder.set(folder_selected)


    def toggle_browser_options(self):
        pass  # Ya no se usa, pero se deja para compatibilidad

    def update_status(self, message):
        """Actualiza el mensaje de estado en la GUI."""
        self.status_label.config(text=message)
        self.master.update_idletasks() # Forzar actualización de la GUI

    def update_progress(self, d):
        """
        Actualiza la barra de progreso basándose en los hooks de progreso de yt-dlp.
        'd' es un diccionario que contiene información sobre el estado de la descarga.
        """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes and total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
                self.progress_bar['value'] = percent
                self.update_status(f"Descargando: {percent:.1f}% de {d.get('_total_bytes_str', 'N/A')} ({d.get('_speed_str', 'N/A')}) ETA: {d.get('_eta_str', 'N/A')}")
            else:
                # Si no hay información de bytes, usar un modo indeterminado o un pequeño paso
                self.progress_bar.step(1) 
                self.update_status(f"Descargando... {d.get('_percent_str', '')} {d.get('_speed_str', '')}")
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.update_status("Procesando audio (esto puede tomar un momento)...")
        elif d['status'] == 'error':
            self.update_status(f"Error durante la descarga: {d.get('error', 'Desconocido')}")
            self.progress_bar['value'] = 0

    def start_download(self):
        """
        Inicia el proceso de descarga para varios links. 
        Ejecuta la descarga en un hilo separado para no bloquear la GUI.
        """
        urls_raw = self.url_text.get("1.0", tk.END)
        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("Entrada Vacía", "Por favor, ingresa al menos una URL de YouTube.")
            return

        # Deshabilitar controles de la GUI durante la descarga para evitar interacciones no deseadas
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.DISABLED)
        self.url_text.config(state=tk.DISABLED)
        self.browser_selected.config(state=tk.DISABLED)

        self.progress_bar['value'] = 0 # Reiniciar barra de progreso
        self.update_status("Iniciando descarga...")

        # El navegador siempre se elige del combobox
        browser = self.browser_selected.get()

        # Crear y ejecutar un hilo para la descarga múltiple
        self._cancel_requested = False
        self._download_thread = threading.Thread(
            target=self._run_downloads_thread, 
            args=(urls, browser)
        )
        self._download_thread.start()

    def _run_downloads_thread(self, urls, browser_name):
        """Función que se ejecuta en el hilo separado para descargar varios links."""
        target_folder = self.download_folder.get()
        all_success = True
        for idx, url in enumerate(urls, 1):
            if getattr(self, '_cancel_requested', False):
                break
            self.master.after(0, self.update_status, f"Descargando {idx} de {len(urls)}...")
            success = descargar_mp3(
                url, 
                target_folder, 
                self.update_progress, 
                self.update_status, 
                True,  # Siempre usar cookies de navegador
                browser_name
            )
            if not success:
                all_success = False
        # Cuando todas las descargas terminan o se cancela, actualizar la GUI en el hilo principal
        self.master.after(0, self._download_complete_ui_update, all_success)

    def cancel_download(self):
        """Marca la descarga como cancelada (solo detiene el bucle, no aborta yt-dlp activo)."""
        self._cancel_requested = True
        self.update_status("Descarga cancelada por el usuario. Espera a que termine la descarga en curso...")

    def _download_complete_ui_update(self, success):
        """
        Actualiza el estado de la GUI una vez que la(s) descarga(s) ha(n) terminado (o fallado).
        Se ejecuta en el hilo principal de Tkinter.
        """
        # Volver a habilitar los controles de la GUI
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.NORMAL)
        self.url_text.config(state=tk.NORMAL)
        self.browser_selected.config(state="readonly")
        self.toggle_browser_options() # Reestablece el estado correcto del combobox del navegador

        # Mostrar mensaje de éxito o error al usuario
        if success:
            messagebox.showinfo("Descarga Exitosa", "¡Todos los MP3 se han descargado correctamente!")
        else:
            messagebox.showerror("Error de Descarga", "Ha ocurrido un error durante la descarga de uno o más links. Consulta la ventana de estado para más detalles.")
        
        self.update_status("Listo para descargar...") # Restablece el mensaje de estado final

# --- Punto de entrada de la aplicación ---
if __name__ == "__main__":
    root = tk.Tk()
    set_icon_on_root(root)  # Asegura que el icono se aplique antes de mostrar la ventana
    app = YtMp3DownloaderApp(root)
    root.mainloop()
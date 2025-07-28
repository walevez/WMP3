# WMP3: Descargador de YouTube a MP3 con Interfaz Gráfica

WMP3 es una aplicación de escritorio para Windows que permite descargar el audio de videos de YouTube en formato MP3 de manera sencilla y rápida, utilizando una interfaz gráfica amigable basada en Tkinter. Soporta múltiples enlaces, descarga por lotes y el uso de cookies de navegador para evitar bloqueos y mejorar la compatibilidad.

## Características principales

- Descarga de audio en formato MP3 desde YouTube.
- Interfaz gráfica intuitiva (Tkinter).
- Soporte para múltiples enlaces (descarga por lotes).
- Selección de carpeta de destino.
- Uso de cookies de navegador (recomendado Firefox) para evitar restricciones.
- Barra de progreso y mensajes de estado en tiempo real.
- Integración con ffmpeg para conversión de audio.

## Requisitos

- **Python 3.8+**
- **yt-dlp**
- **ffmpeg** (incluido en `sources/ffmpeg/`)
- **Tkinter** (incluido en la mayoría de instalaciones de Python)

## Instalación

1. Clona este repositorio o descarga el código fuente.
2. Instala las dependencias de Python:

   ```bash
   pip install -r requirements.txt
   ```

3. Asegúrate de que los ejecutables de ffmpeg estén en `sources/ffmpeg/` (ya incluidos en el repo).
4. (Opcional) Coloca archivos de cookies en `sources/cookies/` para mejorar la compatibilidad con videos restringidos.

## Uso

1. Ejecuta la aplicación:

   ```bash
   python main.py
   ```

2. Ingresa una o varias URLs de YouTube (una por línea).
3. Selecciona la carpeta de destino para los archivos MP3.
4. Elige el navegador para extraer cookies (Firefox recomendado y abierto).
5. Haz clic en **Descargar MP3** y espera a que finalice el proceso.

## Estructura del proyecto

```
WMP3/
├── main.py
├── requirements.txt
├── README.md
├── downloads/           # Carpeta de descargas
├── logs/                # (opcional) Carpeta de logs
├── sources/
│   ├── ffmpeg/          # ffmpeg.exe, ffplay.exe, ffprobe.exe
│   └── cookies/         # Archivos de cookies .txt (opcional)
```

## Notas y recomendaciones

- Para mejores resultados, mantén Firefox abierto y logueado en YouTube.
- Si tienes problemas con videos restringidos, usa cookies de navegador o coloca archivos de cookies en `sources/cookies/`.
- El programa está pensado para uso personal y educativo.

## Licencia

MIT License. Consulta el archivo LICENSE para más detalles.

## Créditos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)
- Interfaz gráfica: Tkinter

---
¡Disfruta descargando tu música favorita de YouTube de forma sencilla y segura!

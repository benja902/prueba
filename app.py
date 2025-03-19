# app.py (Aplicación principal)
import os
import yt_dlp
from flask import Flask, render_template, request, send_file, redirect, url_for
import time

app = Flask(__name__)

# Ruta para almacenar las descargas
UPLOAD_FOLDER = 'descargas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def descargar_audio(url, output_folder=UPLOAD_FOLDER):
    try:
        # Configuración de yt-dlp para descargar solo el audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'cookiefile': 'cookie.txt',  # Agregar cookies

        }
        
        # Descargar audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'audio')
            # Sanitizar el título para el nombre del archivo
            video_title = "".join(c for c in video_title if c.isalnum() or c in ' -_').strip()
            file_path = os.path.join(output_folder, f"{video_title}.mp3")
            return file_path, video_title
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    archivo = None
    nombre_archivo = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            file_path, result = descargar_audio(url)
            if file_path:
                # Obtener solo el nombre del archivo
                nombre_archivo = os.path.basename(file_path)
                archivo = nombre_archivo
                mensaje = f"¡Descarga completada! Archivo: {nombre_archivo}"
            else:
                mensaje = f"Error: {result}"
    
    return render_template('index.html', mensaje=mensaje, archivo=archivo)

@app.route('/descargas/<filename>')
def descargar_archivo(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
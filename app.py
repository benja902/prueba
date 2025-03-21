import os
import re
import yt_dlp
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = "descargas"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def limpiar_nombre(nombre):
    """Elimina caracteres especiales y normaliza el nombre del archivo."""
    nombre = re.sub(r'[^\w\s-]', '', nombre)  # Elimina caracteres especiales
    nombre = re.sub(r'\s+', '_', nombre)  # Reemplaza espacios por "_"
    return nombre.strip("_")  # Elimina "_" adicionales

def descargar_audio(url):
    """Descarga el audio y renombra correctamente."""
    try:
        output_template = os.path.join(UPLOAD_FOLDER, "%(title)s.%(ext)s")

        # Leer las cookies desde la variable de entorno
        cookie_data = os.environ.get('YOUTUBE_COOKIES')

        # Si existen cookies, guardarlas temporalmente en un archivo
        cookie_file = None
        if cookie_data:
            cookie_file = "cookie_tmp.txt"
            with open(cookie_file, "w") as f:
                f.write(cookie_data)
            print("✅ Se creó el archivo de cookies temporalmente.")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Si hay un archivo de cookies, agregarlo a yt-dlp
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_path = info_dict['requested_downloads'][0]['filepath']

            video_title = info_dict.get('title', 'audio')
            video_title = limpiar_nombre(video_title)
            new_file_path = os.path.join(UPLOAD_FOLDER, f"{video_title}.mp3")

            os.replace(downloaded_path, new_file_path)

            # Eliminar el archivo temporal de cookies después de la descarga
            if cookie_file:
                os.remove(cookie_file)
                print("✅ Archivo de cookies temporal eliminado.")

            return new_file_path, video_title

    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje = None
    archivo = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            file_path, result = descargar_audio(url)
            if file_path:
                archivo = os.path.basename(file_path)
                mensaje = f"¡Descarga completada! Archivo: {archivo}"
            else:
                mensaje = f"Error: {result}"
    
    return render_template('index.html', mensaje=mensaje, archivo=archivo)

@app.route('/descargas/<path:filename>')
def descargar_archivo(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Archivo no encontrado", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

import os
import subprocess
from datetime import datetime
from flask import Flask, render_template, send_file, request, redirect, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Конфигурация
CLIPS_FOLDER = r'C:\Users\Кирилл\Downloads\clips'
THUMBNAILS_FOLDER = os.path.join(app.static_folder, 'thumbnails')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)
os.makedirs(CLIPS_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_thumbnail(video_path):
    """Создает превью в формате WebP"""
    thumbnail_name = os.path.splitext(os.path.basename(video_path))[0] + '.webp'
    thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_name)

    if not os.path.exists(thumbnail_path):
        command = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:01',
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            '-q:v', '70',
            thumbnail_path
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"Ошибка FFmpeg: {e}")
            return None
    return thumbnail_name


@app.route('/')
def index():
    search_query = request.args.get('q', '')
    view_mode = request.cookies.get('view_mode', 'grid')
    clips = []

    for filename in os.listdir(CLIPS_FOLDER):
        if allowed_file(filename):
            if search_query.lower() in filename.lower():
                clip_path = os.path.join(CLIPS_FOLDER, filename)
                thumb_name = generate_thumbnail(clip_path)

                if thumb_name:
                    clips.append({
                        'filename': filename,
                        'thumbnail': thumb_name,
                        'created': datetime.fromtimestamp(os.path.getctime(clip_path)).strftime('%Y-%m-%d %H:%M'),
                        'size': os.path.getsize(clip_path)
                    })

    favorites = request.cookies.get('favorites', '').split(',')
    return render_template('index.html',
                           clips=clips,
                           favorites=favorites,
                           search_query=search_query,
                           view_mode=view_mode)


@app.route('/favourites')
def favourites():
    view_mode = request.cookies.get('view_mode', 'grid')
    favorites = request.cookies.get('favorites', '').split(',')
    clips = [clip for clip in get_clips() if clip['filename'] in favorites]
    return render_template('favourites.html', clips=clips, view_mode=view_mode)


@app.route('/video/<filename>')
def video(filename):
    file_path = os.path.join(CLIPS_FOLDER, filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    if not allowed_file(filename):
        return "Invalid file type", 400

    return send_file(file_path)


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    safe_dir = os.path.abspath(CLIPS_FOLDER)
    file_path = os.path.join(safe_dir, filename)

    if not os.path.commonprefix([file_path, safe_dir]) == safe_dir:
        return "Недопустимый путь", 403

    if os.path.exists(file_path):
        os.remove(file_path)
        thumb_path = os.path.join(THUMBNAILS_FOLDER, filename.replace('.mp4', '.webp'))
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    return redirect('/')


@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    new_name = request.form.get('new_name')
    if not new_name:
        return "Новое имя не указано", 400

    safe_dir = os.path.abspath(CLIPS_FOLDER)
    old_path = os.path.join(safe_dir, filename)
    new_path = os.path.join(safe_dir, secure_filename(new_name + '.mp4'))

    if not os.path.commonprefix([old_path, safe_dir]) == safe_dir:
        return "Недопустимый путь", 403

    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        old_thumb = os.path.join(THUMBNAILS_FOLDER, filename.replace('.mp4', '.webp'))
        new_thumb = os.path.join(THUMBNAILS_FOLDER, new_name + '.webp')
        if os.path.exists(old_thumb):
            os.rename(old_thumb, new_thumb)

    return redirect('/')


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/favorite', methods=['POST'])
def toggle_favorite():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'status': 'error', 'message': 'Filename is required'}), 400

    favorites = request.cookies.get('favorites', '').split(',')
    favorites = [f for f in favorites if f]  # Убираем пустые значения

    if filename in favorites:
        favorites.remove(filename)
        status = 'removed'
    else:
        favorites.append(filename)
        status = 'added'

    response = jsonify({
        'status': 'success',
        'action': status,
        'filename': filename,
        'favorites': favorites
    })

    response.set_cookie('favorites', ','.join(favorites), max_age=30*24*60*60)
    return response

@app.route('/view_mode', methods=['POST'])
def change_view_mode():
    mode = request.json.get('mode')
    if mode not in ['grid', 'list']:
        return jsonify({'status': 'error'}), 400

    response = jsonify({'status': 'success'})
    response.set_cookie('view_mode', mode, max_age=30*24*60*60)
    return response


def get_clips(search_query=''):
    clips = []
    for filename in os.listdir(CLIPS_FOLDER):
        if allowed_file(filename):
            if search_query.lower() in filename.lower():
                clip_path = os.path.join(CLIPS_FOLDER, filename)
                clips.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(os.path.getctime(clip_path)).strftime('%Y-%m-%d %H:%M'),
                    'size': os.path.getsize(clip_path)
                })
    return sorted(clips, key=lambda x: x['created'], reverse=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

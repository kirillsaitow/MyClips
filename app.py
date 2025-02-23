from flask import Flask, render_template, send_file, request, redirect
import os
import subprocess

from werkzeug.utils import secure_filename

app = Flask(__name__)
CLIPS_FOLDER = r"E:\clips\Marvel Rivals"
THUMBNAILS_FOLDER = os.path.join(app.static_folder, 'thumbnails')

# Создаем папку для превью при запуске
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)


def generate_thumbnail(video_path):
    """Создает превью для видео с помощью FFmpeg"""
    thumbnail_name = os.path.splitext(os.path.basename(video_path))[0] + '.jpg'
    thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_name)

    # Команда FFmpeg: взять кадр на 1-й секунде видео
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', '00:00:01',  # Время для кадра (1 секунда)
        '-vframes', '1',  # Количество кадров (1)
        '-q:v', '2',  # Качество превью (1-31, где 1 — лучшее)
        thumbnail_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return thumbnail_name
    except Exception as e:
        print(f"Ошибка FFmpeg: {e}")
        return None


@app.route('/')
def index():
    clips = []
    for filename in os.listdir(CLIPS_FOLDER):
        if filename.lower().endswith(('.mp4', '.avi', '.mov')):
            video_path = os.path.join(CLIPS_FOLDER, filename)
            thumb_name = os.path.splitext(filename)[0] + '.jpg'

            # Если превью нет - создаем
            if not os.path.exists(os.path.join(THUMBNAILS_FOLDER, thumb_name)):
                generate_thumbnail(video_path)

            clips.append(filename)

    return render_template('index.html', clips=clips)


@app.route('/video/<filename>')
def video(filename):
    return send_file(os.path.join(CLIPS_FOLDER, filename))


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Проверка безопасности
    safe_dir = os.path.abspath(CLIPS_FOLDER)
    file_path = os.path.join(safe_dir, filename)

    if not os.path.commonprefix([file_path, safe_dir]) == safe_dir:
        return "Недопустимый путь", 403

    # Удаление видео и превью
    if os.path.exists(file_path):
        os.remove(file_path)
        thumb_path = os.path.join(THUMBNAILS_FOLDER, filename.replace('.mp4', '.jpg'))
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

    return redirect('/')


@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    new_name = request.form.get('new_name')
    if not new_name:
        return "Новое имя не указано", 400

    # Проверка безопасности
    safe_dir = os.path.abspath(CLIPS_FOLDER)
    old_path = os.path.join(safe_dir, filename)
    new_path = os.path.join(safe_dir, secure_filename(new_name + '.mp4'))

    if not os.path.commonprefix([old_path, safe_dir]) == safe_dir:
        return "Недопустимый путь", 403

    # Переименование видео и превью
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        old_thumb = os.path.join(THUMBNAILS_FOLDER, filename.replace('.mp4', '.jpg'))
        new_thumb = os.path.join(THUMBNAILS_FOLDER, new_name + '.jpg')
        if os.path.exists(old_thumb):
            os.rename(old_thumb, new_thumb)

    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
import os

import cv2
from flask import Flask, render_template, send_file

app = Flask(__name__)
CLIPS_FOLDER = r"C:\Users\Кирилл\Downloads\clips"
THUMBNAILS_FOLDER = os.path.join(app.static_folder, 'thumbnails')

# Создаем папку для превью при запуске
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)


def generate_thumbnail(video_path):
    try:
        vidcap = cv2.VideoCapture(video_path)
        success, image = vidcap.read()
        if success:
            thumbnail_name = os.path.splitext(os.path.basename(video_path))[0] + '.jpg'
            thumbnail_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_name)
            cv2.imwrite(thumbnail_path, image)
            return thumbnail_name
    except Exception as e:
        print(f"Ошибка OpenCV: {e}")
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

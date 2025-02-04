from flask import Flask, render_template, send_file
import os

app = Flask(__name__)
CLIPS_FOLDER = 'C:/GameClips'  # Путь к вашим клипам

@app.route('/')
def index():
    # Получаем список файлов из папки с клипами
    clips = os.listdir(CLIPS_FOLDER)
    return render_template('index.html', clips=clips)

@app.route('/video/<filename>')
def video(filename):
    # Отправляем видеофайл
    return send_file(os.path.join(CLIPS_FOLDER, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

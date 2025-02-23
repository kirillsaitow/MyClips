import os
import subprocess

# Путь к папке с видео
INPUT_FOLDER = r"E:\clips\Marvel Rivals"
# Путь к папке для сжатых видео
OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, "compressed")

# Создаем папку для сжатых видео, если её нет
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def compress_video(input_path, output_path):
    """Сжимает видео с помощью FFmpeg"""
    command = [
        'ffmpeg',
        '-i', input_path,  # Входной файл
        '-vf', 'scale=1920:-1',  # Масштабирование до ширины 1920px (высота автоматически)
        '-c:v', 'libx264',  # Кодек видео (H.264)
        '-crf', '28',  # Качество (чем меньше, тем лучше, 23–28 — оптимально)
        '-preset', 'medium',  # Скорость сжатия (медленнее = лучше сжатие)
        '-c:a', 'aac',  # Кодек аудио (AAC)
        '-b:a', '128k',  # Битрейт аудио (128 кбит/с)
        output_path  # Выходной файл
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Сжато: {os.path.basename(input_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сжатии {input_path}: {e}")


def compress_all_videos():
    """Сжимает все видео в папке"""
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            compress_video(input_path, output_path)


if __name__ == '__main__':
    print("Начало сжатия видео...")
    compress_all_videos()
    print("Сжатие завершено!")
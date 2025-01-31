# main.py

from datetime import datetime
from tqdm import tqdm
from api.skorozvon_api import get_skorozvon_access_token, get_calls
from api.gigachat_api import get_gigachat_token, analyze_transcript_with_gigachat
from utils.file_utils import save_to_json, create_directory
from utils.audio_utils import convert_mp3_to_wav, transcribe_audio
from utils.filter_utils import filter_calls
import requests
import os
import urllib3

# Отключение предупреждений о небезопасных HTTPS-запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'

# Создание папок для данных
mp3_folder = "data/mp3_files"
wav_folder = "data/wav_files"
create_directory(mp3_folder)
create_directory(wav_folder)

# Получение токена Skorozvon
access_token = get_skorozvon_access_token()

# Получение списка звонков
start_date = datetime(2025, 1, 30, 17, 0, 0)
end_date = datetime(2025, 1, 30, 18, 0, 0)
all_calls = get_calls(access_token, start_date, end_date)

# Сохранение звонков в JSON
save_to_json(all_calls, "data/calls.json")

# Получение токена GigaChat
gigachat_token = get_gigachat_token()

# Обработка звонков
transcripts_and_analysis = []
for call in tqdm(all_calls, desc="Обработка звонков", unit="звонок", total=len(all_calls)):
    call_id = call.get("id")
    recording_url = call.get("recording_url")

    if recording_url:
        # Скачивание записи звонка
        audio_response = requests.get(f"{recording_url}?access_token={access_token}")
        if audio_response.status_code == 200:
            mp3_path = os.path.join(mp3_folder, f"call_{call_id}.mp3")
            with open(mp3_path, "wb") as audio_file:
                audio_file.write(audio_response.content)

            if os.path.getsize(mp3_path) == 0:
                print(f"Файл {mp3_path} пустой или поврежден. Пропуск.")
                continue

            try:
                # Конвертация в WAV
                wav_path = os.path.join(wav_folder, f"call_{call_id}.wav")
                convert_mp3_to_wav(mp3_path, wav_path)

                # Транскрибация
                transcript = transcribe_audio(wav_path)

                # Анализ транскрипции
                analysis = analyze_transcript_with_gigachat(transcript, gigachat_token)

                transcripts_and_analysis.append({
                    "call_id": call_id,
                    "transcript": transcript,
                    "analysis": analysis
                })
            except Exception as e:
                print(f"Ошибка при обработке файла {mp3_path}: {e}")
        else:
            print(f"Ошибка при скачивании записи звонка {call_id}")

# Сохранение транскрипций и анализа
save_to_json(transcripts_and_analysis, "data/transcripts_and_analyze.json")

# Фильтрация звонков
filters = {
    "start_date": datetime(2025, 1, 30, 17, 30, 0),
    "end_date": datetime(2025, 1, 30, 18, 0, 0),
    "user_id": 135602,
    "phone": "+79057551539",
    "has_recording": True,
    "direction": "out",
}

filtered_calls = filter_calls(all_calls, filters)
save_to_json(filtered_calls, "data/filtered_calls_with_recording.json")
print(f"Найдено звонков с заданной фильтрацией: {len(filtered_calls)}")
from pydub import AudioSegment
import speech_recognition as sr
import requests
import json
import os
from datetime import datetime
import time
import urllib3
from tqdm import tqdm

# Отключение предупреждений о небезопасных HTTPS-запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'

# Данные для аунтификации
email = "serga29121995@mail.ru"
api_key = "597e34e84726d32ed63d5f810532b24a69292ada57e335c29e04c9f987ba8e3e"
client_id = "29055bf486467ffb99159edf3c21881d8ec4349ee1eb61c0b172364bbcc623b7"
client_secret = "172f48c27f7eb1c2322526b8f92d5b25dcc9cbc8785f137a428795b3f4a4cb2a"

# URL для получения токена
token_url = "https://api.skorozvon.ru/oauth/token"

response = requests.post(
    token_url,
    data = {
        "grant_type": "password",
        "username": email,
        "api_key": api_key,
        "client_id": client_id,
        "client_secret": client_secret,
    },
)

# Проверка ответа
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Acces Token получен.")
else:
    print("Ошибка при получении токена:", response.status_code, response.text)
    exit()



# URL для получения списка звонков
calls_url = "https://api.skorozvon.ru/api/v2/calls"

start_date = datetime(2025, 1, 30, 17, 0, 0)  # Начальная дата
end_date = datetime(2025, 1, 30, 18, 0, 0)  # Конечная дата

start_time = int(time.mktime(start_date.timetuple()))
end_time = int(time.mktime(end_date.timetuple()))

# Параметры запроса
params = {
    "start_time": start_time,
    "end_time": end_time,
    "page": 1, 
    "length": 100,
    } # Промежуток по времени звонков (01.01.2024 - 29.01.)

headers = {
    "Authorization": f"Bearer {access_token}",
}

# Список для хранения всех звонков
all_calls = []

# Постраничная загрузка звонков
while True:
    # Запрос на получение списка звонков
    response = requests.get(calls_url, headers=headers, params=params)

    # Проверка ответа
    if response.status_code == 200:
        calls = response.json().get("data", [])
        all_calls.extend(calls)
        print(f"Загрузка звонков: {len(calls)} (страница {params['page']})")
        
        # Если количество звонков меньше запрошенного, значит, это последняя страница
        if len(calls) < params["length"]:
            break

        #Переход к следующей странице
        params["page"] += 1
    else:
        print("Ошибка при получении списка звонков:", response.status_code, response.text)
        break

 #Запись звонков в JSON-файл
with open("calls.json", "w", encoding="utf-8") as file:
    json.dump(all_calls, file, ensure_ascii=False, indent=4)
print(f"Всего загружено звонков: {len(all_calls)}. Звонки успешно записаны в calls.json")



# Создание и проверка папок для сохранения файлов
mp3_folder = "mp3_files"
os.makedirs(mp3_folder, exist_ok=True)
wav_folder = "wav_files"
os.makedirs(wav_folder, exist_ok=True)


#Функция для транскрибации записи звонков от GOOGLE
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Речь не распознана"
    except sr.RequestError:
        return "Ошибка сервиса распознавания речи"

#Функция для получения токена GigaChat
def get_gigachat_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': 'd0f8c263-c0fb-41a3-8091-7ae1ef577fab',
        'Authorization': 'Basic NDdlNDAwNGQtNWE3YS00NjQ3LTgxMjMtMjU3MWQ2NTk1ZTE5OjY2MDc4ZTllLTc3ODEtNDIwZC05ZjYxLTNhNzNiODVkNmViMg=='
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Ошибка при получении токена GigaChat:", response.status_code, response.text)
        return None



# Функция для анализа транскрипции с помощью GigaChat
def analyze_transcript_with_gigachat(transcript, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": f"Проанализируй следующий текст звонка и дай отчет: правильно ли отработал менеджер все возражения, проговорил ли верно скрипт и т.д.\n\n{transcript}"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Анализ не удался")
    else:
        print("Ошибка при анализе транскрипции:", response.status_code, response.text)
        return "Ошибка при анализе транскрипции"



gigachat_token = get_gigachat_token()
if not gigachat_token:
    print("Не удалось получить токен GigaChat. Анализ транскрипций невозможен.")
    exit()



transcripts_and_analysis = []

for call in tqdm(all_calls, desc="Обработка звонков", unit="звонок", total=len(all_calls)):
    call_id = call.get("id")
    recording_url = call.get("recording_url")

    if recording_url:
        #Скачивание записи звонка
        audio_response = requests.get(f"{recording_url}?access_token={access_token}")
        if audio_response.status_code == 200:
            # Сохранение MP3-файла в папку mp3_files
            mp3_path = os.path.join(mp3_folder, f"call_{call_id}.mp3")
            with open(mp3_path, "wb") as audio_file:
                audio_file.write(audio_response.content)

            if os.path.getsize(mp3_path) == 0:
                print(f"Файл {mp3_path} пустой или поврежден. Пропуск.")
                continue
            
            try:
                #Конвертация в WAV для транскрибации
                audio = AudioSegment.from_mp3(mp3_path)
                wav_path = os.path.join(wav_folder, f"call_{call_id}.wav")
                audio.export(wav_path, format="wav")

                #Транскрибация
                transcript = transcribe_audio(wav_path)
                # Анализ транскрипции с помощью GigaChat
                analysis = analyze_transcript_with_gigachat(transcript, gigachat_token)

                transcripts_and_analysis.append({
                    "call_id": call_id,
                    "transcript": transcript,
                    "analysis": analysis
                })
                #print(f"Транскрипция и анализ звонка {call_id} завершины.")
            except Exception as e:
                print(f"Ошибка при обработке файла {mp3_path}") #: {e}
        else:
            print(f"Ошибка при скачивании записи звонка {call_id}")
    #else:
        #print(f"Для звонка {call_id} нет записи")

with open("transcripts_and_analyze.json", "w", encoding="utf-8") as file:
    json.dump(transcripts_and_analysis, file, ensure_ascii=False, indent=4)
    print("Транскрипции с анализов сохранены в файл transcripts_and_analyze.json")


# Функция для фильтрации звонков.
def filter_calls(calls, filters):
    """
    Фильтрует звонки по заданным параметрам.
    :param calls: Список звонков.
    :param filters: Словарь с параметрами фильтрации.
    :return: Отфильтрованный список звонков.
    """
    filtered_calls = []

    for call in calls:
        # Фильтрация по дате
        if "start_date" in filters and "end_date" in filters:
            call_time = datetime.strptime(call["started_at"]["utc"], "%Y-%m-%d %H:%M:%S %Z")
            if not (filters["start_date"] <= call_time <= filters["end_date"]):
                continue

        # Фильтрация по менеджеру (user_id или имя)
        if "user_id" in filters:
            if call.get("user", {}).get("id") != filters["user_id"]:
                continue
        if "user_name" in filters:
            if filters["user_name"].lower() not in call.get("user", {}).get("name", "").lower():
                continue

        # Фильтрация по клиенту (номер телефона или lead_id)
        if "phone" in filters:
            if call.get("phone") != filters["phone"]:
                continue
        if "lead_id" in filters:
            if call.get("lead_id") != filters["lead_id"]:
                continue

        # Фильтрация по направлению звонка (входящий/исходящий)
        if "direction" in filters:
            if call.get("direction") != filters["direction"]:
                continue

        # Фильтрация по типу звонка (входящий/исходящий)
        if "call_type" in filters:
            if call.get("call_type") != filters["call_type"]:
                continue

        # Фильтрация по наличию записи (recording_url)
        if "has_recording" in filters:
            if filters["has_recording"] and not call.get("recording_url"):
                continue  # Пропускаем звонки без записи, если нужны только с записью
            if not filters["has_recording"] and call.get("recording_url"):
                continue  # Пропускаем звонки с записью, если нужны только без записи

        # Если все условия фильтрации выполнены, добавляем звонок в результат
        filtered_calls.append(call)

    return filtered_calls

filters = {
    "start_date": datetime(2025, 1, 30, 17, 30, 0),
    "end_date": datetime(2025, 1, 30, 18, 0, 0),
    "user_id": 135602,       # Звонки конкретного менеджера
    "phone": "+79057551539",
    "has_recording": True,   # Только звонки с записью
    "direction": "out",      # Только исходящие звонки
}

filtered_calls = filter_calls(all_calls, filters)
print(f"Найдено звонков с заданной фильтрацией: {len(filtered_calls)}")

with open("filtered_calls_with_recording.json", "w", encoding="utf-8") as file:
    json.dump(filtered_calls, file, ensure_ascii=False, indent=4)
print("Отфильтрованные звонки сохранены в файл filtered_calls_with_recording.json")
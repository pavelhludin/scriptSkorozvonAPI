# api/gigachat_api.py

import requests
from config import GIGACHAT_AUTH_URL, GIGACHAT_API_URL, GIGACHAT_AUTH_HEADERS

def get_gigachat_token():
    """Получает access token для API GigaChat."""
    payload = {'scope': 'GIGACHAT_API_PERS'}
    response = requests.post(GIGACHAT_AUTH_URL, headers=GIGACHAT_AUTH_HEADERS, data=payload, verify=False)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Ошибка при получении токена GigaChat: {response.status_code}, {response.text}")

def analyze_transcript_with_gigachat(transcript, access_token):
    """Анализирует транскрипцию с помощью GigaChat."""
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

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Анализ не удался")
    else:
        raise Exception(f"Ошибка при анализе транскрипции: {response.status_code}, {response.text}")
# api/skorozvon_api.py

import requests
from datetime import datetime
import time
from config import SKOROZVON_TOKEN_URL, SKOROZVON_CALLS_URL, SKOROZVON_EMAIL, SKOROZVON_API_KEY, SKOROZVON_CLIENT_ID, SKOROZVON_CLIENT_SECRET

def get_skorozvon_access_token():
    """Получает access token для API Skorozvon."""
    response = requests.post(
        SKOROZVON_TOKEN_URL,
        data={
            "grant_type": "password",
            "username": SKOROZVON_EMAIL,
            "api_key": SKOROZVON_API_KEY,
            "client_id": SKOROZVON_CLIENT_ID,
            "client_secret": SKOROZVON_CLIENT_SECRET,
        },
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Ошибка при получении токена: {response.status_code}, {response.text}")

def get_calls(access_token, start_date, end_date):
    """Получает список звонков за указанный период."""
    start_time = int(time.mktime(start_date.timetuple()))
    end_time = int(time.mktime(end_date.timetuple()))

    params = {
        "start_time": start_time,
        "end_time": end_time,
        "page": 1,
        "length": 100,
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    all_calls = []
    while True:
        response = requests.get(SKOROZVON_CALLS_URL, headers=headers, params=params)
        if response.status_code == 200:
            calls = response.json().get("data", [])
            all_calls.extend(calls)
            if len(calls) < params["length"]:
                break
            params["page"] += 1
        else:
            raise Exception(f"Ошибка при получении списка звонков: {response.status_code}, {response.text}")

    return all_calls
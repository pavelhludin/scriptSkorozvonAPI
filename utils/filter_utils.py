# utils/filter_utils.py

from datetime import datetime

def filter_calls(calls, filters):
    """Фильтрует звонки по заданным параметрам."""
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
                continue
            if not filters["has_recording"] and call.get("recording_url"):
                continue

        filtered_calls.append(call)

    return filtered_calls
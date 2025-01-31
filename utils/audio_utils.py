# utils/audio_utils.py

from pydub import AudioSegment
import speech_recognition as sr

def convert_mp3_to_wav(mp3_path, wav_path):
    """Конвертирует MP3 в WAV."""
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")

def transcribe_audio(wav_path):
    """Транскрибирует аудиофайл."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="ru-RU")
    except sr.UnknownValueError:
        return "Речь не распознана"
    except sr.RequestError:
        return "Ошибка сервиса распознавания речи"
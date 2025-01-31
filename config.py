# config.py

# Данные для аутентификации в Skorozvon
SKOROZVON_EMAIL = "serga29121995@mail.ru"
SKOROZVON_API_KEY = "597e34e84726d32ed63d5f810532b24a69292ada57e335c29e04c9f987ba8e3e"
SKOROZVON_CLIENT_ID = "29055bf486467ffb99159edf3c21881d8ec4349ee1eb61c0b172364bbcc623b7"
SKOROZVON_CLIENT_SECRET = "172f48c27f7eb1c2322526b8f92d5b25dcc9cbc8785f137a428795b3f4a4cb2a"

# URL для API Skorozvon
SKOROZVON_TOKEN_URL = "https://api.skorozvon.ru/oauth/token"
SKOROZVON_CALLS_URL = "https://api.skorozvon.ru/api/v2/calls"

# Данные для аутентификации в GigaChat
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_AUTH_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': 'd0f8c263-c0fb-41a3-8091-7ae1ef577fab',
    'Authorization': 'Basic NDdlNDAwNGQtNWE3YS00NjQ3LTgxMjMtMjU3MWQ2NTk1ZTE5OjY2MDc4ZTllLTc3ODEtNDIwZC05ZjYxLTNhNzNiODVkNmViMg=='
}
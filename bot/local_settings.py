import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-xp+fdpuqonq8jq)sdsadhhp-2tb+kc+211=fhdf)qvl_sdfdfs!hs&'

DEBUG = True

WEBHOOK_URL_HOST = "<IP or DOMEN>"
WEBHOOK_URL_PATH = "v47dq-2ysd-hdr13-7w8a"

ALLOWED_HOSTS = [WEBHOOK_URL_HOST, '127.0.0.1', "localhost"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

#Telegram Bot settings
BOT_TOKEN = "<TELEGRAM_BOT_TOKEN>"
SUPPORT_LINK = "@ExampleLink"

#https://microsoft-computer-vision3.p.rapidapi.com/ocr
OCR_API_KEY = "<OCR_API_KEY>"
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.conf import settings

import telebot
from .telegram_bot.main import bot


@csrf_exempt
def handle_webhook_requests(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])

        return HttpResponse(status=200)

    else:
        return HttpResponse("error")

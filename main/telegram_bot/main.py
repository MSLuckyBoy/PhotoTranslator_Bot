from django.conf import settings
from django.core.cache import cache
import telebot

from main.models import Member

from .middlewares import AntifloodMiddleware
from .localization import BotLocalization
from . import filters
from . import flags
from . import keyboards as btn
from . import ocr_api

import googletrans
import gtts
import os

bot = telebot.TeleBot(
	settings.BOT_TOKEN, 
	parse_mode="HTML",
	use_class_middlewares=True
)

#bot.remove_webhook()
#bot.set_webhook(url=f"https://{settings.WEBHOOK_URL_HOST}/{settings.WEBHOOK_URL_PATH}")

#Middlewares
bot.setup_middleware(AntifloodMiddleware(limit=2))

#Localization
i18n = BotLocalization(translations_path="locales", domain_name="messages")
_ = i18n.gettext

#Translator
translator = googletrans.Translator()

#-------------------------------------------------------------

@bot.message_handler(commands=['start'], chat_types="private")
def start_message(msg):
	markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(
		msg.chat.id, 
		_("start_msg", msg.from_user.language_code).format(first_name=msg.from_user.first_name),
		reply_markup=markup
	)

	member, created = Member.objects.update_or_create(
		chat_id=msg.from_user.id,
		defaults={
			"first_name": msg.from_user.first_name,
			"username": msg.from_user.username,
			"language_code": msg.from_user.language_code
		}
	)

#-------------------------------------------------------------

@bot.message_handler(content_types=['text', 'photo'], chat_types="private")
def main_message(msg):
	if msg.content_type == 'photo':
		bot_msg = bot.send_message(msg.from_user.id, _("scanning_msg", msg.from_user.language_code))
		photo_url = bot.get_file_url(msg.photo[-1].file_id)

		try:
			text = ocr_api.scan(photo_url)
		except:
			bot.send_message(msg.chat.id, _("scanning_error_msg", msg.from_user.language_code).format(support_link=settings.SUPPORT_LINK))
			return
		finally:
			bot.delete_message(bot_msg.chat.id, bot_msg.message_id)

	else:
		text = msg.text

	src = translator.detect(text).lang
	src = src[0].lower() if type(src).__name__ == "list" else src.lower()

	user_lang = msg.from_user.language_code

	if user_lang in flags.FLAGS and user_lang != src:
		dest = user_lang
	elif src != "en":
		dest = "en"
	else:
		dest = "ru"

	cache.set(f"{msg.chat.id}_{msg.message_id}", text, timeout=300)

	bot.reply_to(msg, _("choose_lang_msg", msg.from_user.language_code),
		reply_markup=btn.translator_menu(src=src, dest=dest))

#-------------------------------------------------------------

@bot.callback_query_handler(func=filters.translator_menu_filter)
def translator_menu_message(call):
	src = call.data.split("/")[0]
	callback = call.data.split("/")[1]
	dest = call.data.split("/")[2]

	if callback in ["src", "dest"]:
		bot.edit_message_reply_markup(call.from_user.id, call.message.id,
            reply_markup=btn.language_menu(src=src, dest=dest, btn_type=callback))

	elif callback == "swap":
		bot.edit_message_reply_markup(call.from_user.id, call.message.id,
            reply_markup=btn.translator_menu(src=dest, dest=src))

	elif callback == "translate":
		bot.delete_message(call.from_user.id, call.message.id)
		
		message = call.message.reply_to_message
		
		text = cache.get(f"{message.chat.id}_{message.message_id}")
		
		if text == None and message.content_type == "photo":
			bot_msg = bot.send_message(message.from_user.id, _("rescanning_msg", call.from_user.language_code))
			photo_url = bot.get_file_url(message.photo[-1].file_id)

			try:
				text = ocr_api.scan(photo_url)
			except:
				bot.send_message(msg.chat.id, _("scanning_error_msg", call.from_user.language_code).format(support_link=settings.SUPPORT_LINK))
				return
			finally:
				bot.delete_message(bot_msg.chat.id, bot_msg.message_id)

		elif text == None and message.content_type == "text":
			text = message.text
		
		tr_text = translator.translate(text, src=src, dest=dest)

		src_lang = flags.FLAGS.get(src, googletrans.LANGUAGES[src].title())
		dest_lang = flags.FLAGS.get(dest, googletrans.LANGUAGES[dest].title())

		text_list = [f"{src_lang}:\n<i>{text}</i>", f"\n{'➖'*10}\n", f"{dest_lang}:\n<i>{tr_text.text}</i>"]

		full_text = text_list[0] + text_list[1] + text_list[2]

		if len(full_text) <= 4096:
			markup = btn.tts_button(src=src, dest=dest) if len(text) <= 1024 else None
			bot.send_message(call.from_user.id, full_text, reply_markup=markup, disable_web_page_preview=True)

		elif len(text_list[0]) <= 4096 and len(text_list[2]) <= 4096:
			bot.send_message(call.from_user.id, text_list[0], disable_web_page_preview=True)
			bot.send_message(call.from_user.id, text_list[2], disable_web_page_preview=True)

		else:
			bot.send_message(call.from_user.id, _("long_text_error_msg", call.from_user.language_code))

	elif callback in ["change_src", "change_dest", "back"]:
		bot.edit_message_reply_markup(call.from_user.id, call.message.id,
			reply_markup=btn.translator_menu(src=src, dest=dest))

#-------------------------------------------------------------

@bot.callback_query_handler(func=filters.tts_message_filter)
def tts_message(call):
	callback_type = call.data.split("/")[0]
	callback = call.data.split("/")[1]
	data = call.data.split("/")[2]

	if callback.isdigit():
		bot.copy_message(call.from_user.id, call.from_user.id, callback, reply_to_message_id=call.message.message_id)
		return

	if os.path.exists(f"{settings.MEDIA_ROOT}/audio") == False:
		x=os.makedirs(f"{settings.MEDIA_ROOT}/audio")
	
	text = call.message.text.split(f"\n{'➖'*10}\n")
	sep = flags.FLAGS.get(data, googletrans.LANGUAGES[data].title())
	
	if callback_type == "src":
		text = text[0].split(f"{sep}:\n")[1]
	elif callback_type == "dest":
		text = text[1].split(f"{sep}:\n")[1]

	output = gtts.gTTS(text=text, lang=data)

	bot_msg = bot.send_message(call.from_user.id, _("record_audio_msg", call.from_user.language_code))
	bot.send_chat_action(call.from_user.id, action="record_audio")

	file_path = f"{settings.MEDIA_ROOT}/audio/{call.from_user.id}.ogg"
	output.save(file_path)

	bot.send_chat_action(call.from_user.id, action="upload_audio")

	with open(file_path, "rb") as voice:
		caption = flags.FLAGS.get(data, googletrans.LANGUAGES[data].title())
		msg = bot.send_voice(call.from_user.id, reply_to_message_id=call.message.message_id, voice=voice, caption=caption)

	if os.path.exists(file_path):
		os.remove(file_path)

	bot.edit_message_reply_markup(call.from_user.id, call.message.id,
		reply_markup=btn.tts_button_edit(call=call, voice_message_id=msg.message_id))

	bot.delete_message(bot_msg.chat.id, bot_msg.message_id)

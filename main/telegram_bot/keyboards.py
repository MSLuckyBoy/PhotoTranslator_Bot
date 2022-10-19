from telebot import types
import googletrans
import gtts
from . import flags


def translator_menu(src, dest):
	src_text = flags.FLAGS.get(src, googletrans.LANGUAGES[src].title())
	dest_text = flags.FLAGS.get(dest, googletrans.LANGUAGES[dest].title())
	
	markup = types.InlineKeyboardMarkup()
	markup.add(
		types.InlineKeyboardButton(text=src_text, callback_data=f"{src}/src/{dest}"),
		types.InlineKeyboardButton(text="🔁", callback_data=f"{src}/swap/{dest}"),
		types.InlineKeyboardButton(text=dest_text, callback_data=f"{src}/dest/{dest}")
	)
	markup.add(
		types.InlineKeyboardButton(text="Translate", callback_data=f"{src}/translate/{dest}")
	)

	return markup


def language_menu(src, dest, btn_type):
	buttons = list()
	markup = types.InlineKeyboardMarkup()

	for key, value in flags.FLAGS.items():
		if btn_type == "src":
			value = "🔸" + value if key == src else value
			buttons.append(types.InlineKeyboardButton(text=value, callback_data=f"{key}/change_{btn_type}/{dest}"))
		elif btn_type == "dest":
			value = "🔹" + value if key == dest else value
			buttons.append(types.InlineKeyboardButton(text=value, callback_data=f"{src}/change_{btn_type}/{key}"))

	markup.add(*buttons)
	markup.add(
		types.InlineKeyboardButton(text="🔙Back", callback_data=f"{src}/back/{dest}")
	)

	return markup


def tts_button(src=None, dest=None):
	markup = types.InlineKeyboardMarkup()
	tts_langs = gtts.lang.tts_langs()

	buttons = list()

	if src in tts_langs:
		text = flags.FLAGS.get(src, googletrans.LANGUAGES[src].title())	
		buttons.append(types.InlineKeyboardButton(text=f"🔈 {text}", callback_data=f"src/voice/{src}"))

	if dest in tts_langs:
		text = flags.FLAGS.get(dest, googletrans.LANGUAGES[dest].title())	
		buttons.append(types.InlineKeyboardButton(text=f"🔈 {text}", callback_data=f"dest/voice/{dest}"))

	markup.add(*buttons)

	return markup


def tts_button_edit(call, voice_message_id):
	keyboards = call.message.reply_markup.keyboard[0]
	data_type = call.data.split('/voice/')[0]
	data = call.data.split('/voice/')[1]

	if data_type == "src":
		src_callback_data = f"src/{voice_message_id}/{data}"
		dest_callback_data = keyboards[1].callback_data

	elif data_type == "dest":
		src_callback_data = keyboards[0].callback_data
		dest_callback_data = f"dest/{voice_message_id}/{data}"

	markup = types.InlineKeyboardMarkup()
	markup.add(
		types.InlineKeyboardButton(text=keyboards[0].text, callback_data=src_callback_data),
		types.InlineKeyboardButton(text=keyboards[1].text, callback_data=dest_callback_data)
	)

	return markup
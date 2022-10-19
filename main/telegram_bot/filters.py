import re

def translator_menu_filter(call):
    if re.search("^[a-z -]{2,5}\\/(src|dest|swap|translate)\\/[a-z -]{2,5}$", call.data):
    	return True
    elif re.search("^[a-z -]{2,5}\\/(change_src|change_dest|back)\\/[a-z -]{2,5}$", call.data):
    	return True
    else:
    	return False

def tts_message_filter(call):
	if re.search("^(src|dest)\\/voice\\/[a-z -]{2,5}$", call.data):
		return True
	elif re.search("^(src|dest)\\/\\d+\\/[a-z -]{2,5}$", call.data):
		return True
	else:
		return False

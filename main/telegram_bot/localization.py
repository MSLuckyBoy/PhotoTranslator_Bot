import gettext
import os

class BotLocalization:
	def __init__(self, translations_path, domain_name):
		self.path = translations_path
		self.domain = domain_name
		self.translations = self.find_translations()

	def gettext(self, text, lang):
		if lang not in self.translations:
			return text

		translator = self.translations[lang]
		return translator.gettext(text)

	def find_translations(self):
		if not os.path.exists(self.path):
			raise RuntimeError(f"Translations directory by path: {self.path!r} was not found")

		mo_files = gettext.find(self.domain, self.path, all=True, languages=os.listdir(self.path))
		result = {}

		for mo_file in mo_files:
			language = mo_file.split("/")[1]

			with open(mo_file, "rb") as file:
				result[language] = gettext.GNUTranslations(file)

		return result


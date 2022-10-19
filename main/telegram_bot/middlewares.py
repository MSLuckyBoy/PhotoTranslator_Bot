from telebot.handler_backends import BaseMiddleware
from telebot.handler_backends import CancelUpdate

from django.core.cache import cache


class AntifloodMiddleware(BaseMiddleware):
	def __init__(self, limit):
		self.limit = limit
		self.update_types = ['message']

	def pre_process(self, message, data):
		if cache.get(message.from_user.id):
			return CancelUpdate()
		else:
			cache.set(message.from_user.id, message.date, timeout=self.limit)

	def post_process(self, message, data, exception):
		pass



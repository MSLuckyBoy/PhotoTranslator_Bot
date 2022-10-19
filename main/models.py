from django.db import models


class Member(models.Model):
	chat_id = models.PositiveIntegerField(unique=True)
	first_name = models.CharField(null=True, max_length=64)
	username = models.CharField(null=True, blank=True, max_length=32)
	language_code = models.CharField(max_length=10)
	time_create = models.DateTimeField(auto_now_add=True)
	time_update = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.chat_id} [ {self.first_name} ]"

	class Meta:
		ordering = ['time_create', 'time_update']


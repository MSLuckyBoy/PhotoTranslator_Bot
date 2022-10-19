from django.contrib import admin

from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
	list_display = ('id', 'chat_id', 'first_name', 'username', 'language_code', 'time_create', 'time_update')
	list_display_links = ('id', 'chat_id')
	search_fields = ('chat_id', 'first_name', 'username')
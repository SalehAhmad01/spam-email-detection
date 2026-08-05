from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'sender_display', 'short_raw_text', 'submitted_by', 'submitted_at')
    list_filter = ('channel', 'submitted_at')
    search_fields = ('sender', 'raw_text', 'submitted_by__username')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)

    def sender_display(self, obj):
        return obj.sender or "-"
    sender_display.short_description = "Sender"

    def short_raw_text(self, obj):
        return obj.raw_text[:50] + "..." if len(obj.raw_text) > 50 else obj.raw_text
    short_raw_text.short_description = "Raw Text"

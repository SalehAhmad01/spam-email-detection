from django.contrib import admin
from django.utils.html import format_html
from .models import DetectionResult, FeedbackCorrection


class FeedbackCorrectionInline(admin.TabularInline):
    model = FeedbackCorrection
    extra = 0
    readonly_fields = ('corrected_by', 'corrected_label', 'note', 'created_at')
    can_delete = False


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_sender', 'message_snippet', 'label_badge', 'confidence_display', 'language_mix', 'model_version', 'created_at')
    list_filter = ('label', 'language_mix', 'model_version', 'created_at')
    search_fields = ('message__raw_text', 'message__sender')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [FeedbackCorrectionInline]

    def message_sender(self, obj):
        return obj.message.sender or "Direct Web"
    message_sender.short_description = "Sender"

    def message_snippet(self, obj):
        text = obj.message.raw_text
        return text[:50] + "..." if len(text) > 50 else text
    message_snippet.short_description = "Content Snippet"

    def label_badge(self, obj):
        colors = {
            'legit': 'background-color: #064e3b; color: #6ee7b7;',
            'spam': 'background-color: #78350f; color: #fde68a;',
            'fraud': 'background-color: #7f1d1d; color: #fca5a5;',
        }
        style = colors.get(obj.label, 'background-color: #334155; color: #f1f5f9;')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; {}">{}</span>',
            style, obj.label.upper()
        )
    label_badge.short_description = "Label"

    def confidence_display(self, obj):
        return f"{obj.confidence_score * 100:.1f}%"
    confidence_display.short_description = "Confidence"


@admin.register(FeedbackCorrection)
class FeedbackCorrectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_snippet',
        'original_label_display',
        'corrected_label_badge',
        'corrected_by_user',
        'short_note',
        'created_at'
    )
    list_filter = ('corrected_label', 'detection_result__label', 'created_at')
    search_fields = ('note', 'corrected_by__username', 'detection_result__message__raw_text')
    readonly_fields = ('detection_result', 'corrected_by', 'corrected_label', 'note', 'created_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Correction Information', {
            'fields': ('detection_result', 'corrected_by', 'corrected_label', 'created_at')
        }),
        ('Analyst Reasoning', {
            'fields': ('note',)
        }),
    )

    def message_snippet(self, obj):
        text = obj.detection_result.message.raw_text
        return text[:45] + "..." if len(text) > 45 else text
    message_snippet.short_description = "Raw Message"

    def original_label_display(self, obj):
        return format_html('<span style="color: #94a3b8; font-weight: 600;">{}</span>', obj.detection_result.label.upper())
    original_label_display.short_description = "Original Label"

    def corrected_label_badge(self, obj):
        colors = {
            'legit': 'background-color: #064e3b; color: #6ee7b7;',
            'spam': 'background-color: #78350f; color: #fde68a;',
            'fraud': 'background-color: #7f1d1d; color: #fca5a5;',
        }
        style = colors.get(obj.corrected_label, 'background-color: #334155; color: #f1f5f9;')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; {}">{}</span>',
            style, obj.corrected_label.upper()
        )
    corrected_label_badge.short_description = "Corrected Label"

    def corrected_by_user(self, obj):
        return obj.corrected_by.username if obj.corrected_by else "Anonymous"
    corrected_by_user.short_description = "Reviewer"

    def short_note(self, obj):
        return obj.note[:50] + "..." if obj.note and len(obj.note) > 50 else (obj.note or "-")
    short_note.short_description = "Analyst Note"

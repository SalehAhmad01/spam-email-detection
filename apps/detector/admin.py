from django.contrib import admin
from .models import DetectionResult, FeedbackCorrection


class FeedbackCorrectionInline(admin.TabularInline):
    model = FeedbackCorrection
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'label', 'confidence_display', 'language_mix', 'model_version', 'created_at')
    list_filter = ('label', 'language_mix', 'model_version', 'created_at')
    search_fields = ('message__raw_text', 'message__sender')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    inlines = [FeedbackCorrectionInline]

    def confidence_display(self, obj):
        return f"{obj.confidence_score * 100:.1f}%"
    confidence_display.short_description = "Confidence"


@admin.register(FeedbackCorrection)
class FeedbackCorrectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'detection_result', 'corrected_label', 'corrected_by', 'short_note', 'created_at')
    list_filter = ('corrected_label', 'created_at')
    search_fields = ('note', 'corrected_by__username', 'detection_result__message__raw_text')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def short_note(self, obj):
        return obj.note[:40] + "..." if obj.note and len(obj.note) > 40 else (obj.note or "-")
    short_note.short_description = "Note"

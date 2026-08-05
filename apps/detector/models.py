from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DetectionResult(models.Model):
    class LabelChoices(models.TextChoices):
        LEGIT = 'legit', 'Legitimate'
        SPAM = 'spam', 'Spam'
        FRAUD = 'fraud', 'Fraud / Phishing'

    class LanguageChoices(models.TextChoices):
        ENGLISH = 'english', 'English'
        PIDGIN = 'pidgin', 'Nigerian Pidgin'
        MIXED = 'mixed', 'Mixed Language'

    message = models.OneToOneField(
        'inbox.Message',
        on_delete=models.CASCADE,
        related_name='detection_result',
        help_text="Associated message inspected by detector."
    )
    label = models.CharField(
        max_length=20,
        choices=LabelChoices.choices,
        default=LabelChoices.LEGIT,
        db_index=True,
        help_text="Threat classification label."
    )
    confidence_score = models.FloatField(
        help_text="Confidence score from 0.0 to 1.0."
    )
    flagged_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="List of flagged keywords or suspicious tokens extracted."
    )
    language_mix = models.CharField(
        max_length=30,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH,
        help_text="Primary language mixture of the message."
    )
    model_version = models.CharField(
        max_length=50,
        default='v1.0',
        help_text="Version of ML/heuristic model used."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['label']),
            models.Index(fields=['created_at']),
            models.Index(fields=['confidence_score']),
        ]

    def __str__(self):
        return f"Result #{self.id} for Message #{self.message_id} - {self.get_label_display()} ({self.confidence_score * 100:.1f}%)"


class FeedbackCorrection(models.Model):
    detection_result = models.ForeignKey(
        DetectionResult,
        on_delete=models.CASCADE,
        related_name='feedback_corrections',
        help_text="Target detection result being flagged or corrected."
    )
    corrected_label = models.CharField(
        max_length=20,
        choices=DetectionResult.LabelChoices.choices,
        help_text="User-suggested correct label for model retraining."
    )
    corrected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_corrections',
        help_text="User submitting the feedback correction."
    )
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Reasoning or notes to assist model retraining."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['corrected_label']),
        ]

    def __str__(self):
        user_str = self.corrected_by.username if self.corrected_by else "Anonymous"
        return f"Correction on Result #{self.detection_result_id} by {user_str} -> {self.get_corrected_label_display()}"

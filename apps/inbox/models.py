from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    class ChannelChoices(models.TextChoices):
        SMS = 'sms', 'SMS Text'
        EMAIL = 'email', 'Email'
        WHATSAPP = 'whatsapp', 'WhatsApp'

    channel = models.CharField(
        max_length=20,
        choices=ChannelChoices.choices,
        default=ChannelChoices.SMS,
        help_text="Channel through which the message was received."
    )
    raw_text = models.TextField(
        help_text="Original raw body text of the message."
    )
    sender = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Phone number, email address, or sender ID."
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_messages',
        help_text="User who submitted this message for detection (optional)."
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['submitted_at']),
            models.Index(fields=['channel']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        sender_str = f" from {self.sender}" if self.sender else ""
        text_snippet = self.raw_text[:30] + "..." if len(self.raw_text) > 30 else self.raw_text
        return f"[{self.get_channel_display()}]{sender_str}: \"{text_snippet}\""

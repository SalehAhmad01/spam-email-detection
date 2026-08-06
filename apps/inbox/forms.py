from django import forms
from inbox.models import Message
from detector.models import DetectionResult, FeedbackCorrection

TAILWIND_INPUT = (
    "w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white "
    "placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
)

TAILWIND_SELECT = (
    "w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white "
    "focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
)

TAILWIND_TEXTAREA = (
    "w-full bg-slate-950 border border-slate-800 rounded-lg p-4 text-sm text-white font-mono "
    "placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
)


class SingleMessageForm(forms.ModelForm):
    channel = forms.ChoiceField(
        choices=Message.ChannelChoices.choices[:2],  # SMS and Email
        widget=forms.RadioSelect(attrs={'class': 'hidden peer'}),
        initial=Message.ChannelChoices.SMS
    )

    class Meta:
        model = Message
        fields = ('channel', 'sender', 'raw_text')
        widgets = {
            'sender': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. +2348030000000 or alert@bank.ng'}),
            'raw_text': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 6, 'placeholder': 'Paste SMS or email body content here to analyze threat vectors...'}),
        }


class BulkCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 file:cursor-pointer'
        })
    )


class FeedbackCorrectionForm(forms.ModelForm):
    class Meta:
        model = FeedbackCorrection
        fields = ('corrected_label', 'note')
        widgets = {
            'corrected_label': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'note': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3, 'placeholder': 'Explain why this was misclassified (e.g. "This is an official bank notification, not phishing")...'}),
        }

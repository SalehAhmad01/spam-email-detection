from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inbox.models import Message
from .models import DetectionResult


@login_required
def scan_text(request):
    scan_result = None

    if request.method == 'POST':
        channel = request.POST.get('channel', 'sms')
        raw_text = request.POST.get('message_text', '').strip()
        sender = request.POST.get('sender', '').strip() or 'Direct Submission'

        if raw_text:
            # Simple keyword rule evaluation engine
            text_lower = raw_text.lower()
            fraud_keywords = ['bvn', 'nin', 'account freeze', 'cbn-verify', 'palmpay', 'opay', 'blocked']
            spam_keywords = ['won', 'promo', 'claim', 'whatsapp', '200k', 'cash reward']

            flagged = []
            for kw in fraud_keywords:
                if kw in text_lower:
                    flagged.append(kw)

            for kw in spam_keywords:
                if kw in text_lower:
                    flagged.append(kw)

            if any(kw in text_lower for kw in fraud_keywords):
                label = DetectionResult.LabelChoices.FRAUD
                score = 0.96
            elif any(kw in text_lower for kw in spam_keywords):
                label = DetectionResult.LabelChoices.SPAM
                score = 0.88
            else:
                label = DetectionResult.LabelChoices.LEGIT
                score = 0.99

            # Save Message to Database
            msg_obj = Message.objects.create(
                channel=channel,
                raw_text=raw_text,
                sender=sender,
                submitted_by=request.user
            )

            # Save DetectionResult to Database
            scan_result = DetectionResult.objects.create(
                message=msg_obj,
                label=label,
                confidence_score=score,
                flagged_keywords=flagged,
                language_mix='pidgin' if 'abeg' in text_lower else 'english',
                model_version='v1.0-rules'
            )
            messages.success(request, f"Threat analysis complete. Saved to database as #{msg_obj.id}.")
        else:
            messages.error(request, "Please enter message text to inspect.")

    return render(request, 'detector/scan.html', {'result': scan_result})

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from inbox.models import Message
from detector.models import DetectionResult


@login_required
def index(request):
    # Dynamic live database metrics
    total_messages = Message.objects.count()
    blocked_count = DetectionResult.objects.filter(label__in=['spam', 'fraud']).count()
    legit_count = DetectionResult.objects.filter(label='legit').count()

    if total_messages > 0:
        legit_percentage = round((legit_count / total_messages) * 100, 1)
    else:
        legit_percentage = 100.0

    recent_interceptions = DetectionResult.objects.select_related('message').order_by('-created_at')[:5]

    context = {
        'total_messages': total_messages,
        'blocked_count': blocked_count,
        'legit_count': legit_count,
        'legit_percentage': legit_percentage,
        'recent_interceptions': recent_interceptions,
    }
    return render(request, 'pages/home.html', context)


@login_required
def analytics_view(request):
    # Overall Counts
    total_checked = DetectionResult.objects.count()
    legit_count = DetectionResult.objects.filter(label='legit').count()
    spam_count = DetectionResult.objects.filter(label='spam').count()
    fraud_count = DetectionResult.objects.filter(label='fraud').count()

    # Fraud Rate %
    fraud_rate = round((fraud_count / total_checked * 100), 1) if total_checked > 0 else 0.0

    # Language Mix Breakdown
    lang_english = DetectionResult.objects.filter(language_mix='english').count()
    lang_pidgin = DetectionResult.objects.filter(language_mix='pidgin').count()
    lang_mixed = DetectionResult.objects.filter(language_mix='mixed').count()

    # Channel Breakdown
    channel_sms = DetectionResult.objects.filter(message__channel='sms').count()
    channel_email = DetectionResult.objects.filter(message__channel='email').count()
    channel_whatsapp = DetectionResult.objects.filter(message__channel='whatsapp').count()

    # Trend Over Time (Grouped by Date)
    trend_queryset = (
        DetectionResult.objects
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(
            total=Count('id'),
            fraud=Count('id', filter=Q(label='fraud')),
            spam=Count('id', filter=Q(label='spam')),
            legit=Count('id', filter=Q(label='legit'))
        )
        .order_by('date')
    )

    dates = [item['date'].strftime('%b %d') if item['date'] else 'Today' for item in trend_queryset]
    trend_fraud = [item['fraud'] for item in trend_queryset]
    trend_spam = [item['spam'] for item in trend_queryset]
    trend_legit = [item['legit'] for item in trend_queryset]

    context = {
        'total_checked': total_checked,
        'legit_count': legit_count,
        'spam_count': spam_count,
        'fraud_count': fraud_count,
        'fraud_rate': fraud_rate,
        # JSON serialized data for Chart.js
        'ratio_json': json.dumps([legit_count, spam_count, fraud_count]),
        'lang_json': json.dumps([lang_english, lang_pidgin, lang_mixed]),
        'channel_json': json.dumps([channel_sms, channel_email, channel_whatsapp]),
        'dates_json': json.dumps(dates),
        'trend_fraud_json': json.dumps(trend_fraud),
        'trend_spam_json': json.dumps(trend_spam),
        'trend_legit_json': json.dumps(trend_legit),
    }
    return render(request, 'dashboard/analytics.html', context)

import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from inbox.models import Message
from detector.models import DetectionResult, FeedbackCorrection
from detector.engine import analyze_message
from .forms import SingleMessageForm, BulkCSVUploadForm, FeedbackCorrectionForm


@login_required
def submit_message_view(request):
    single_form = SingleMessageForm()
    bulk_form = BulkCSVUploadForm()

    if request.method == 'POST':
        # Single Message Submission
        if 'submit_single' in request.POST:
            single_form = SingleMessageForm(request.POST)
            if single_form.is_valid():
                msg_obj = single_form.save(commit=False)
                msg_obj.submitted_by = request.user
                msg_obj.save()

                analysis = analyze_message(
                    raw_text=msg_obj.raw_text,
                    channel=msg_obj.channel,
                    sender=msg_obj.sender
                )

                result_obj = DetectionResult.objects.create(
                    message=msg_obj,
                    label=analysis['label'],
                    confidence_score=analysis['confidence_score'],
                    flagged_keywords=analysis['flagged_keywords'],
                    language_mix=analysis['language_mix'],
                    model_version=analysis['model_version']
                )

                messages.success(request, "Message successfully analyzed and recorded!")
                return redirect('inbox:result', pk=result_obj.pk)
            else:
                messages.error(request, "Please correct errors in the single message form.")

        # Bulk CSV Upload
        elif 'submit_bulk' in request.POST:
            bulk_form = BulkCSVUploadForm(request.POST, request.FILES)
            if bulk_form.is_valid():
                csv_file = request.FILES['csv_file']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, "Uploaded file must be a CSV format.")
                    return redirect('inbox:submit')

                data_set = csv_file.read().decode('utf-8')
                io_string = io.StringIO(data_set)
                reader = csv.DictReader(io_string)

                created_results = []
                for row in reader:
                    text = row.get('text') or row.get('message') or row.get('raw_text') or ''
                    if not text.strip():
                        continue

                    channel = row.get('channel', 'sms').lower()
                    if channel not in ['sms', 'email', 'whatsapp']:
                        channel = 'sms'

                    sender = row.get('sender', 'Bulk Upload CSV')

                    msg_obj = Message.objects.create(
                        channel=channel,
                        raw_text=text.strip(),
                        sender=sender,
                        submitted_by=request.user
                    )

                    analysis = analyze_message(raw_text=text, channel=channel, sender=sender)

                    result_obj = DetectionResult.objects.create(
                        message=msg_obj,
                        label=analysis['label'],
                        confidence_score=analysis['confidence_score'],
                        flagged_keywords=analysis['flagged_keywords'],
                        language_mix=analysis['language_mix'],
                        model_version=analysis['model_version']
                    )
                    created_results.append(result_obj.pk)

                request.session['bulk_result_ids'] = created_results
                messages.success(request, f"Processed {len(created_results)} messages from CSV upload!")
                return redirect('inbox:bulk_results')
            else:
                messages.error(request, "Failed to parse CSV upload file.")

    return render(request, 'inbox/submit.html', {
        'single_form': single_form,
        'bulk_form': bulk_form
    })


@login_required
def result_detail_view(request, pk):
    result = get_object_or_404(DetectionResult.objects.select_related('message'), pk=pk)

    if request.method == 'POST' and 'submit_correction' in request.POST:
        feedback_form = FeedbackCorrectionForm(request.POST)
        if feedback_form.is_valid():
            correction = feedback_form.save(commit=False)
            correction.detection_result = result
            correction.corrected_by = request.user
            correction.save()

            messages.success(request, "Thank you for your feedback correction! This will assist future ML model retraining.")
            return redirect('inbox:result', pk=result.pk)
        else:
            messages.error(request, "Please fill in a valid corrected label and note.")
    else:
        feedback_form = FeedbackCorrectionForm(initial={'corrected_label': result.label})

    existing_corrections = result.feedback_corrections.select_related('corrected_by').order_by('-created_at')

    context = {
        'result': result,
        'feedback_form': feedback_form,
        'existing_corrections': existing_corrections,
    }
    return render(request, 'inbox/result.html', context)


@login_required
def history_view(request):
    # Base queryset for logged in user's submitted messages
    queryset = DetectionResult.objects.select_related('message').filter(message__submitted_by=request.user).order_by('-created_at')

    # Filter parameters
    channel_filter = request.GET.get('channel', '').strip()
    label_filter = request.GET.get('label', '').strip()

    if channel_filter:
        queryset = queryset.filter(message__channel=channel_filter)

    if label_filter:
        queryset = queryset.filter(label=label_filter)

    # Pagination (10 per page)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'channel_filter': channel_filter,
        'label_filter': label_filter,
        'total_count': paginator.count,
    }
    return render(request, 'inbox/history.html', context)


@login_required
def bulk_results_view(request):
    bulk_ids = request.session.get('bulk_result_ids', [])
    if bulk_ids:
        results = DetectionResult.objects.select_related('message').filter(pk__in=bulk_ids)
    else:
        results = DetectionResult.objects.select_related('message').order_by('-created_at')[:20]

    return render(request, 'inbox/bulk_results.html', {'results': results, 'bulk_count': len(bulk_ids)})


@login_required
def message_list(request):
    results = DetectionResult.objects.select_related('message').order_by('-created_at')
    return render(request, 'inbox/list.html', {'results': results})

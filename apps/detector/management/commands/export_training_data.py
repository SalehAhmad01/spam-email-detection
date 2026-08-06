import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from detector.models import DetectionResult, FeedbackCorrection


class Command(BaseCommand):
    help = 'Exports merged dataset (original detections + user feedback corrections) into a retraining CSV file.'

    def add_arguments(self, parser):
        default_output = str(settings.BASE_DIR / 'apps' / 'detector' / 'data' / 'retraining_dataset.csv')
        parser.add_argument(
            '--output',
            type=str,
            default=default_output,
            help='Target path to save the exported retraining CSV dataset file.'
        )

    def handle(self, *args, **options):
        output_path = Path(options['output'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        results = DetectionResult.objects.select_related('message').prefetch_related('feedback_corrections').order_by('id')

        total_exported = 0
        corrections_applied = 0

        with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['text', 'label', 'channel', 'language_mix', 'sender'])

            for item in results:
                raw_text = item.message.raw_text
                channel = item.message.channel
                lang_mix = item.language_mix
                sender = item.message.sender or ''

                # Check if user submitted a FeedbackCorrection for this record
                latest_correction = item.feedback_corrections.order_by('-created_at').first()
                if latest_correction:
                    effective_label = latest_correction.corrected_label
                    corrections_applied += 1
                else:
                    effective_label = item.label

                writer.writerow([raw_text, effective_label, channel, lang_mix, sender])
                total_exported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {total_exported} records ({corrections_applied} user corrections applied) to '{output_path}'!"
            )
        )

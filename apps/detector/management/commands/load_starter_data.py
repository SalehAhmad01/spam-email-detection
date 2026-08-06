import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from inbox.models import Message
from detector.models import DetectionResult


class Command(BaseCommand):
    help = "Loads starter training data from starter_training_data.csv into database models."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help="Path to CSV file (defaults to apps/detector/data/starter_training_data.csv)"
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if not file_path:
            base_dir = Path(__file__).resolve().parent.parent.parent
            file_path = base_dir / 'data' / 'starter_training_data.csv'

        csv_file = Path(file_path)
        if not csv_file.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file}"))
            return

        created_count = 0
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                msg = Message.objects.create(
                    channel=row.get('channel', 'sms'),
                    raw_text=row.get('text', ''),
                    sender=row.get('sender', '')
                )
                DetectionResult.objects.create(
                    message=msg,
                    label=row.get('label', 'legit'),
                    confidence_score=0.95,
                    language_mix=row.get('language_mix', 'english'),
                    model_version='v1.0-starter'
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {created_count} starter records into the database!"))

import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application

# Ensure apps directory is in sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir / 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_asgi_application()

from .base import *

DEBUG = True

# Internal IPs for development tools
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Output emails to console during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

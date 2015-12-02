from datetime import timedelta
import os


def bool_env(val):
    """Replaces string based environment values with Python booleans"""
    return True if os.environ.get(val, False) == 'True' else False

TIMEZONE = os.getenv('TIMEZONE', "US/Central")

#######
# Flask
#
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

########
# Celery
#
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ALWAYS_EAGER = bool_env('CELERY_ALWAYS_EAGER')
CELERYBEAT_SCHEDULE = {
        'every-minute': {
            'task': 'batch.charge_cards',
            'schedule': timedelta(seconds=10)
            },
        }

######
# SMTP
#
MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'user')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD' 'pass')
MAIL_PORT = os.getenv('MAIL_PORT', '2525')
MAIL_USE_TLS = bool_env('MAIL_USE_TLS', True)
DEFAULT_MAIL_SENDER = os.getenv('DEFAULT_MAIL_SENDER', 'me@myplace.org')

############
# Salesforce
#
MEMBERSHIP_RECORDTYPEID = '01216000001IhHp'
DONATION_RECORDTYPEID = '01216000001IhI9'
SALESFORCE = {
    "CLIENT_ID": os.getenv('SALESFORCE_CLIENT_ID'),
    "CLIENT_SECRET": os.getenv('SALESFORCE_CLIENT_SECRET'),
    "USERNAME": os.getenv('SALESFORCE_USERNAME'),
    "PASSWORD": os.getenv('SALESFORCE_PASSWORD'),
    "HOST": os.getenv("SALESFORCE_HOST")
}

########
# Stripe
#
STRIPE_KEYS = {
    'secret_key': os.getenv('SECRET_KEY'),
    'publishable_key': os.getenv('PUBLISHABLE_KEY')
}

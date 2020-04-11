DEBUG = False

LOAD_TIMEOUT = 10
PROXY_LOAD_TIMEOUT = 180

ERRORS_MAX_COUNT = 2

LOG_FORMAT = '%(asctime)-15s %(message)s'

PROCS_NUM = 2
GUYS_PER_PROC = 250

DB = {
    'name': 'eth',
    'host': '127.0.0.1',
    'port': 27019
}

PROXY = '127.0.0.1:8118'
TOR_PORT = 9051

# hush!

import secrets

GUYS = secrets.GUYS
LEAD = secrets.LEAD

API_KEY = secrets.API_KEY
SITE_KEY = secrets.SITE_KEY

URL = secrets.URL
REF_URL = secrets.REF_URL
LOGIN_URL = secrets.LOGIN_URL
LOGOUT_URL = secrets.LOGOUT_URL

PASSWORD = getattr(secrets, 'PASSWORD')

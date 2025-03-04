import json

config = {
    "DEBUG": False,
    "SECRET_KEY": "django-insecure-j8op9)1q8$1&0^s&p*_0%d#pr@w9qj@1o=3#@d=a(^@9@zd@%j",
    "ALLOWED_HOSTS": [
        "*"
    ],
    "CSRF_TRUSTED_ORIGINS": [
        "https://example.com",
        "https://sub.example.com"
    ],
    "TIME_ZONE": "Asia/Kolkata",
    "DATABASE_URL": "postgresql://user:password@localhost:5432/dbname",
    "DB_CONFIG": {
        "DB_INIT_PASSWORD": "d3f6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d",
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": 5432
    }
}

def get_hr_setting(subdoamin, domain, db_name):
    config['CSRF_TRUSTED_ORIGINS'] = [f'http://{domain}', f'https://{domain}', f'http://{subdoamin}.{domain}', f'https://{subdoamin}.{domain}']
    config['DB_CONFIG']['NAME'] = db_name
    return json.dumps(config)
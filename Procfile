# filepath: c:\Django Project\FC92_Club\FC92_Club\Procfile
release: python manage.py migrate
web: gunicorn FC92_Club.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
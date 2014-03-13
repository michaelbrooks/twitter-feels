web: gunicorn twitter_feels.wsgi:application --access-logfile -
worker: python manage.py rqworker
stream: python manage.py stream
scheduler: python manage.py rqscheduler

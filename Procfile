web: PYTHONUNBUFFERED=1 gunicorn twitter_feels.wsgi:application --access-logfile -
worker: PYTHONUNBUFFERED=1 python manage.py rqworker
stream: PYTHONUNBUFFERED=1 python manage.py stream
scheduler: PYTHONUNBUFFERED=1 python manage.py rqscheduler

#web_debug: PYTHONUNBUFFERED=1 python manage.py runserver
#syncdb: PYTHONUNBUFFERED=1 python manage.py syncdb
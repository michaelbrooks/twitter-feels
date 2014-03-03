web: PYTHONUNBUFFERED=1 gunicorn twitter_feels.wsgi:application --access-logfile -
worker: PYTHONUNBUFFERED=1 python manage.py rqworker
stream: PYTHONUNBUFFERED=1 python manage.py stream --scheduler-queue default

#web_debug: PYTHONUNBUFFERED=1 python manage.py runserver
#scheduler: PYTHONUNBUFFERED=1 python manage.py rqscheduler
#syncdb: PYTHONUNBUFFERED=1 python manage.py syncdb
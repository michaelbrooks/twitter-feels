web: gunicorn twitter_feels.wsgi:application
worker: PYTHONUNBUFFERED=1 python manage.py rqworker
stream: PYTHONUNBUFFERED=1 python manage.py stream --scheduler-queue default

# scheduler: PYTHONUNBUFFERED=1 python manage.py rqscheduler
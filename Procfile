web: gunicorn twitter_feels.wsgi:application -c gunicorn.conf.py --access-logfile -
worker: python manage.py rqworker
stream: python manage.py stream
scheduler: python manage.py rqscheduler --interval 15
test: which gunicorn
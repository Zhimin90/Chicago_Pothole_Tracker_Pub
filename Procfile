web: gunicorn --pythonpath geodjango geodjango.wsgi:application  --log-file=-
clock: python geodjango/manage.py runscript load_data_frame_schedule
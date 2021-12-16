#coverage run --source='.' --omit '.venv*' manage.py test tests/
coverage run  --omit '.venv*'  -m unittest discover
coverage report
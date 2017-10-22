pip install -r requirements.txt
python2.7 website/manage.py syncdb
python2.7 website/manage.py migrate

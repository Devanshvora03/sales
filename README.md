pip install -r requirements.txt
python manage.py createsuperuser

# create the user by your choice of username, email, password

python manage.py makemigrations
python manage.py migrate

python manage.py runserver
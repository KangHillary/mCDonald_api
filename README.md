# mCDonald_api

McDonald API is developed with the django framework and rest API part is done via rest framework.

Python3.5 as the python version. 

During this cycle of development, sqlite 3 is used with simplicity in mind. 

To run the application.

Create a python virtual environment with python3.5

virtualenv -p python3.5 venv

Activate environment 

source venv/bin/activate

install requirements.

pip install -r requirements.txt

Run migrations 

python manage.py migrate

Run the application and serve is through simple web server

python manage.py runserver 8091 



TODO:

Dockerize application

use gunicorn web server in favour of simple web server to enhance the API

Use Postgres database.

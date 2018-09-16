# Web Application for SWD BITS Goa

## About

The main repository for the development of SWD web application of BITS Goa.

## Installation

* Assuming you have python 3.4 already installed, go to the desired folder on your machine and follow these commands to clone the repository and install dependencies in a virtual environment:

```
$ virtualenv swd
$ cd swd
$ source bin/activate
$ git clone https://github.com/swd-bits-goa/swd_django src
$ cd src/swd
$ pip install -r requirements.txt
```
NOTE for windows in the 3rd line use:
```
$ swd\Scripts\activate
```

* db.sqlite3 is the database for this repository, you can delete that if you want to start with a fresh database and follow: (But not required and can skip this step)

```
$ python manage.py migrate
```

* Create a superuser for admin controls (accessible at localhost:8000/admin)

```
$ python manage.py createsuperuser
```

* Run the server and access at localhost:8000

```
$ python manage.py runserver
```

## Importing Data

To import data, there are a set of scripts created. On hitting the urls mentioned in [swd/swd/urls.py#L52-L58](https://github.com/SebastinSanty/swd_django/blob/master/swd/swd/urls.py#L52-L58), the data will get imported. Please be patient as there are ~9000 records to be inserted. You don't necessarily need to use all the data. Scripts are designed to handle failures, so no worries :). If you need more data, just hit the url again.


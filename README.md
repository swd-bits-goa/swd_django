# SWD Website BITS Goa

The main repository for the development of SWD website of BITS Goa. It is hosted at swd.bits-goa.ac.in

---
## Setting the Environment

Assuming you have python 3.4 (or above) already installed, go to the desired folder on your machine and follow these commands to clone the repository and install dependencies in a virtual environment:

#### Virtual Environment
It's possible to skip this step, but it's highly recommended to keep your coding environment tidy.

On Linux:
```
$ python3 -m venv swd
$ cd swd
$ source bin/activate
```
On Windows:
```
$ python -m venv swd
$ cd swd
$ swd\Scripts\activate
```
#### Forking and Dependencies
Fork the repository and clone it.
```
$ git clone https://github.com/YOUR_USERNAME/swd_django src
$ cd src/swd
$ pip install -r requirements.txt
```
#### Database
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

**Important:** This requires the `dev_info.py` to be present in `tools` folder. Please contact the maintainers if you don't have it.

To import data, there are a set of scripts created. On accessing the urls mentioned in [swd/swd/urls.py#L52-L58](https://github.com/swd-bits-goa/swd_django/blob/master/swd/swd/urls.py#L52), the data will get imported from `dev_info.py`. 
- Example: To create users - [localhost:8000/create-users/](localhost:8000/create-users/)

Please be patient as there are ~9000 records to be inserted. You don't necessarily need to use all the data. Scripts are designed to handle failures, so no worries :). If you need more data, just hit the url again.

---
## Contributing
If you face any problem using the site, you can create an issue [here](https://github.com/swd-bits-goa/swd_django/issues) or solve one if you are a developer. TIA :)

## Licensing
This project is licensed under [MIT license](LICENSE).
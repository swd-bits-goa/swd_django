# SWD Website BITS Goa

The main repository for the development of SWD website of BITS Goa. It is hosted at swd.bits-goa.ac.in

---

## Setting the Environment

Assuming you have python 3.4 (or above) already installed, go to the desired folder on your machine and follow these commands to clone the repository and install dependencies in a virtual environment:

#### Virtual Environment

It's possible to skip this step, but it's highly recommended to keep your coding environment tidy.

On Linux:

```bash
$ python3 -m venv swd
$ cd swd
$ source bin/activate
```

On Windows:

```bash
$ python -m venv swd
$ cd swd
$ .\Scripts\activate
```

#### Forking and Dependencies

Fork the repository and clone it.

```bash
$ git clone https://github.com/YOUR_USERNAME/swd_django src
$ cd src/swd
$ pip install -r requirements.txt
```
#### Database

* db.sqlite3 is the database for this repository, you can delete that if you want to start with a fresh database and follow: (But not required and can skip this step)

### Shifting to development

* Go to swd/config.py and change ```PRODUCTION``` and ```EMAIL_PROD``` to ```False```
* While committing any changes, make sure to change ```PRODUCTION``` and ```EMAIL_PROD``` variable to ```True``` again

***Note:*** When setting up the environment make sure you run ```$ python manage.py setup_keys```, this will create ```dev_info.py```.
This needs to be done once only. This creates secret key and other important variables for the project. This will overwrite and previous file with same name and render 
any previous database and session invalid.

```bash
$ python manage.py setup_keys
$ python manage.py migrate
```

* Create a superuser for admin controls (accessible at localhost:8000/admin)

```bash
$ python manage.py createsuperuser
```

### Populate the database

* To generate dummy data for the website, use the following script

```bash
$ python populate_data.py
```

* this will create a super user with username as ```admim``` and password as ```password```

### Running the development server

* Run the server and access at localhost:8000

```bash
$ python manage.py runserver
```

### Logging in

* To login as a student use the format as username: f20180001 or p20180001 and password: passoword
* To login as admin, username: admin and password: password

**Important:** This requires the `dev_info.py` to be present in `tools` folder. Please contact the maintainers if you don't have it.

---

## Contributing

If you face any problem using the site, you can create an issue [here](https://github.com/swd-bits-goa/swd_django/issues) or solve one if you are a developer. TIA :)

## Licensing

This project is licensed under [MIT license](LICENSE).

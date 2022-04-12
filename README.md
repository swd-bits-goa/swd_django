# SWD Website BITS Goa

The main repository for the development of SWD website of BITS Goa.<br>Hosted at [swd.bits-goa.ac.in](https://swd.bits-goa.ac.in)

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

## Shifting to development

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

## Populate the database

* To generate dummy data for the website, use the following script

```bash
$ python populate_data.py
```

* this will create a super user with username as ```admin``` and password as ```password```

## Running the development server

* Run the server and access at localhost:8000

```bash
$ python manage.py runserver
```

## Logging In

**Important:** This requires the `dev_info.py` to be present in `tools` folder. Please contact the maintainers if you don't have it.

Here's a list of usernames for different types of credentials. The password for all of these is `password`.

* **Admin**<br>Username: `admin`

* **Student**<br>Example: `f20180001` or `p20180001`<br>A full list of generated students can be found in the admin tab

* **Warden**<br>Format: `warden_<hostel name>`<br>Example: `warden_AH1`, `warden_AH2` (hostel name always in uppercase)

* **Hostel Superintendent**<br>Format: `superintendent_<hostel 1>_<hostel 2>`<br><details><summary>Full list of usernames</summary>`superintendent_AH1_AH2`, `superintendent_AH3_AH4`, `superintendent_AH5_AH6`, `superintendent_AH7_AH8`, `superintendent_AH9_CH1`, `superintendent_CH2_CH3`, `superintendent_CH4_CH5`, `superintendent_CH6_CH7`, `superintendent_DH1_DH2`, `superintendent_DH3_DH4`, `superintendent_DH5_DH6`</details>

* **Gate Security**:<br>Username: **security**

---

## Contributing

If you face any problem using the site, you can create an issue [here](https://github.com/swd-bits-goa/swd_django/issues) or solve one if you are a developer. TIA :)

## Licensing

This project is licensed under [MIT license](LICENSE).

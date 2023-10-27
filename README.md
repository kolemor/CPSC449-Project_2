# Project 2

## create a venv and activate it then install the requirements

`python -m venv myenv`

`source myenv/bin/activate`

`pip install -r requirements.txt`

## then in the main directory run this command to run the uvicorn server

`foreman start -m enrollment=3,primary=1,secondary=1,tertiary=1,krakend=1`

## finally go to the following link to test the api

- Enrollment service

  `http://localhost:5000/docs`

  `http://localhost:5001/docs`

  `http://localhost:5002/docs`

- user service

  `http://localhost:5100/docs`

- KrakenD (enrollment service)

  `http://localhost:5400/api/`

## to populate the databases with some sample data run populate.py from the main directory

`python enrollment/populate_enrollment.py`

`python users/populate_users.py`

the user database population can take anywhere from 30 seconds to a couple minutes as there are ~600 users, and each one needs to have their password hashed, which takes some time. I'll see if I can optimize this later on, but for now it works

## if you want to view what was populated in the enrollment.db run enrollment_queries.py (the population for users.db does this automatically)

`python enrollment_queries.py`

# Enrollment Service testing variables

- student_id 1 is on 3 waitlists (class_id: 8, 4, 13)
- class_id 2 (with instructor_id 2) has 4 dropped students
- class_id 4, 6, 8, 13, 14 are all full, but have open waitlists
- class_id 12 is fully enrolled, with a full waitlist
- all classes have a default max_enroll value of 30
- there are 500 student_ids, with upwards of 300 of them currently being used
- there are 100 instructor_ids, with only ~14 of them being used

# Users Service testing variables

- the first user has a username of "James Smith"
- Every user's non-hashed password is the same as their username
- Users 1 - 500 have the 'student' role
- Users 501 - 600 have the 'instructor' role
- Users 551 - 600 also have the 'registrar' role

# windows execution policy

- if you are running this on a windows machine you may have to set the execution policy to run your virutal enviroment

` Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

# Overview of files

## Enrollment Service (Project 1)

- enrollment_queries.py:

  prints to the terminal what is located within the enrollment database

- enrollment_routes.py:

  contains all the routes and code for the endpoints of the API

- enrollment.db:

  the database file for the enrollment service

- enrollment.py:

  the 'main' file for the enrollment service

- populate_enrollment.py:

  creates and populates the enrollment database

- enrollment_schemas.py:

  has all the base models for the service

## Users Service (Project 2)

- mkclaims.py & mkjwk.py:

  used for JWT claims

- populate_users.py:

  creates and populates the users database

- users_routes.py:

  contains all the routes and code for the endpoints of the API

- users.db:

  the database file for the users service

- users.py:

  the 'main' file for the users service

- users_schemas.py:

  has all the base models for the service

- users_hash.py:

  has functions which handle password hashing

## Misc files

- Procfile:

  runs both services

- requirements.txt:

  the required libraries that pip needs to install

- CPSC 449 Project 1 Documentation:

  self explanatory

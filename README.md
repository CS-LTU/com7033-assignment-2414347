# Stroke Prediction Management System

A secure Flask web application that manages patient stroke data using **SQLite** and **MongoDB**, built for the COM7033 Secure Software Development assessment.

## ✔ Features
- Secure registration & login (SQLite + password hashing)
- CRUD operations for stroke dataset patients (MongoDB)
- CSRF protection, input validation, secure sessions
- Role‑based access to user‑added records
- Logging for all critical operations
- Reset script to rebuild databases safely

## ✔ Security Features
- BCrypt password hashing
- CSRF protection using Flask‑WTF
- Input validation with WTForms
- Secure sessions using Flask
- Detailed logging for auditing

## ✔ How to Run
## Preperation:
Install Python.
pip install python
Install Mongodb.
Run and Connect test server to Mongodb.
Install any libraries, not installed on your pc:
pip install flask flask_sqlalchemy flask_bcrypt flask_wtf wtforms pymongo
pip install bcrypt

## To Run:
(in terminal):
```bash
.\env\Scripts\activate
python .\reset.py
python -m flask --app .\app.py run
```

## ✔ How to Reset Databases
```bash
python .\reset.py
```

## ✔ Unit Tests
Run tests using:
```bash 
python -m unittest discover
```

## ✔ How to Use
After successful running
Go to http://localhost:5000/ your local host.
Go to create account.
Go to login and enter your credentials.
Click on Add Patient.
Add all History of your patient and click add.
From My Patients, Manage your patients, edit or delete.

## ✔ Use of Generative AI
This assignment used generative AI for **explanation** purposes.

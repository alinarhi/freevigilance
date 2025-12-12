# Freevigilance
***Task manager for the pharmaceutical industry*** 

Manage `PVAs`, `Obligations` and `Tasks` and keep track of all changes

<img src="demo/freevigilance-demo.gif" alt="screen 1" height=600>

## To run locally
*prerequisites: python 3.10, npm*
### 1. clone this repo
### 2. create venv in `backend` folder, install dependencies and run manage.py
In terminal:
  - $ cd backend
  - $ python3 -m venv .venv
  - $ source .venv/bin/activate
  - $ pip install -r requirements.txt
  - $ python manage.py runserver
### 3. go to `frontend` folder, configure VITE_API_URL in .env, install dependencies and run via npm
In terminal:
  - $ cd frontend
  - $ echo VITE_API_URL='http://127.0.0.1:8000/' >> .env
  - $ npm install
  - $ npm run preview

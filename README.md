# Flask Notes API

## Description
A session-authenticated REST API for a personal notes app, built with Flask,
Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate and Flask-Bcrypt. Users can
sign up, log in and manage their own notes with full CRUD and pagination.
Users can never view or modify each other's notes.

## Installation
```bash
pipenv install
pipenv shell
cd server
flask db upgrade
cd ..
python seed.py
```

## Running
```bash
cd server
flask run -p 5555
```
The API runs at http://127.0.0.1:5555.
Seeded login: `user1` / `password123` (also `user2`, `user3`).

## Running the tests
```bash
pytest
```

## Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | /signup | No | Create an account and log in. Returns 201, or 422 if invalid or the username is taken. |
| POST | /login | No | Log in. Returns 200, or 401 if credentials are invalid. |
| DELETE | /logout | No | Log out. Returns 204. |
| GET | /check_session | Yes | Return the current user. Returns 200, or 401 if not logged in. |
| GET | /notes?page=&per_page= | Yes | Paginated list of your notes (default 5 per page, max 50). |
| POST | /notes | Yes | Create a note with `title` and `content`. Returns 201, or 422 if invalid. |
| GET | /notes/<id> | Yes | Get one of your notes. Returns 404 if it is not yours. |
| PATCH | /notes/<id> | Yes | Update your note's title or content. |
| DELETE | /notes/<id> | Yes | Delete your note. Returns 204. |

Unauthenticated requests to protected routes return 401. Requests for another
user's note return 404.

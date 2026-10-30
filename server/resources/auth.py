from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import User


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["Username and password are required."]}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already taken."]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password") or ""):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"errors": ["Invalid username or password."]}, 401


class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user:
            return user.to_dict(), 200
        return {"errors": ["Unauthorized"]}, 401

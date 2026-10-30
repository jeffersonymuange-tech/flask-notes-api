from functools import wraps

from flask import request, session
from flask_restful import Resource

from config import db
from models import Note

DEFAULT_PER_PAGE = 5
MAX_PER_PAGE = 50


def login_required(view):
    """Return a 401 unless someone is logged in."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return {"errors": ["Unauthorized"]}, 401
        return view(*args, **kwargs)

    return wrapper


def get_owned_note(note_id):
    """Look up a note, but only if it belongs to the current user.

    Someone else's note looks the same as a missing one, so callers
    can't tell which note ids exist.
    """
    return Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()


class NoteList(Resource):
    method_decorators = [login_required]

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", DEFAULT_PER_PAGE, type=int)
        per_page = max(1, min(per_page, MAX_PER_PAGE))

        # id breaks ties so notes created at the same instant keep a stable order
        pagination = (
            Note.query.filter_by(user_id=session["user_id"])
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "notes": [note.to_dict() for note in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        data = request.get_json() or {}

        try:
            note = Note(
                title=data.get("title"),
                content=data.get("content"),
                user_id=session["user_id"],
            )
            db.session.add(note)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return note.to_dict(), 201


class NoteDetail(Resource):
    method_decorators = [login_required]

    def get(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        return note.to_dict(), 200

    def patch(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404

        data = request.get_json() or {}

        try:
            for field in ("title", "content"):
                if field in data:
                    setattr(note, field, data[field])
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return note.to_dict(), 200

    def delete(self, note_id):
        note = get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204
from flask import request, session
from flask_restful import Resource

from config import db
from models import Note


def current_user_id():
    return session.get("user_id")


class NoteList(Resource):
    def get(self):
        user_id = current_user_id()
        if not user_id:
            return {"errors": ["Unauthorized"]}, 401

        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 5, type=int), 50)

        pagination = (
            Note.query.filter_by(user_id=user_id)
            .order_by(Note.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "notes": [n.to_dict() for n in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        user_id = current_user_id()
        if not user_id:
            return {"errors": ["Unauthorized"]}, 401

        data = request.get_json() or {}
        try:
            note = Note(
                title=data.get("title"),
                content=data.get("content"),
                user_id=user_id,
            )
            db.session.add(note)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        return note.to_dict(), 201


class NoteDetail(Resource):
    def _get_owned_note(self, note_id):
        """Return the note only if it belongs to the logged-in user."""
        return Note.query.filter_by(
            id=note_id, user_id=current_user_id()
        ).first()

    def get(self, note_id):
        if not current_user_id():
            return {"errors": ["Unauthorized"]}, 401
        note = self._get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404
        return note.to_dict(), 200

    def patch(self, note_id):
        if not current_user_id():
            return {"errors": ["Unauthorized"]}, 401
        note = self._get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404

        data = request.get_json() or {}
        try:
            for field in ("title", "content"):
                if field in data:
                    setattr(note, field, data[field])
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        return note.to_dict(), 200

    def delete(self, note_id):
        if not current_user_id():
            return {"errors": ["Unauthorized"]}, 401
        note = self._get_owned_note(note_id)
        if not note:
            return {"errors": ["Note not found."]}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204

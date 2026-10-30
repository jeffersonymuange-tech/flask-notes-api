from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import bcrypt, db

MIN_PASSWORD_LENGTH = 6


class User(db.Model):
    """An account holder who owns a collection of notes."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    notes = db.relationship(
        "Note", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password_hash(self):
        # Write-only: the hash is never exposed
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
            )
        self._password_hash = bcrypt.generate_password_hash(
            password.encode("utf-8")
        ).decode("utf-8")

    def authenticate(self, password):
        """Return True if the password matches the stored hash."""
        return bcrypt.check_password_hash(
            self._password_hash, password.encode("utf-8")
        )

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username is required.")
        return value.strip()

    def to_dict(self):
        return {"id": self.id, "username": self.username}


class Note(db.Model):
    """A single note that belongs to one user."""

    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="notes")

    @validates("title", "content")
    def validate_not_blank(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} is required.")
        return value.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
        }
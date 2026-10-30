from config import api, app
from resources.auth import CheckSession, Login, Logout, Signup
from resources.notes import NoteDetail, NoteList


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")


api.add_resource(NoteList, "/notes")
api.add_resource(NoteDetail, "/notes/<int:note_id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
from config import api, app
from resources.auth import CheckSession, Login, Logout, Signup

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

if __name__ == "__main__":
    app.run(port=5555, debug=True)

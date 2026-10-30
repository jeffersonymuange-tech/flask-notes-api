from config import app

import models  # noqa: F401  (registers tables with SQLAlchemy)

if __name__ == "__main__":
    app.run(port=5555, debug=True)

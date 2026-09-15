import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    project_root = os.path.dirname(
        os.path.dirname(__file__)
    )

    upload_folder = os.path.join(
        project_root,
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    # Register THIS db instance with Flask
    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.farms import farms_bp
    from app.routes.diagnosis import diagnosis_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(farms_bp)
    app.register_blueprint(diagnosis_bp)
    app.register_blueprint(pages_bp)

    return app
import os
from flask import Flask
from .extensions import db, migrate, login_manager
from . import models


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="sk",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite3",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)  # initialize db for this app
    migrate.init_app(app, db)  # initialize migrate for this app
    login_manager.init_app(app)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.create_all()

    # Register blueprints here

    from . import inventory

    app.register_blueprint(inventory.bp)
    app.add_url_rule("/", endpoint="home")

    from . import auth

    app.register_blueprint(auth.bp)

    return app

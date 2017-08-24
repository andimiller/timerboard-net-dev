from flask import Flask, render_template, send_from_directory, url_for, redirect
from flask.ext.assets import Environment, Bundle
from flask.ext.login import LoginManager
from assets import assets
from flask.ext.sqlalchemy import SQLAlchemy
from models import *
import redis_wrap

import os, json

login_manager = LoginManager()

users = redis_wrap.get_hash("timerboard_net_users")

@login_manager.user_loader
def load_user(user):
	if user in users:
		return User(json.loads(users[user]))
	else:
		flash("User not found.", "warning")



def create_app():   # We could pass a config object here
    app = Flask(__name__)
    app.debug = os.environ.get('TIMERBOARD_PRODUCTION', True)
    app.config.from_envvar("TIMERBOARD_SETTINGS")
    with open(os.environ["TIMERBOARD_SETTINGS"]) as fh:
        app.myconfig = json.loads(fh.read())
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///timerboard"
    # Register template filters here
    # app.add_template_filter(some_method)

    #app.config.from_object(config)
    #app.config.from_pyfile(config_filename)

    app.secret_key = os.urandom(24)
    assets.init_app(app)
    login_manager.init_app(app)

    app.db = SQLAlchemy(app)
    with app.app_context():
        app.db.create_all()

    from app.users.views import mod as users_blueprint
    from app.assets import mod as assets_blueprint
    from app.login import mod as login_blueprint
    app.register_blueprint(users_blueprint)
    app.register_blueprint(assets_blueprint)
    app.register_blueprint(login_blueprint)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

app = create_app()

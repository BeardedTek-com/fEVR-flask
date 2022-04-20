# External Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import LoginManager

# Flask app Setup
app = Flask(__name__)
app.config.from_file('config.json',load=json.load)

# Database Setup
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .models import User

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .main import api as api_blueprint
app.register_blueprint(api_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .setup import setup as setup_blueprint
app.register_blueprint(setup_blueprint)
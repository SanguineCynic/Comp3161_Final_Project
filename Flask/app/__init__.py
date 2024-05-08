from flask import Flask
from .config import Config
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from app import views
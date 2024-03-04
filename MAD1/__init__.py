from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from MAD1.database import db
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import Flask, render_template
from datetime import timedelta
from flask_restful import Api, Resource, reqparse


app = Flask(__name__)

current_directory = os.path.abspath(os.path.dirname(__file__))
relative_path = 'site.db'
database_path = os.path.join(current_directory, relative_path)

app.config['SECRET_KEY'] = "707e76b4d8feaa299d88943b7b3fd92709cc"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['PERMANENT_SESSION_LIFETIME']= timedelta(days=1)

db.init_app(app)



bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


app_context = app.app_context()
app_context.push()

from MAD1 import routes


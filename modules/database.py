from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



class Database:
    db = None
    bcrypt = None
    UserModel = None
    NewsModel = None
    def Initialize(app):
        Database.db = SQLAlchemy(app)
        Database.bcrypt = Bcrypt(app)
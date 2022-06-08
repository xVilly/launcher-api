from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from modules.database import Database
from modules.user import CreateUserEndpoint, AuthenticationEndpoint
from modules.session import Session
from config import Config, ProductionConfig

#App initialization
app = Flask(__name__)
api = Api(app)
app.config.from_object(Config)

#Database initialization
Database.Initialize(app)
db = Database.db
bcrypt = Database.bcrypt

#Sessions initialization
Session.Initialize()

# DB models
class UserModel(db.Model):
    """Database model for storing user data"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False) # hashed
    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"
Database.UserModel = UserModel


# Endpoints
api.add_resource(CreateUserEndpoint, "/createuser")
api.add_resource(AuthenticationEndpoint, "/auth")


if __name__ == "__main__":
    app.run(debug=True)
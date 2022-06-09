from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from modules.database import Database
from modules.user import CreateUserEndpoint, AuthenticationEndpoint, UserEndpoint, HeartBeatEndpoint
from modules.news import NewsEndpoint
from modules.session import Session
from config import Config, ProductionConfig
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

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
scheduler = BackgroundScheduler()
scheduler.add_job(func=Session.Update, trigger="interval", seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

# DB models
class UserModel(db.Model):
    """Database model for storing user data"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False) # hashed
    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"
Database.UserModel = UserModel
class NewsPostModel(db.Model):
    """Database model for storing news data"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    posted_at = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"News(id = {self.id}, title = {self.title}, content = {self.content}, author = {self.author}, posted_at = {self.posted_at})"
Database.NewsModel = NewsPostModel

# Endpoints
api.add_resource(CreateUserEndpoint, "/api/createuser")
api.add_resource(AuthenticationEndpoint, "/api/auth")
api.add_resource(UserEndpoint, "/api/user/<int:user_id>")
api.add_resource(HeartBeatEndpoint, "/api/hb")
api.add_resource(NewsEndpoint, "/api/news")


if __name__ == "__main__":
    app.run(debug=True)
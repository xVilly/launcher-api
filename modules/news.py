from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from modules.database import Database
from modules.args import createuser_args, getuser_args, authentication_args, news_args
from modules.session import Session
from datetime import datetime, timedelta
import secrets

# has to be lower than database model setting
NEWS_TITLE_MAX_LENGTH = 50
NEWS_CONTENT_MAX_LENGTH = 150

class NewsEndpoint(Resource):
    def post(self):
        headers = request.headers
        if 'Token' not in headers or not Session.CheckAuthorization(headers['Token'], request.remote_addr):
            abort(401, message="Authorization token is missing or is invalid")
        if 'D-Title' not in headers or len(headers['D-Title']) < 1:
            abort(400, message="News entry requires title header")
        if len(headers['D-Title']) > NEWS_TITLE_MAX_LENGTH:
            abort(400, message=f"Max title length supported: {NEWS_TITLE_MAX_LENGTH}")
        if 'D-Content' not in headers or len(headers['D-Content']) < 1:
            abort(400, message="News entry requires content header")
        if len(headers['D-Content']) > NEWS_TITLE_MAX_LENGTH:
            abort(400, message=f"Max content length supported: {NEWS_CONTENT_MAX_LENGTH}")
        session = Session.GetSessionByToken(headers['Token'])
        user = Database.UserModel.query.filter_by(id=session['user_id']).first()
        if not user:
            abort(404, message=f"User not found..")
        author = user.name
        news = Database.NewsModel(title=headers['D-Title'], content=headers['D-Content'], author=author, posted_at=datetime.utcnow().isoformat())
        Database.db.session.add(news)
        Database.db.session.commit()
        return {'message':'News succesfully posted'}, 201
    
    def get(self):
        args = news_args.parse_args()
        news = Database.NewsModel.query.filter_by(id=args['id']).first()
        if news:
            return {'id':news.id, 'title':news.title, 'content':news.content, 'author':news.author, 'posted_at':news.posted_at}, 200
        else:
            abort(404, message=f"News entry with id {args['id']} not found")
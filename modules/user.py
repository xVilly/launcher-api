from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from modules.database import Database
from modules.args import createuser_args, getuser_args, authentication_args
from modules.session import Session
from datetime import datetime, timedelta
import secrets

user_fields = {
    'name' : fields.String,
    'password': fields.String
}

#* Create new user
#* endpoint: /createuser
#* headers: D-Username, D-Password

class CreateUserEndpoint(Resource):
    def put(self):
        headers = request.headers
        if 'D-Username' not in headers:
            abort(401, message="Request is missing 'D-Username' header")
        elif 'D-Password' not in headers:
            abort(401, message="Request is missing 'D-Password' header")
        # Check if user exists
        find_user = Database.UserModel.query.filter_by(name=headers['D-Username']).first()
        if find_user:
            abort(409, message="User name is already taken..")
        # hash new password
        password_hash = Database.bcrypt.generate_password_hash(headers['D-Password'])
        # create new user object and insert it into the database
        user = Database.UserModel(name=headers['D-Username'], password=password_hash)
        Database.db.session.add(user)
        Database.db.session.commit()
        return {'message':'User successfully created', 'user_name':headers['D-Username']}, 201


#* User authentication
#* endpoint: /auth
#* headers: D-Username, D-Password

class AuthenticationEndpoint(Resource):
    def get(self):
        headers = request.headers
        if 'D-Username' not in headers:
            abort(401, message="Request is missing 'D-Username' header")
        elif 'D-Password' not in headers:
            abort(401, message="Request is missing 'D-Password' header")
        user = Database.UserModel.query.filter_by(name=headers['D-Username']).first()
        if not user:
            abort(404, message="User doesnt exist..")
        if Database.bcrypt.check_password_hash(user.password, headers['D-Password']):
            if not (Session.initialized and Session.allow_authentication):
                abort(400, message="Server doesn't accept new authentications at the moment ..")
            if Session.UserAlreadyAuthenticated(user.id):
                abort(400, message="User is already authenticated ..")
            token = secrets.token_urlsafe(40)
            if Session.TokenExists(token):
                abort(400, message="Token already exists .. failed to authenticate")
            ip_address = request.remote_addr
            exp = datetime.utcnow() + timedelta(minutes=Session.TOKEN_LIFETIME_MINUTES)
            session_data = {'token':token, 'user_id':user.id, 'ip_address':ip_address, 'exp':exp.isoformat()}

            if Session.RegisterSession(session_data):
                return {'authorization_token':token, 'message':'User authenticated', 'user_name':user.name, 'exp':session_data['exp']}, 200
            else:
                abort(400, message="Failed to authenticate .. try again later ..")
            
        else:
            abort(406, message="Password doesn't match..")

#* Session heartbeat request
#* endpoint: /hb
#* headers: Token, New

class HeartBeatEndpoint(Resource):
    def put(self):
        headers = request.headers
        if 'Token' not in headers or not Session.CheckAuthorization(headers['Token'], request.remote_addr):
            abort(401, message="Authorization token is missing or is invalid")
        session = Session.GetSessionByToken(headers['Token'])
        exp = datetime.utcnow() + timedelta(minutes=Session.TOKEN_LIFETIME_MINUTES)
        session['exp'] = exp.isoformat()
        return {'message':'Heartbeat successful', 'exp':session['exp']}, 200

#* User info request (AUTHORIZATION REQUIRED)
#* endpoint: /user/<int:user_id>
#* headers: Token

class UserEndpoint(Resource):
    def get(self, user_id):
        headers = request.headers
        if 'Token' not in headers or not Session.CheckAuthorization(headers['Token'], request.remote_addr):
            abort(401, message="Authorization token is missing or is invalid")
        return {'session_data':Session.GetSessionByToken(headers['Token'])}

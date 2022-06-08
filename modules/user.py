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
#* headers: createuser_args

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
#* headers: authentication_args

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
            exp = datetime.utcnow() + timedelta(minutes=30)
            session_data = {'token':token, 'user_id':user.id, 'ip_address':ip_address, 'exp:':exp.isoformat()}

            if Session.RegisterSession(session_data):
                return {'authorization_token':token, 'message':'User authenticated', 'data':session_data}, 200
            else:
                abort(400, message="Failed to authenticate .. try again later ..")
            
        else:
            abort(406, message="Password doesn't match..")
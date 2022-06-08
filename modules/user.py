from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from modules.database import Database
from modules.args import createuser_args, getuser_args, authentication_args
import secrets

user_fields = {
    'name' : fields.String,
    'password': fields.String
}

#* Create new user
#* endpoint: /createuser
#* headers: createuser_args

class CreateUserEndpoint(Resource):
    @marshal_with(user_fields)
    def get(self):
        args = getuser_args.parse_args()
        result = Database.UserModel.query.filter_by(name=args['name']).first()
        return result

    def put(self):
        args = createuser_args.parse_args()
        # Check if user exists
        find_user = Database.UserModel.query.filter_by(name=args['name']).first()
        if find_user:
            abort(409, message="User name is already taken..")
        # hash new password
        password_hash = Database.bcrypt.generate_password_hash(args['password'])
        # create new user object and insert it into the database
        user = Database.UserModel(name=args['name'], password=password_hash)
        Database.db.session.add(user)
        Database.db.session.commit()
        return {'message':'User successfully created', 'user_name':args['name']}, 201


#* User authentication
#* endpoint: /auth
#* headers: authentication_args

class AuthenticationEndpoint(Resource):
    def get(self):
        args = authentication_args.parse_args()
        user = Database.UserModel.query.filter_by(name=args['username']).first()
        if not user:
            abort(404, message="User doesnt exist..")
        if Database.bcrypt.check_password_hash(user.password, args['password']):
            token = secrets.token_urlsafe(40)
            return {'authorization_token':token, 'message':'User authenticated'}, 200
        else:
            abort(406, message="Password doesn't match..")
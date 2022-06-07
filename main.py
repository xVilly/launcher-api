from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'RqzAt8?$2b./z~jm)/=%8;4y!7j2pGY!'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#* User and account creation
#* endpoint: /createuser
class UserModel(db.Model):
    """Database model for storing user data"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False) # hashed
    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"

user_fields = {
    'name' : fields.String,
    'password': fields.String
}

createuser_args = reqparse.RequestParser()
createuser_args.add_argument("name", type=str, help="Provide name for the new user", required=True)
createuser_args.add_argument("password", type=str, help="Provide password for the new user", required=True)

getuser_args = reqparse.RequestParser()
getuser_args.add_argument("name", type=str, help="Provide user name", required=True)

class CreateUserEndpoint(Resource):
    @marshal_with(user_fields)
    def get(self):
        args = getuser_args.parse_args()
        result = UserModel.query.filter_by(name=args['name']).first()
        return result

    def put(self):
        args = createuser_args.parse_args()
        # Check if user exists
        find_user = UserModel.query.filter_by(name=args['name']).first()
        if find_user:
            abort(409, message="User name is already taken..")
        # hash new password
        password_hash = bcrypt.generate_password_hash(args['password'])
        # create new user object and insert it into the database
        user = UserModel(name=args['name'], password=password_hash)
        db.session.add(user)
        db.session.commit()
        return {'message':'User successfully created', 'user_name':args['name']}, 201

#* User authentication
#* endpoint /auth
authentication_args = reqparse.RequestParser()
authentication_args.add_argument("username", type=str, help="Provide user name for the authentication", required=True)
authentication_args.add_argument("password", type=str, help="Provide user password for the authentication", required=True)
authentication_args.add_argument("data", type=dict)

class AuthenticationEndpoint(Resource):
    def get(self):
        args = authentication_args.parse_args()
        user = UserModel.query.filter_by(name=args['username']).first()
        if not user:
            abort(404, message="User doesnt exist..")
        if bcrypt.check_password_hash(user.password, args['password']):
            token = secrets.token_urlsafe(40)
            return {'authorization_token':token, 'message':'User authenticated'}, 200
        else:
            abort(406, message="Password doesn't match..")

api.add_resource(CreateUserEndpoint, "/createuser")
api.add_resource(AuthenticationEndpoint, "/auth")

if __name__ == "__main__":
    app.run(debug=True)
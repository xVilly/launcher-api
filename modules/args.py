from flask_restful import reqparse

# Used in '/createuser' endpoint
createuser_args = reqparse.RequestParser()
createuser_args.add_argument("name", type=str, help="Provide name for the new user", required=True)
createuser_args.add_argument("password", type=str, help="Provide password for the new user", required=True)

getuser_args = reqparse.RequestParser()
getuser_args.add_argument("name", type=str, help="Provide user name", required=True)

# Used in '/auth' endpoint
authentication_args = reqparse.RequestParser()
authentication_args.add_argument("username", type=str, help="Provide user name for the authentication", required=True)
authentication_args.add_argument("password", type=str, help="Provide user password for the authentication", required=True)
authentication_args.add_argument("data", type=dict)

news_args = reqparse.RequestParser()
news_args.add_argument("id", type=int, help="Select news id that you want to request", required=True)
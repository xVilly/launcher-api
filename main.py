from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

name_arg_template = reqparse.RequestParser()
name_arg_template.add_argument("name", type=str, help="Provide your name (string)", required=True)

class HelloWorld(Resource):
    def get(self, _id):
        args = name_arg_template.parse_args()
        return {'hello':f'{_id} said hello world', 'args':args}

api.add_resource(HelloWorld, "/<int:_id>")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self, name):
        return {'hello':f'{name} said hello world'}

api.add_resource(HelloWorld, "/<int:name>")

print("Hello world")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class NewsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"News(title = {self.title})"

news_model_fields = {
    'id' : fields.Integer,
    'title' : fields.String
}

#! USE THIS ONLY ONCE (Creates a new database)
##db.create_all()##

name_arg_template = reqparse.RequestParser()
name_arg_template.add_argument("name", type=str, help="Provide your name (string)", required=True)

class News(Resource):

    @marshal_with(news_model_fields)
    def get(self, news_id):
        result = NewsModel.query.filter_by(id=news_id).first()
        if not result:
            abort(404, message=f'News with id {news_id} not found')
        return result, 200

api.add_resource(News, "/news/<int:news_id>")

if __name__ == "__main__":
    app.run(debug=True)
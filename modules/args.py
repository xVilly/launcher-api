from flask_restful import reqparse

news_args = reqparse.RequestParser()
news_args.add_argument("id", type=int, help="Select news id that you want to request", required=True)
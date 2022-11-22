from flask import Flask, jsonify
from sqlalchemy import create_engine
from datetime import datetime
from flask_restx import Api, Namespace, Resource, \
    reqparse, inputs, fields

user = "schedulin"
passw = "MySQLIsFun"
host = "35.231.228.133"
database = "fakenews"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = host

api = Api(app, version = '1.0',
    title = 'The REAL Fake News API',
    description = """
        The Fake News API is an API to manage reservations
        inside a neighborhood community.""",
    contact = "frangardel@gmail.com",
    endpoint = "/fakenews/api/v1"
)

news_model = api.model(
    'news', {
        'id': fields.Integer,
        'title': fields.String(required = True),
        'text': fields.String,
        'subject': fields.String(enum = ['POLITICS', 'NEWS']),
        'fake': fields.Integer(min=0, max=1),
        'date': fields.date
})

def connect():
    db = create_engine(
    'mysql+pymysql://{0}:{1}@{2}/{3}' \
        .format(user, passw, host, database), \
    connect_args = {'connect_timeout': 10})
    conn = db.connect()
    return conn

def disconnect(conn):
    conn.close()

basics = Namespace('basics',
    description = 'Basic operations',
    path='/api/v1')
api.add_namespace(basics)

@basics.route('/hello')
class hello_swagger(Resource):

    def get(self):
        return 'Hello from Flask!'

@basics.route('/bye')
class bye_swagger(Resource):

    def get(self):
        return 'Bye bye from Flask!'

news = Namespace('news',
    description = 'All operations related to news',
    path='/fakenews/api/v1')
api.add_namespace(news)

allnews_creation_parser = reqparse.RequestParser()
allnews_creation_parser.add_argument('fake', type = str,
        help = 'It indicates whether all required news are fake or not. \
                Expected Values: YES - all fake news; NO - all true news.',
        location = 'form')
allnews_creation_parser.add_argument('date', type = str,
        help = 'Please enter the date in which the news was published. \
                Expected format: DD/MM/YYYY.',
        location = 'form')

@news.route("/allnews")
class isFake(Resource):

    @api.doc(parser = allnews_creation_parser)
    @api.expect(allnews_creation_parser)
    def get(self):
        args = news_creation_parser.parse_args()
        date = args['date']
        fake = args['fake']
        connection = connect()
        select = """
            SELECT *
            FROM news
            WHERE deletion_date IS NULL
            LIMIT 10;"""
        result = connection.execute(select).fetchall()
        disconnect(connection)
        return jsonify({'result': [dict(row) for row in result]})

news_creation_parser = reqparse.RequestParser()
news_creation_parser.add_argument('title', type = str,
        help = 'The title of the news.',
        location = 'form')
news_creation_parser.add_argument('text', type = str,
        help = 'The text of the news',
        location = 'form')
news_creation_parser.add_argument('subject', type = str,
        help = 'The subject of the news. Values are: ACTIVE, INACTIVE',
        location = 'form')
news_creation_parser.add_argument('fake', type = str,
        help = 'It indicates whether all required news are fake or not. \
                Expected Values: YES - all fake news; NO - all true news.',
        location = 'form')
news_creation_parser.add_argument('date', type = str,
        help = 'Please enter the date in which the news was published. \
                Expected format: DD/MM/YYYY.',
        location = 'form')

@news.route("/news")
class create_news(Resource):

    @api.doc(parser = news_creation_parser)
    @api.expect(news_creation_parser)
    def post(self):
        args = news_creation_parser.parse_args()
        title = args['title']
        text = args['text']
        subject = args['subject']
        date = args['date']
        creation_date = datetime.now()
        connection = connect()
        insert = """
            INSERT INTO user (name, email, status, creation_date, modification_date)
                VALUES ('{0}', '{1}', '{2}', '{3}', '{3}')""" \
                .format(title, text, subject, date, creation_date)
        connection.execute(insert)
        disconnect(connection)
        return jsonify({'result': "OK"})

news_update_parser = reqparse.RequestParser()
news_update_parser.add_argument('fake', type = str,
        help = 'It indicates whether all required news are fake or not. \
                Expected Values: YES - all fake news; NO - all true news.',
        location = 'form')
news_update_parser.add_argument('subject', type = str,
        help = 'The subject of the news. Values are: ACTIVE, INACTIVE',
        location = 'form')

@news.route("/news/<string:id>")
@news.doc(params = {'id': 'The ID of the news'})
class select_news(Resource):

    @api.response(404, "NEWS not found")
    def get(self, id):
        id = int(id)
        connection = connect()
        select = """
            SELECT *
            FROM news
            WHERE id = {0}
                AND deletion_date IS NULL;""".format(id)
        result = connection.execute(select).fetchall()
        disconnect(connection)
        return jsonify({'result': [dict(row) for row in result]})

    @api.doc(parser = news_update_parser)
    @api.expect(news_update_parser)
    def put(self, id):
        id = int(id)
        args = news_update_parser.parse_args()
        status = args['status']
        modification_date = datetime.now()
        connection = connect()
        update = """
            UPDATE news
            SET status = '{0}',
                modification_date = '{1}'
            WHERE id = {2}
                AND deletion_date IS NULL""".format(status, modification_date, id)
        connection.execute(update)
        disconnect(connection)
        return jsonify({'result': "OK"})

    def delete(self, id):
        id = int(id)
        deletion_date = datetime.now()
        connection = connect()
        delete = """
            UPDATE news
            SET deletion_date = '{0}'
            WHERE id = {1}""".format(deletion_date, id)
        connection.execute(delete)
        disconnect(connection)
        return jsonify({'result': "OK"})
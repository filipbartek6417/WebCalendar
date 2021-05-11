from flask import Flask, abort
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import date

# app config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webCalendar.db'
db = SQLAlchemy(app)
api = Api(app)
# Create 2 parsers, one for adding events, the other for requesting them
addingParser = reqparse.RequestParser()
requestParser = reqparse.RequestParser()
addingParser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)
addingParser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! "
         "The correct format is YYYY-MM-DD!",
    required=True
)
requestParser.add_argument(
    'start_time',
    type=inputs.date,
    help="The start_time with the correct format is required! "
         "The correct format is YYYY-MM-DD!"
)
requestParser.add_argument(
    'end_time',
    type=inputs.date,
    help="The end_time with the correct format is required! "
         "The correct format is YYYY-MM-DD!"
)


# Create a DB model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __str__(self):
        return f'{self.id}, {self.event}, {self.date}'


# db.create_all()  # Creates a DB
# Event.query.delete()  # These 2 lines erase your DB
# db.session.commit()

# fields by which @marshal_with operates
resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.String
}


# home page
class SlashResource(Resource):
    def get(self):
        return 'Home Page'


# all events page
class EventResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = requestParser.parse_args()
        if args['start_time']:
            if args['end_time']:
                return Event.query.filter \
                    (args['start_time'] <= Event.date,
                     Event.date < args['end_time']).all()
            return Event.query.filter \
                (args['start_time'] <= Event.date).all()
        elif args['end_time']:
            return Event.query.filter \
                (Event.date < args['end_time']).all()
        return Event.query.all()

    def post(self):
        args = addingParser.parse_args()
        db.session.add(Event(event=args['event'],
                             date=args['date']))
        db.session.commit()
        return {
            'message': 'The event has been added!',
            'event': args['event'],
            'date': args['date'].strftime('%Y-%m-%d')
        }


# today's event page
class EventTodayResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        print(type(Event.date))
        print(type(date.today()))
        return Event.query.filter \
            (Event.date == date.today()).all()


# individual event page
class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {
            'message': 'The event has been deleted!',
        }


# route handling
api.add_resource(SlashResource, '/')
api.add_resource(EventTodayResource, '/event/today')
api.add_resource(EventResource, '/event')
api.add_resource(EventByID, '/event/<int:event_id>')
# flask run
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

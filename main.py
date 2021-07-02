import argparse
from flask import Flask
import sys
from flask_restful import reqparse, Api, marshal_with, Resource, fields
import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask import abort

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
api = Api(app)

resource_fields = {
    'id': fields.Integer,
    "event": fields.String,
    'date': fields.String,
}

#Class to for the event/id endpoint
class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        for i in db.session.query(Event.id, Event.event, Event.date).filter(Event.id == event_id).all():
            date_time = datetime.datetime.strptime(dict(i)['date'], '%Y-%m-%d %H:%M:%S')
            dict_results = dict(i)
            dict_results.update({'date': date_time.strftime('%Y-%m-%d')})

        return dict_results

    @staticmethod
    def delete(event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            Event.query.filter(Event.id == event_id).delete()
            db.session.commit()
            return {"message": "The event has been deleted!"}



class Event(db.Model):
    __tablename__ = 'Event'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)

db.create_all()

#Class for the /event endpoint
class Eventlist(Resource):
    @marshal_with(resource_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('start_time', type=str, required=False)
        parser.add_argument('end_time', type=str, required=False)
        args = parser.parse_args()
        empty_array = [] #checking if the endpoint is /event or /event?start_time=&end_time=

        if args['start_time'] is None or args['end_time'] is None:
            for i in db.session.query(Event.id, Event.event, Event.date).filter().all():
                date_time = datetime.datetime.strptime(dict(i)['date'], '%Y-%m-%d %H:%M:%S')
                my_dict = dict(i)
                my_dict.update({'date': date_time.strftime('%Y-%m-%d')})
                print(my_dict['date'])
                empty_array.append(my_dict)
            return empty_array
        else:
            for i in db.session.query(Event.id, Event.event, Event.date).filter(Event.date >= datetime.datetime.strptime(args['start_time'], '%Y-%m-%d').strftime(
                    '%Y-%m-%d %H:%M:%S')).filter(Event.date <= datetime.datetime.strptime(args['end_time'], '%Y-%m-%d').strftime(
                         '%Y-%m-%d %H:%M:%S')).all():
                date_time = datetime.datetime.strptime(dict(i)['date'], '%Y-%m-%d %H:%M:%S')
                my_dict = dict(i)
                my_dict.update({'date': date_time.strftime('%Y-%m-%d')})
                print(my_dict['date'])
                empty_array.append(my_dict)
            return empty_array

    @staticmethod
    def post():
        args = parser.parse_args()

        event = Event(event=args['event'], date=args['date'])

        db.session.add(event)
        db.session.commit()
        args['id'] = event.id
        args['message'] = 'The event has been added!'

        dicto = {
            "id": args['id'],
            "message": args['message'],
            "event": args['event'],
            "date": args['date'].strftime('%Y-%m-%d')
        }
        return dicto


#        return {'id': event.id, 'event': event.event, 'date': event.date}

#Class to for the event/today endpoint

class EventToday(Resource):
    @marshal_with(resource_fields)
    def get(self):
        empty_array = []
        for i in db.session.query(Event.id, Event.event, Event.date).filter(
                Event.date == date.today().strftime('%Y-%m-%d %H:%M:%S')).all():
            date_time = datetime.datetime.strptime(dict(i)['date'], '%Y-%m-%d %H:%M:%S')
            my_dict = dict(i)
            my_dict.update({'date': date_time.strftime('%Y-%m-%d')})
            print(my_dict['date'])
            empty_array.append(my_dict)
        return empty_array


# checking if the date format is valid
def valid_date(string):
    try:
        return datetime.datetime.strptime(string, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(string)
        raise argparse.ArgumentTypeError(msg)


parser = reqparse.RequestParser()
api.add_resource(Eventlist, '/event')
api.add_resource(EventToday, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')

parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

parser.add_argument(
    'date',
    type=valid_date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()


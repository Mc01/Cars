import json
import os
from collections import defaultdict

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


class DatabaseConnection(object):
    def __init__(self, env_file='.env'):
        load_dotenv(dotenv_path=env_file)
        self.db_protocol = 'postgresql'
        self.db_username = os.getenv('POSTGRES_USER')
        self.db_password = os.getenv('POSTGRES_PASSWORD')
        self.db_host = os.getenv('POSTGRES_HOST')
        self.db_port = os.getenv('POSTGRES_PORT')
        self.db_database = os.getenv('POSTGRES_DB')

    def get_config(self):
        uri = 'SQLALCHEMY_DATABASE_URI'
        mods = 'SQLALCHEMY_TRACK_MODIFICATIONS'
        return {
            uri: ''
                 f'{self.db_protocol}://'
                 f'{self.db_username}:'
                 f'{self.db_password}@'
                 f'{self.db_host}:'
                 f'{self.db_port}/'
                 f'{self.db_database}',
            mods: False,
        }


app = Flask(__name__)
app.config.update(DatabaseConnection(env_file='server/.env').get_config())
db = SQLAlchemy(app)


with open('parser/cache/params.json') as f:
    data = json.load(f)


builds = defaultdict(list)


for car in data:
    car_name = car['name']
    for spec in car['specs']:
        spec_params = spec['params']
        all_params = dict([param_pair.values() for param_pair in spec_params])
        car_build = {
            'transmission': all_params.get('Rodzaj skrzyni'),
            'engine_type': all_params.get('Typ silnika'),
            'engine_size': all_params.get('Pojemność skokowa'),
            'engine_power': all_params.get('Moc silnika'),
            'weight': all_params.get('Minimalna masa własna pojazdu (bez obciążenia)'),
            'clearance': all_params.get('Prześwit'),
            'acceleration': all_params.get('Przyspieszenie (od 0 do 100km/h)'),
            'fuel_in_city': all_params.get('Spalanie w mieście'),
            'version': spec['name'],
            'transmission_name': all_params.get('Nazwa skrzyni'),
            'steps': all_params.get('Liczba stopni'),
            'gears': all_params.get('Liczba biegów'),
            'engine_torque': all_params.get('Maksymalny moment obrotowy'),
            'engine_charged': all_params.get('Doładowanie'),
            'engine_cylinders': all_params.get('Liczba cylindrów'),
            'wheel_drive': all_params.get('Rodzaj napędu'),
            'max_speed': all_params.get('Prędkość maksymalna'),
            'fuel_out_city': all_params.get('Spalanie w trasie (na autostradzie)'),
            'fuel_mixed': all_params.get('Średnie spalanie (cykl mieszany)'),
            'fuel_tank': all_params.get('Pojemność zbiornika paliwa'),
            'fuel_range_mixed': all_params.get('Zasięg (cykl mieszany)'),
        }
        builds[car_name].append(car_build)

print(builds)


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.name}'


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    model = db.Column('Model', backref=db.backref('builds', lazy=True))
    version = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.version}'


db.create_all()


@app.route('/')
def hello():
    return 'Elo'

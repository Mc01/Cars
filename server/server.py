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
            'version': spec['name'],
            'transmission_name': all_params.get('Nazwa skrzyni'),
            'steps': all_params.get('Liczba stopni'),
            'gears': all_params.get('Liczba biegów'),
            'transmission': all_params.get('Rodzaj skrzyni'),
            'engine_type': all_params.get('Typ silnika'),
            'engine_size': all_params.get('Pojemność skokowa'),
            'engine_power': all_params.get('Moc silnika'),
            'engine_torque': all_params.get('Maksymalny moment obrotowy'),
            'engine_charged': all_params.get('Doładowanie'),
            'engine_cylinders': all_params.get('Liczba cylindrów'),
            'weight': all_params.get('Minimalna masa własna pojazdu (bez obciążenia)'),
            'length': all_params.get('Długość'),
            'clearance': all_params.get('Prześwit'),
            'acceleration': all_params.get('Przyspieszenie (od 0 do 100km/h)'),
            'max_speed': all_params.get('Prędkość maksymalna'),
            'wheel_drive': all_params.get('Rodzaj napędu'),
            'all_wheel_drive': all_params.get('Nazwa 4x4'),
            'cargo_space': all_params.get('Minimalna pojemność bagażnika (siedzenia rozłożone)'),
            'fuel_in_city': all_params.get('Spalanie w mieście'),
            'fuel_out_city': all_params.get('Spalanie w trasie (na autostradzie)'),
            'fuel_mixed': all_params.get('Średnie spalanie (cykl mieszany)'),
            'fuel_tank': all_params.get('Pojemność zbiornika paliwa'),
            'fuel_range_mixed': all_params.get('Zasięg (cykl mieszany)'),
            'fuel_range_in_city': all_params.get('Zasięg (miasto)'),
            'fuel_range_out_city': all_params.get('Zasięg (autostrada)'),
        }
        builds[car_name].append(car_build)


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.name}'


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    model = db.relationship('Model', backref=db.backref('builds', lazy=True))
    version = db.Column(db.String(255), unique=True, nullable=False)
    transmission_name = db.Column(db.String(255), nullable=True)
    steps = db.Column(db.String(255), nullable=True)
    gears = db.Column(db.String(255), nullable=True)
    transmission = db.Column(db.String(255), nullable=True)
    engine_type = db.Column(db.String(255), nullable=True)
    engine_size = db.Column(db.String(255), nullable=True)
    engine_power = db.Column(db.String(255), nullable=True)
    engine_torque = db.Column(db.String(255), nullable=True)
    engine_charged = db.Column(db.String(255), nullable=True)
    engine_cylinders = db.Column(db.String(255), nullable=True)
    weight = db.Column(db.String(255), nullable=True)
    length = db.Column(db.String(255), nullable=True)
    clearance = db.Column(db.String(255), nullable=True)
    acceleration = db.Column(db.String(255), nullable=True)
    max_speed = db.Column(db.String(255), nullable=True)
    wheel_drive = db.Column(db.String(255), nullable=True)
    all_wheel_drive = db.Column(db.String(255), nullable=True)
    cargo_space = db.Column(db.String(255), nullable=True)
    fuel_in_city = db.Column(db.String(255), nullable=True)
    fuel_out_city = db.Column(db.String(255), nullable=True)
    fuel_mixed = db.Column(db.String(255), nullable=True)
    fuel_tank = db.Column(db.String(255), nullable=True)
    fuel_range_mixed = db.Column(db.String(255), nullable=True)
    fuel_range_in_city = db.Column(db.String(255), nullable=True)
    fuel_range_out_city = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'{self.version}'


db.create_all()


for model_name in builds.keys():
    model = Model.query.filter_by(name=model_name).first()
    if not model:
        model = Model(name=model_name)
    for build_config in builds[model_name]:
        build = Build.query.filter_by(version=build_config['version']).first()
        if not build:
            Build(model=model, **build_config)
    db.session.add(model)
    db.session.commit()


@app.route('/')
def hello():
    return 'Elo'

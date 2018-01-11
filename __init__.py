from flask import Flask, request
from flask_mongoengine import MongoEngine

import mongoengine

from flask import json
from cerberus import Validator
from errors.base import FailedUpdatingUser, UserNotFound, OccupationNotFound
from models.users import Therapist, Patient, Occupation, TimeSlot
from services.users import validate_user_login, update_users_token, \
    register_user, generate_restriction, get_occupation, register_occupation, \
    get_therapists_by_occupation
import schemas
import utils


def init_db():
    Therapist.ensure_indexes()
    Patient.ensure_indexes()
    Occupation.ensure_indexes()
    TimeSlot.ensure_indexes()


db = MongoEngine()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['MONGODB_DB'] = 'shikum'
app.config['MONGODB_HOST'] = '127.0.0.1'
app.config['MONGODB_PORT'] = 27017
db.init_app(app)
init_db()

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/users/login/patient', methods=['POST'])
def patient_login():
    return login_handler(Patient)


@app.route('/users/login/therapist', methods=['POST'])
def therapist_login():
    return login_handler(Therapist)


@app.route('/users/register/patient', methods=['POST'])
def patient_register():
    return register_handler(Patient, schemas.register_schema)


@app.route('/users/register/therapist', methods=['POST'])
def therapist_register():
    return register_handler(Therapist, schemas.register_therapist_schema)


@app.route('/<user_id>/restriction', methods=['POST'])
def add_restriction(user_id):
    data = request.json
    try:
        user_obj = get_user(user_id)
        validate = Validator(schemas.restriction_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert start time and end time in millis"}), 400
        start_time, end_time, description = data['start_time'], data['end_time'], data['description']
        if not utils.from_millis(start_time) or not utils.from_millis(end_time):
            return json.dumps({"success": False, "error": "Invalid time in milliseconds"}), 400
        if not generate_restriction(user_obj, utils.from_millis(start_time), utils.from_millis(end_time), description):
            return json.dumps({"success": False, "error": "Restrictions overlap"})
        return json.dumps({"success": True})
    except UserNotFound:
        return json.dumps({"success": False, "error": "User not found"}), 404


@app.route('/occupation', methods=['POST'])
def add_occupation():
    data = request.json
    try:
        validate = Validator(schemas.occupation_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert an occupation name in String"}), 400
        occupation_name = data['occupation_name']
        occupation = register_occupation(occupation_name)
        return json.dumps({"success": True, "id": str(occupation.id)})
    except mongoengine.NotUniqueError:
        return json.dumps({"success": False, "error": "Occupation already exists"})



@app.route('/therapists/<occupation_id>', methods=['GET'])
def get_occupation_therapists(occupation_id):
    try:
        occupation_obj = get_occupation(occupation_id)
        therapists = get_therapists_by_occupation(occupation_id)
        return json.dumps({"success": True, "Therapists": therapists.to_json()})
    except OccupationNotFound:
        return json.dumps({"success": False, "error": "Occupation not exits"})


def login_handler(cls):
    data = request.json
    validate = Validator(schemas.login_schema).validate(data)
    if not validate:
        return json.dumps({"success": False, "error": "Bad request, please insert username and password attributes"}), 400
    username, password = data['username'], data['password']
    try:
        user_obj = validate_user_login(cls, username, password)
        if user_obj:
            token = update_users_token(user_obj)
            return json.dumps({'success': True, 'token': token})
        return json.dumps({'success': False, 'error': 'Authentication failed'}), 401
    except UserNotFound:
        return json.dumps({"success": False, "error": "User not found"}), 404
    except FailedUpdatingUser:
        return json.dumps({"success": False, "error": "Failed saving user"}), 500


def register_handler(cls, schema):
    data = request.json
    validate = Validator(schema).validate(data)
    if not validate:
        return json.dumps({"success": False, "error": "Bad request, please insert username, password and occupation"}), 400
    username, password, occupation = data['username'], data['password'], data.get('occupation', None)
    if not username.isalnum():
        return json.dumps({"success": False, "error": "Please use alpha numeric charachters only"}), 400
    if len(password) < 8:
        return json.dumps({"success": False, "error": "Password minimum length is 8"}), 400
    try:
        user_obj = register_user(cls, username, password, occupation)
    except mongoengine.NotUniqueError:
        return json.dumps({"success": False, "error": "Username already exists"}), 409

    return json.dumps({"success": True})


if __name__ == "__main__":
    app.run(debug=True)

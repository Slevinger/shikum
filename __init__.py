from flask import Flask, request
from flask_mongoengine import MongoEngine

import mongoengine

from flask import json
from cerberus import Validator
from errors.base import FailedUpdatingUser, UserNotFound, OccupationNotFound
from services.DBUtils import get_user
from services.users import validate_user_login, update_users_token, register_user, generate_restriction, \
    get_occupation, get_occupation_by_name, register_occupation, add_therapist_to_occupation, \
    add_patient_to_occupation, get_users_list_from_ids, get_users_list_from_ids
import schemas
import utils

db = MongoEngine()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['MONGODB_DB'] = 'shikum'
app.config['MONGODB_HOST'] = '127.0.0.1'
app.config['MONGODB_PORT'] = 27017
db.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/users/login', methods=['POST'])
def login():
    data = request.json
    validate = Validator(schemas.login_schema).validate(data)
    if not validate:
        return json.dumps({"success": False, "error": "Bad request, please insert username and password attributes"}), 400
    username, password = data['username'], data['password']
    try:
        user_obj = validate_user_login(username, password)
        if user_obj:
            token = update_users_token(user_obj)
            return json.dumps({'success': True, 'token': token})
        return json.dumps({'success': False, 'error': 'Authentication failed'}), 401
    except UserNotFound:
        return json.dumps({"success": False, "error": "User not found"}), 404
    except FailedUpdatingUser:
        return json.dumps({"success": False, "error": "Failed saving user"}), 500


@app.route('/users/register', methods=['POST'])
def register():
    data = request.json
    validate = Validator(schemas.register_schema).validate(data)
    if not validate:
        return json.dumps({"success": False, "error": "Bad request, please insert username, password and role attributes"}), 400
    username, password, role = data['username'], data['password'], data['role']
    if not username.isalnum():
        return json.dumps({"success": False, "error": "Please use alpha numeric charachters only"}), 400
    if len(password) < 8:
        return json.dumps({"success": False, "error": "Password minimum length is 8"}), 400
    if role not in ['Patient', 'Therapist']:
        return json.dumps({"success": False, "error": "Invalid role"}), 400
    try:
        user_obj = register_user(username, password, role)
    except mongoengine.NotUniqueError:
        return json.dumps({"success": False, "error": "Username already exists"}), 409

    return json.dumps({"success": True})


@app.route('/<user_id>/restriction', methods=['POST'])
def add_restriction(user_id):
    data = request.json
    try:
        user_obj = get_user(user_id)
        validate = Validator(schemas.restriction_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert start time and end time in millis"}), 400
        start_time, end_time,reason = data['start_time'], data['end_time'], data['reason']
        if not utils.from_millis(start_time) or not utils.from_millis(end_time):
            return json.dumps({"success": False, "error": "Invalid time in milliseconds"}), 400
        if not generate_restriction(user_obj, utils.from_millis(start_time), utils.from_millis(end_time), reason):
            return json.dumps({"success": False, "error": "Restrictions overlap"})
        return  json.dumps({"success": True})
    except UserNotFound:
        return json.dumps({"success": False, "error": "User not found"}), 404


@app.route('/add/occupation/therapist/<occupation_id>', methods=['POST'])
def add_occupation_therapist(occupation_id):
    data = request.json
    try:
        validate = Validator(schemas.therapist_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert an occupation name in String"}), 400
        occupation_obj = get_occupation(occupation_id)
        therapist_id = data['therapist_id']
        therapist_obj = get_user(therapist_id)
        add_therapist_to_occupation(occupation_obj,therapist_obj)
        return  json.dumps({"success": True})
    except UserNotFound:
        return json.dumps({"success": False, "error": "No such therapist in the system"})
    except OccupationNotFound:
        return json.dumps({"success": False, "error": "No such Occupation in the system"})


@app.route('/add/occupation/patient/<occupation_id>', methods=['POST'])
def add_occupation_patient(occupation_id):
    data = request.json
    try:
        validate = Validator(schemas.therapist_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert an occupation name in String"}), 400
        occupation_obj = get_occupation(occupation_id)
        patient_id = data['patient_id']
        patient_obj = get_user(patient_id)
        add_patient_to_occupation(occupation_obj,patient_obj)
        return  json.dumps({"success": True})
    except UserNotFound:
        return json.dumps({"success": False, "error": "No such therapist in the system"})
    except OccupationNotFound:
        return json.dumps({"success": False, "error": "No such Occupation in the system"})

@app.route('/add/occupation', methods=['POST'])
def add_occupation():
    data = request.json
    try:
        validate = Validator(schemas.occupation_schema).validate(data)
        if not validate:
            return json.dumps({"success": False, "error": "Bad request, please insert an occupation name in String"}), 400
        occupation_name = data['occupation_name']
        occupation_obj = get_occupation_by_name(occupation_name)
        if occupation_obj:
            return json.dumps({"success": False, "error": "Occupation allready exits"})

        register_occupation(occupation_name)
        return  json.dumps({"success": True})
    except UserNotFound:
        return json.dumps({"success": False, "error": "/add/occupation"})


@app.route('/get/occupation/<occupation_id>/patients', methods=['GET'])
def get_occupation_patients(occupation_id):
    try:
        occupation_obj = get_occupation(occupation_id)
        if not occupation_obj:
            return json.dumps({"success": False, "error": "Occupation does not exits"})
        patients = get_users_list_from_ids(occupation_obj.patients)
        return  json.dumps({"success": True, "Patients": patients})
    except UserNotFound:
        return json.dumps({"success": False, "error": "/add/occupation"})


@app.route('/get/occupation/<occupation_id>/therapist', methods=['GET'])
def get_occupation_therapists(occupation_id):
    try:
        occupation_obj = get_occupation(occupation_id)
        if not occupation_obj:
            return json.dumps({"success": False, "error": "Occupation does not exits"})
        therapists = get_users_list_from_ids(occupation_obj.therapists)
        return  json.dumps({"success": True, "Therapists": therapists})
    except UserNotFound:
        return json.dumps({"success": False, "error": "/add/occupation"})



if __name__ == "__main__":
    app.run(debug=True)

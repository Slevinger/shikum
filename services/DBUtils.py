import bson

from errors.base import UserNotFound
from models.users import User

users_obj = {}
therapists_obj = {}
patients_obj = {}


def get_user(user_id):
    id_obj = bson.ObjectId(user_id)
    obj = None
    if user_id in users_obj.keys():
        obj = users_obj[id]
    else:
        obj = User.objects(id=id_obj).first()
        users_obj[id] = obj
    if obj:
        if obj.role == "Therapist":
            add_therapist(obj)
        else:
            add_patient(obj)
        return obj
    raise UserNotFound


def add_therapist(user_obj):
    if str(user_obj.id) in therapists_obj.keys():
       pass
    else:
        therapists_obj[str(user_obj.id)] = user_obj


def add_patient(user_obj):
    if str(user_obj.id) in patients_obj.keys():
       pass
    else:
        patients_obj[str(user_obj.id)] = user_obj
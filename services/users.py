import random
import string

import bson

from errors.base import UserNotFound, FailedUpdatingUser, OccupationNotFound
from models.users import User, Occupation, UnavailabilitySlot


def register_occupation(name):
    occupation = Occupation(occupation_name=name)
    return occupation.save()


def get_occupation_by_name(occupation_name):
    occupation_obj = Occupation.objects(occupation_name=occupation_name).first()
    if occupation_obj:
        return occupation_obj
    pass


def get_occupation(occupation_id):
    id_obj = bson.ObjectId(occupation_id)
    occupation_obj = Occupation.objects(id=id_obj).first()
    if occupation_obj:
        return occupation_obj
    raise OccupationNotFound


def add_patient_to_occupation(occupation_obj,patient_obj):
    valid = True
    patient_id = str(patient_obj.id)
    for patient in occupation_obj.patients:
        if patient.id == patient_id:
            valid = False
    id_obj = bson.ObjectId(occupation_obj.id)

    if valid:
        Occupation.objects(id=id_obj).update_one(push__patients=patient_id)
        return True
    return False


def add_therapist_to_occupation(occupation_obj, therapist_obj):
    valid = True
    therapist_id = str(therapist_obj.id)
    for therapist in occupation_obj.therapists:
        if therapist.id == therapist_id:
            valid = False
    id_obj = bson.ObjectId(occupation_obj.id)
    if valid:
        Occupation.objects(id=id_obj).update_one(push__therapists=therapist_id)
        return True
    return False


def validate_user_login(username, password):
    user = User.objects(username=username).first()
    if not user:
        raise UserNotFound
    if user.password == password:
        return user
    return False


def update_users_token(user_obj):
    hexdigits = string.hexdigits.lower()
    token = ''.join(random.choice(hexdigits) for _ in range(40))
    user_obj.token = token
    try:
        user_obj.save()
    except:
        raise FailedUpdatingUser
    return token


def register_user(username, password, role):
    user = User(username=username, password=password, role=role)
    return user.save()


def get_users_list_from_ids(list_of_ids):
    string_list = [str(elem) for elem in list_of_ids]
    users = User.objects.filter(id__in=string_list)
    return users._result_cache


def generate_restriction(user_obj, start_time, end_time, reason):
    slot = UnavailabilitySlot(start_time=start_time, end_time=end_time, reason=reason)
    valid = True
    for schedules_slot in user_obj.unavailability:
        if schedules_slot.overlap(slot):
            valid = False

    if valid:
        User.objects(id=user_obj.id).update_one(push__unavailability=slot)
        return True

    return False

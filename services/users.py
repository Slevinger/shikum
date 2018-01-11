import random
import string

import bson

from errors.base import UserNotFound, FailedUpdatingUser, OccupationNotFound
from models.users import Occupation, TimeSlot, Therapist


def register_occupation(name):
    occupation_obj = Occupation(name=name)
    return occupation_obj.save()


def get_occupation_by_name(occupation_name):
    occupation_obj = Occupation.objects(name=occupation_name).first()
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


def validate_user_login(cls, username, password):
    user = cls.objects(username=username).first()
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


def register_user(cls, username, password, occupation):
    if occupation:
        return cls(username=username, password=password, occupation=occupation).save()
    return cls(username=username, password=password).save()


def generate_restriction(user_obj, start_time, end_time, description):
    slot = TimeSlot(start_time=start_time, end_time=end_time, description=description, available=False)
    for unavailability in user_obj.unavailability:
        if unavailability.overlap(slot):
            unavailability.start_time = min([unavailability.start_time, slot.start_time])
            unavailability.end_time = max([unavailability.end_time, slot.end_time])
            unavailability.description = "{}, {}".format(unavailability.description, slot.description)
            return unavailability.save()

    user_obj.__class__.objects(id=user_obj.id).update_one(push__unavailability=slot)
    return True


def get_therapists_by_occupation(occupation_id):
    id_obj = bson.ObjectId(occupation_id)
    occupation = Occupation.objects.get(id=id_obj)
    therapists = Therapist.objects(occupation=occupation)
    return therapists
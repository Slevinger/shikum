
from mongoengine import *
import datetime


class ShikumBaseDocument(Document):
    created_at = DateTimeField(required=True, default=lambda: datetime.datetime.utcnow())
    updated_at = DateTimeField(required=True, default=lambda: datetime.datetime.utcnow())

    meta = {
        'abstract': True,
        'auto_create_index': False,
        'indexes': ['created_at']
    }


class Slot(ShikumBaseDocument):
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    description = StringField()
    available = BooleanField()

    def overlap(self, slot):
        if self.start_time <= slot.start_time <= self.end_time or self.start_time <= slot.end_time <= self.end_time:
            return True
        return False

    meta = {
        'abstract': True
    }


class TimeSlot(Slot):
    therapist = StringField(max_length=200)
    patients = ListField(StringField(max_length=200))

    meta = {
        'collection': 'time_slots'
    }


class Occupation(ShikumBaseDocument):
    name = StringField(max_length=200, required=True, unique=True)

    meta = {
        'collection': 'occupations'
    }


class User(ShikumBaseDocument):
    username = StringField(max_length=200, required=True, unique=True)
    password = StringField(max_length=100, min_length=8, required=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    token = StringField()
    unavailability = ListField(TimeSlot)

    meta = {
        'abstract': True
    }


class Patient(User):
    therapists = ListField(StringField(max_length=200, required=False))
    occupiations = ListField(ReferenceField(Occupation, required=True))

    meta = {
        'collection': 'patients'
    }


class Therapist(User):
    patients = ListField(StringField(max_length=200, required=False))
    occupiation = ReferenceField(Occupation, required=True)
    meta = {
        'collection': 'therapists'
    }




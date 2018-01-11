from mongoengine import *
import datetime


class UnavailabilitySlot(EmbeddedDocument):
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    reason = StringField()

    def overlap(self, slot):
        if self.start_time <= slot.start_time <= self.end_time or self.start_time <= slot.end_time <= self.end_time:
            return True
        return False


class TimeSlot(Document):
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    therapist = StringField(max_length=200)
    patients = ListField(StringField(max_length=200))

    def overlap(self, slot):
        if self.start_time <= slot.start_time <= self.end_time or self.start_time <= slot.end_time <= self.end_time:
            return True
        return False


class User(Document):
    username = StringField(max_length=200, required=True, unique=True)
    password = StringField(max_length=100, min_length=8, required=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    token = StringField()
    unavailability = ListField(EmbeddedDocumentField(UnavailabilitySlot))
    role = StringField(required=True, choices=("Therapist", "Patient"))
    patients = ListField(StringField(max_length=200, required=False))
    therapists = ListField(StringField(max_length=200, required=False))
    meta = {
        'indexes': [{'fields': ['username'], 'unique': True}, 'created_at']
    }


class Occupation(Document):
    occupation_name = StringField(max_length=200, required=True, unique=True)
    patients = ListField(StringField(max_length=200, required=True, unique=True))
    therapists = ListField(StringField(max_length=200, required=True, unique=True))

import logging

from datetime import datetime

from mongoengine import connect, DynamicDocument
from mongoengine.fields import (StringField, EmailField, IntField, FloatField,
                                DateTimeField, ListField, ReferenceField)
import config

logger = logging.getLogger('users')

db = connect(config.DB.pop('name'), alias='default', connect=False, **config.DB)


class Guy(DynamicDocument):
    meta = {'collection': 'guys'}

    email = EmailField()
    balance = FloatField()
    claimed = DateTimeField()

    problems = IntField(default=0)

    def __repr__(self):
        return 'Guy({})'.format(str(self.to_json()))

#!/usr/bin/python3
""" database.py - get persistence for data
    v0.0.2 - 2021-10-21 - nelbren@nelbren.com"""
from pathlib import Path
from peewee import (
        SqliteDatabase,
        Model,
        CharField,
        IntegerField,
        FloatField
    )

HOME = str(Path.home())
BASE = HOME + '/.miner.db'
db = SqliteDatabase(BASE)

class BaseModel(Model):
    '''Database'''

    class Meta:
        '''Metadata'''
        # pylint: disable=too-few-public-methods
        database = db

class Unpaid(BaseModel):
    '''Unpaid table'''
    source = CharField(max_length=50)
    currency = CharField(max_length=3)
    work = IntegerField()
    step = IntegerField()
    timestamp = CharField(max_length=18)
    value = FloatField()
    usd = FloatField()
    pm_type = CharField(max_length=3)
    pm_max = FloatField()
    pm = FloatField()

    class Meta:
        '''Metadata'''
        # pylint: disable=too-few-public-methods
        db_table = 'unpaid'
        indexes = (
                      (('source', 'currency', 'work', 'step', 'timestamp'), True),
                      (('source', 'currency', 'work', 'step'), True)
                  )

    def __str__(self):
        # pylint: disable=no-member
        return f'{self.id} : {self.source} {self.currency} {self.work} {self.step}'

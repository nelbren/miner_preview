#!/usr/bin/python3
""" database.py - get persistence for data
    v0.0.3 - 2021-10-24 - nelbren@nelbren.com"""
from pathlib import Path
from peewee import (
        SqliteDatabase,
        Model,
        CharField,
        IntegerField,
        FloatField
    )

HOME = str(Path.home())
BASE = HOME + '/.miner_preview.db'
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
        return (
                   f'{self.id} : SRC: {self.source} CUR: {self.currency} '
                   f'WKR: {self.work} STP: {self.step} '
                   f'VAL: {self.value} USD: {self.usd}'
               )

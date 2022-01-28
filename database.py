#!/usr/bin/python3
""" database.py - get persistence for data
    v0.0.4 - 2022-01-27 - nelbren@nelbren.com"""
import os
from pathlib import Path
from peewee import SqliteDatabase, Model, CharField, IntegerField, FloatField

HOME = str(Path.home())
PWD = os.path.dirname(os.path.realpath(__file__))
PWD_DIR = os.path.basename(PWD)
BASE = f"{HOME}/.{PWD_DIR}.db"
db = SqliteDatabase(BASE)


class BaseModel(Model):
    """Database"""

    class Meta:
        """Metadata"""

        # pylint: disable=too-few-public-methods
        database = db


class Unpaid(BaseModel):
    """Unpaid table"""

    source = CharField(max_length=50)
    currency = CharField(max_length=3)
    work = IntegerField()
    step = IntegerField()
    timestamp = CharField(max_length=18)
    value = FloatField()
    usd = FloatField()

    class Meta:
        """Metadata"""

        # pylint: disable=too-few-public-methods
        db_table = "unpaid"
        indexes = (
            (("source", "currency", "work", "step", "timestamp"), True),
            (("source", "currency", "work", "step"), True),
        )

    def __str__(self):
        # pylint: disable=no-member
        return (
            f"{self.id} : SRC: {self.source} CUR: {self.currency} "
            f"WKR: {self.work} STP: {self.step} "
            f"VAL: {self.value} USD: {self.usd}"
        )

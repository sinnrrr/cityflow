from peewee import *

db = SqliteDatabase('tournament.db')


class BaseModel(Model):
    class Meta:
        database = db


class Road(BaseModel):
    class Meta:
        table_name = 'roads'

    x1 = IntegerField()
    y1 = IntegerField()
    x2 = IntegerField()
    y2 = IntegerField()
    lanes = IntegerField(default=2)
    covering = IntegerField(default=0)
    parallel = ForeignKeyField('self', null=True, default=None)
    following = ForeignKeyField('self', null=True, default=None)

    @classmethod
    def seed(cls):
        dictionary = [
            {'x1': 0, 'y1': 0, 'x2': 300, 'y2': 300},
            {'x1': 300, 'y1': 300, 'x2': 600, 'y2': 600},
            {'x1': 600, 'y1': 0, 'x2': 300, 'y2': 300},
            {'x1': 300, 'y1': 300, 'x2': 0, 'y2': 600},
        ]

        with db.atomic():
            for data in dictionary:
                Road.get_or_create(**data)

            print("roads seeded")


db.connect()
db.create_tables([Road])

Road.seed()

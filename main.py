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
    lanes = IntegerField(default=1)
    covering = IntegerField(default=0)
    parallel = ForeignKeyField('self', null=True, default=None)

    @classmethod
    def seed(cls):
        dictionary = [
            {'x1': 0, 'y1': 0, 'x2': 70, 'y2': 65},
            {'x1': 70, 'y1': 65, 'x2': 0, 'y2': 0},
            {'x1': 0, 'y1': 0, 'x2': 40, 'y2': 100},
            {'x1': 40, 'y1': 100, 'x2': 0, 'y2': 100},
            {'x1': 300, 'y1': 300, 'x2': 600, 'y2': 600},
            {'x1': 600, 'y1': 0, 'x2': 300, 'y2': 300},
            {'x1': 300, 'y1': 300, 'x2': 0, 'y2': 600},
        ]

        with db.atomic():
            for data in dictionary:
                Road.get_or_create(**data)

            print("roads seeded")

    @classmethod
    def point(cls, road_id, dot_x, dot_y):
        oldroad = Road.get_by_id(road_id)
        oldroad.delete_instance()

        dictionary = [
            {'x1': oldroad.x1, 'y1': oldroad.y1, 'x2': dot_x, 'y2': dot_y},
            {'x1': dot_x, 'y1': dot_y, 'x2': oldroad.x2, 'y2': oldroad.y2},
        ]

        Road.insert_many(dictionary).execute()
        print("road created")

    @classmethod
    def new(cls, x1, y1, x2, y2, lanes=None, covering=None, has_parallel=False):
        if has_parallel:
            dictionary = [
                {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'lanes': lanes, 'covering': covering},
                {'x1': x2, 'y1': y2, 'x2': x1, 'y2': y1, 'lanes': lanes, 'covering': covering},
            ]

            Road.insert_many(dictionary).execute()
        else:
            Road.create(x1=x1, y1=y1, x2=x2, y2=y2, lanes=lanes, covering=covering)


db.connect()
db.create_tables([Road])

Road.seed()

from peewee import *
import os

dbname = 'tournament.db'
db = SqliteDatabase(dbname)


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
    level = IntegerField(default=0)
    lanes = IntegerField(default=1)
    covering = IntegerField(default=0)
    parallel = ForeignKeyField('self', null=True, default=None)

    # for first launch
    @classmethod
    def seed(cls):
        dictionary = [
            {"x1": 0, "y1": 0, "x2": 300, "y2": 0, "covering": 2},
            {"x1": 300, "y1": 0, "x2": 300, "y2": 300, "covering": 4},
            {"x1": 300, "y1": 300, "x2": 0, "y2": 300, "covering": 3},
            {"x1": 0, "y1": 300, "x2": 0, "y2": 0, "covering": 0},
            {"x1": 0, "y1": 0, "x2": 300, "y2": 300, "covering": 2},
            {"x1": 300, "y1": 300, "x2": 0, "y2": 0, "covering": 2}
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
    def new(cls, *dictionary):
        if len(dictionary) > 1:
            for road in dictionary:
                if road.has_parallel:
                    parallel_road = {'x1': x2, 'y1':  y2, 'x2': x1, 'y2': y1}
                    dictionary.append(parallel_road)

            Road.insert_many(dictionary).execute()
        else:
            Road.create(dictionary)


os.remove(dbname)


db.connect()
db.create_tables([Road])

Road.seed()

# roads = Road.select()
# for road in roads:
#     print(road.x1)
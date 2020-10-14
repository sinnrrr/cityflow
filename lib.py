from peewee import *
import os

db = SqliteDatabase(None)

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

    red = IntegerField(default=30)
    green = IntegerField(default=30)
    tick = IntegerField(default=0)

    level = IntegerField(default=0)
    lanes = IntegerField(default=1)
    covering = IntegerField(default=0)
    parallel = ForeignKeyField('self', null=True, default=None)

    @classmethod
    def seed(cls):
        dictionary = [
            {"x1": 0, "y1": 0, "x2": 200, "y2": 0, "covering": 0, "red": 90, "green": 30},
            {"x1": 0, "y1": 50, "x2": 0, "y2": 0, "covering": 0, "red": 90, "green": 30},
            {"x1": 200, "y1": 0, "x2": 200, "y2": 50, "covering": 0}
        ]

        with db.atomic():
            for data in dictionary:
                Road.get_or_create(**data)

            print("roads seeded")

    @classmethod
    def load(cls, dc):
        with db.atomic():
            for data in dc:
                Road.get_or_create(**data)

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

def saveFile(name, level, rtype):
    if os.path.isfile(name):
        os.remove(name)
    db.init(name)
    db.connect()
    db.create_tables([Road])
    data = []
    count = 0
    for t in level:
        data.append({"x1": t[0], "y1": t[1], "x2": t[2], "y2": t[3], "covering": rtype[count]})
        count += 1
    Road.load(data)
    db.close()

def loadFile(name):
    db.init(name)
    db.connect()
    db.create_tables([Road])
    data = Road.select()
    db.close()
    return list(data)

if __name__ == "__main__":
    if os.path.isfile("tour.db"):
        os.remove("tour.db")
    db.init("tour.db")
    db.connect()
    db.create_tables([Road])
    Road.seed()
    db.close()
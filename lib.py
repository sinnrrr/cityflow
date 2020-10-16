from peewee import *
import os

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class Road(BaseModel):
    class Meta:
        table_name = "roads"

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

    spawn = BooleanField(default=True)
    #parallel = ForeignKeyField("self", null=True, default=None) # ?

    @classmethod
    def seed(cls):
        dictionary = [
            {"x1": 20, "y1": 20, "x2": 100, "y2": 100, "covering": 1},
            {"x1": 100, "y1": 100, "x2": 100, "y2": 20, "covering": 2},
            {"x1": 100, "y1": 20, "x2": 20, "y2": 100, "covering": 3, "lanes": 2},
            {"x1": 20, "y1": 100, "x2": 20, "y2": 20, "covering": 4},
            {"x1": 100, "y1": 100, "x2": 20, "y2": 100, "covering": 5, "lanes": 4},
            {"x1": 20, "y1": 20, "x2": -100, "y2": -100, "lanes": 4, "spawn": False},
            {"x1": -100, "y1": -100, "x2": 20, "y2": 20, "lanes": 4, "spawn": False}
        ]

        with db.atomic():
            for data in dictionary:
                Road.get_or_create(**data)

    @classmethod
    def load(cls, dc):
        with db.atomic():
            for data in dc:
                Road.get_or_create(**data)

    @classmethod
    def point(cls, road_id, dot_x, dot_y): # ?
        oldroad = Road.get_by_id(road_id)
        oldroad.delete_instance()

        dictionary = [
            {"x1": oldroad.x1, "y1": oldroad.y1, "x2": dot_x, "y2": dot_y},
            {"x1": dot_x, "y1": dot_y, "x2": oldroad.x2, "y2": oldroad.y2},
        ]

        Road.insert_many(dictionary).execute()

    @classmethod
    def new(cls, *dictionary): # ?
        if len(dictionary) > 1:
            for road in dictionary:
                if road.has_parallel:
                    parallel_road = {"x1": x2, "y1":  y2, "x2": x1, "y2": y1}
                    dictionary.append(parallel_road)

            Road.insert_many(dictionary).execute()
        else:
            Road.create(dictionary)

class Trigger(BaseModel):
    class Meta:
        table_name = "triggers"

    name = TextField()
    ints = TextField()

    @classmethod
    def seed(self):
        with db.atomic():
            Trigger.get_or_create(name="TEST", ints="lock 0")

    @classmethod
    def load(self, texts):
        for data in texts:
            Trigger.insert_many(data).execute()

def saveFile(name, level, rtype, lights, ints):
    if os.path.isfile(name):
        os.remove(name)
    db.init(name)
    db.connect()
    db.create_tables([Road, Trigger])
    data = []
    count = 0
    for t in level:
        data.append({"x1": t[0], "y1": t[1], "x2": t[2], "y2": t[3], "covering": rtype[count]})
        count += 1
    Trigger.load(ints)
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
    db.create_tables([Road, Trigger])
    Road.seed()
    Trigger.seed()
    db.close()
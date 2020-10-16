from peewee import *
from settings import *
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

    level = IntegerField(default=0)
    lanes = IntegerField(default=1)
    covering = IntegerField(default=0)

    tick = IntegerField(default=0)
    red_time = IntegerField(default=30)
    green_time = IntegerField(default=30)

    spawn_ability = BooleanField(default=True)

    @classmethod
    def seed(cls):  # seeds roads to database
        dictionary = [
            {"x1": 20, "y1": 20, "x2": 100, "y2": 100, "covering": 1},
            {"x1": 100, "y1": 100, "x2": 100, "y2": 20, "covering": 2},
            {"x1": 100, "y1": 20, "x2": 20, "y2": 100, "covering": 3, "lanes": 2},
            {"x1": 20, "y1": 100, "x2": 20, "y2": 20, "covering": 4},
            {"x1": 100, "y1": 100, "x2": 20, "y2": 100, "covering": 5, "lanes": 4},
            {"x1": 20, "y1": 20, "x2": -100, "y2": -100, "lanes": 4, "spawn_ability": False},
            {"x1": -100, "y1": -100, "x2": 20, "y2": 20, "lanes": 4, "spawn_ability": False}
        ]

        with db.atomic():
            for data in dictionary:
                Road.get_or_create(**data)

    @classmethod
    def point(cls, road_id, dot_x, dot_y):  # method to divide roads in two parts, when creating
        oldroad = Road.get_by_id(road_id)
        oldroad.delete_instance()

        dictionary = [
            {"x1": oldroad.x1, "y1": oldroad.y1, "x2": dot_x, "y2": dot_y},
            {"x1": dot_x, "y1": dot_y, "x2": oldroad.x2, "y2": oldroad.y2},
        ]

        Road.insert_many(dictionary).execute()

    @classmethod
    def new(cls, dictionary):  # method to connect two dots into one road and insert to database
        if len(dictionary) > 1:
            Road.insert_many(dictionary).execute()
        else:
            Road.create(dictionary)


class Trigger(BaseModel):
    class Meta:
        table_name = "triggers"

    name = TextField()
    instructions = TextField()

    @classmethod
    def seed(cls):
        with db.atomic():
            Trigger.get_or_create(name="TEST", instructions="lock 0")


def loadFile(name):
    initDB(name)
    data = Road.select()

    db.close()

    return list(data)


def initDB(name):
    db.init(name)
    db.connect()

    db.create_tables([Road, Trigger])


if __name__ == "__main__":
    default_db_name = os.getenv("DEFAULT_DB_FILE_NAME")

    if os.path.isfile(default_db_name):
        os.remove(default_db_name)

    initDB(default_db_name)

    Road.seed()
    Trigger.seed()

    db.close()

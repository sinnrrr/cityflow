from tkinter import filedialog, messagebox
from tkinter import *

from settings import *
from pygame.time import Clock

import random
import time
import lib
import os
import threading


# for Windows only
def drag_and_attribute():
    if len(sys.argv) > 1:
        from os.path import isfile

        if not isfile(sys.argv[1]):
            sys.exit(1)


# init root tkinter configuration
def init():
    global root, canvas, clock, menu, trigger_menu
    drag_and_attribute()

    root = Tk()
    clock = Clock()
    canvas = Canvas(
        root,
        width=int(os.getenv("TK_WIDTH")),
        height=int(os.getenv("TK_HEIGHT")),
    )

    menu = Menu(root)
    trigger_menu = Menu(menu, tearoff=0)

    root.title(os.getenv("TK_TITLE"))
    root.geometry(os.getenv("TK_WIDTH") + "x" + os.getenv("TK_HEIGHT"))
    root.resizable(int(os.getenv("TK_RESIZABLE_X")), int(os.getenv("TK_RESIZABLE_Y")))


# init root variables
init()


# highlight cover color
def highlight_color(color):
    dictionary = Settings.covers.values()

    for value in dictionary:
        if value[1] == color:
            return value[2]


# system object
class System:
    cars = []
    lanes = []
    lines = []
    lights = []
    triggers = []

    level = []
    scale = 1.0
    road_types = []
    position = [0, 0]

    locked_roads = []
    spawn_positions = []

    @classmethod
    def load_db_file(cls, db):
        roads = lib.loadFile(db)
        cls.reset_map()

        roads_width = {}
        counter = 0

        cls.min_x, cls.min_y, cls.max_x, cls.max_y = 2147483647, 2147483647, 0, 0

        for road in roads:
            if road.covering in Settings.covers:
                cls.road_types.append(road.covering)
            else:
                cls.road_types.append(0)
            try:
                roads_width[
                    tuple({
                        (road.x1, road.y1),
                        (road.x2, road.y2),
                    })
                ] += road.lanes
            except:
                roads_width[
                    tuple({
                        (road.x1, road.y1),
                        (road.x2, road.y2),
                    })
                ] = road.lanes

            cls.level.append([road.x1, road.y1, road.x2, road.y2])
            cls.lanes.append(road.lanes)
            cls.spawn_positions.append(road.spawn_ability)
            cls.lights.append(Light(counter, road.red_time, road.green_time, road.tick))

            if road.x1 < cls.min_x:
                cls.min_x = road.x1
            elif road.x2 < cls.min_x:
                cls.min_x = road.x2
            if road.y1 < cls.min_y:
                cls.min_y = road.y1
            elif road.y2 < cls.min_y:
                cls.min_y = road.y2

            if road.x1 > cls.max_x:
                cls.max_x = road.x1
            elif road.x2 > cls.max_x:
                cls.max_x = road.x2
            if road.y1 > cls.max_y:
                cls.max_y = road.y1
            elif road.y2 > cls.max_y:
                cls.max_y = road.y2

            counter += 1

        counter = 0

        cls.locked_roads.clear()
        for road in cls.level:
            road_width = roads_width[
                tuple({
                    (road[0], road[1]),
                    (road[2], road[3]),
                })
            ]
            line_id = canvas.create_line(
                *road,
                fill=Settings.covers[cls.road_types[counter]][2],
                width=road_width,
                activefill=highlight_color(Settings.covers[cls.road_types[counter]][2]),
            )

            exec(
                "c.tag_bind(o, \"<Button-1>\", lambda e: lock(%s, %s))"
                % (counter, line_id),
                {"c": canvas, "o": line_id, "lock": lock_road}
            )

            cls.lines.append(line_id)
            cls.locked_roads.append(0)
            counter += 1

        for trigger in lib.Trigger.select():
            cls.triggers.append(ExecutableCommand(trigger.name, trigger.instructions))

        for light in cls.lights:
            light.init()

        cls.goto_home(None)

    @classmethod
    def update_lines(cls):
        for i in range(len(cls.lines)):
            canvas.coords(cls.lines[i], *cls.road_coordinates(i))

        cls.move_lines(*cls.position)

    @classmethod
    def goto_home(cls, event):
        for i in range(len(cls.lines)):
            canvas.coords(cls.lines[i], *cls.road_coordinates(i))

        cls.position = [0, 0]
        cls.update_lines()

    @classmethod
    def mouse_press(cls, event):
        cls.start = event.x, event.y

    @classmethod
    def hold_motion(cls, event):
        cls.move_lines(event.x - cls.start[0], event.y - cls.start[1])
        cls.position[0] += event.x - cls.start[0]
        cls.position[1] += event.y - cls.start[1]
        cls.start = event.x, event.y

    @classmethod
    def move_lines(cls, dx, dy):
        for i in range(len(cls.lines)):
            canvas.move(cls.lines[i], dx, dy)
        for car in cls.cars:
            car.update()

    @classmethod
    def scale_down(cls, event):
        cls.scale /= 1.2
        cls.update_lines()

    @classmethod
    def scale_up(cls, event):
        cls.scale *= 1.2
        cls.update_lines()

    @classmethod
    def scale_reset(cls, event):
        cls.scale = 1
        cls.update_lines()

    @classmethod
    def road_coordinates(cls, road_id):
        return (cls.level[road_id][0] * cls.scale,
                cls.level[road_id][1] * cls.scale,
                cls.level[road_id][2] * cls.scale,
                cls.level[road_id][3] * cls.scale)

    @classmethod
    def get_scaled_position(cls, x, y):
        return cls.position[0] + x * cls.scale, cls.position[1] + y * cls.scale

    @classmethod
    def mouse_wheel(cls, event):
        val = abs(event.delta // 120)
        if event.delta > 0:
            for t in range(val):
                cls.scale_up(event)
        else:
            for t in range(val):
                cls.scale_down(event)

    @classmethod
    def reset_map(cls):
        cls.remove_cars()

        for road in cls.lines:
            canvas.delete(road)

        for light in cls.lights:
            canvas.delete(light.id)

        for trigger in cls.triggers:
            trigger_menu.delete(0)

        cls.lines, cls.level, cls.triggers, cls.rtype, cls.lights, cls.lanes, cls.spawn = [], [], [], [], [], [], []

    @classmethod
    def open_db_file(cls):

        path = filedialog.askopenfilename(
            initialdir="/",
            title="Select file",
            filetypes=(
                ("Data Bases", "*.db"),
            )
        )
        if path:
            try:
                cls.load_db_file(path)
                cls.currentFile = path
            except:
                messagebox.showerror(title="Oops!", message="File %s does not exist" % path)

    @classmethod
    def move_entities(cls):
        for light in cls.lights:
            light.update()

        for car in cls.cars:
            car.move()

        root.update()

    @classmethod
    def spawn_random_place_car(cls):
        previous_scale = System.scale
        System.scale = 1

        sequence = []
        for road in range(len(cls.level)):
            if cls.spawn_positions[road]:
                sequence.append(road)

        if sequence:
            road = random.choice(sequence)
            speed = random.randint(6, 20)

            cls.cars.append(
                Car(
                    road,
                    speed,
                    color_convert[
                        selected_color.get()
                    ],
                )
            )

        System.scale = previous_scale

    @classmethod
    def spawn_concrete_place_car(cls):
        previous_scale = System.scale
        System.scale = 1

        sequence = []
        for road in range(len(cls.level)):
            if cls.spawn_positions[road]:
                sequence.append(road)

        if sequence:
            road = random.choice(sequence)
            speed = random.randint(6, 21)

            cls.cars.append(
                Car(
                    road,
                    speed,
                    color_convert[
                        random.randrange(16)
                    ]
                )
            )

        System.scale = previous_scale

    @classmethod
    def remove_cars(cls):
        for car in cls.cars:
            car.destruct()

        cls.cars.clear()


# angle calculation functions
def head_x(x, y, dx, dy, qy):
    if y == dy:
        return y

    return round((qy - y) * (dx - x) / (dy - y) + x)


def head_y(x, y, dx, dy, qx):
    if x == dx:
        return x

    return round((qx - x) * (dy - y) / (dx - x) + y)


# get number's number_sign
def number_sign(n):
    if n > 0:
        return 1
    elif n < 0:
        return -1
    return 0


# set lock to road
def lock_road(road_id, line_id=None):
    System.locked_roads[road_id] = not System.locked_roads[road_id]

    if not line_id:
        line_id = System.lines[road_id]

    if System.locked_roads[road_id]:
        canvas.itemconfig(line_id, dash=[8, 8])
    else:
        canvas.itemconfig(line_id, dash=[])


# target list
target1 = [0, 0]
target2 = [0, 0]
target3 = [0, 0]
target4 = [0, 0]
target5 = [0, 0]
target6 = [0, 0]
target7 = [0, 0]
target8 = [0, 0]
target9 = [0, 0]
target10 = [0, 0]


# car class
class Car:
    def __init__(self, road_id, max_velocity, color):
        self.max_velocity = max_velocity  # to load
        self.lane = 0
        self.velocity = 0

        self.position = list(System.road_coordinates(road_id)[0:2])  # to load

        self.id = canvas.create_oval(
            int(self.position[0]) + System.position[0] - System.scale * 3,
            int(self.position[1]) + System.position[1] - System.scale * 3,
            int(self.position[0]) + System.position[0] + System.scale * 3,
            int(self.position[1]) + System.position[1] + System.scale * 3, fill="#%06x" % color)

        self.queue = road_id  # to load
        self.current_max_velocity = Settings.covers[System.road_types[road_id]]

    def update_position(self):
        canvas.coords(
            self.id,
            int(self.position[0]) * System.scale + System.position[0] - System.scale * 3,
            int(self.position[1]) * System.scale + System.position[1] - System.scale * 3,
            int(self.position[0]) * System.scale + System.position[0] + System.scale * 3,
            int(self.position[1]) * System.scale + System.position[1] + System.scale * 3,
        )

    def move_position(self):
        if self.current_max_velocity > self.max_velocity:
            bigger_velocity = self.current_max_velocity
        else:
            bigger_velocity = self.max_velocity
        if self.velocity >= bigger_velocity:
            coordinates = System.level[self.queue]

            if coordinates[2:4] != self.position:
                difference = coordinates[0] - coordinates[2], coordinates[1] - coordinates[3]

                if abs(difference[0]) >= abs(difference[1]):
                    target1[0] = self.position[0] - number_sign(difference[0])
                    target1[1] = head_y(*coordinates, target1[0])

                    target2[0] = self.position[0] - number_sign(difference[0]) * 2
                    target2[1] = head_y(*coordinates, target2[0])

                    target3[0] = self.position[0] - number_sign(difference[0]) * 3
                    target3[1] = head_y(*coordinates, target3[0])

                    target4[0] = self.position[0] - number_sign(difference[0]) * 4
                    target4[1] = head_y(*coordinates, target4[0])

                    target5[0] = self.position[0] - number_sign(difference[0]) * 5
                    target5[1] = head_y(*coordinates, target5[0])

                    target6[0] = self.position[0] - number_sign(difference[0]) * 6
                    target6[1] = head_y(*coordinates, target6[0])

                    target7[0] = self.position[0] - number_sign(difference[0]) * 7
                    target7[1] = head_y(*coordinates, target7[0])

                    target8[0] = self.position[0] - number_sign(difference[0]) * 8
                    target8[1] = head_y(*coordinates, target8[0])

                    target9[0] = self.position[0] - number_sign(difference[0]) * 9
                    target9[1] = head_y(*coordinates, target9[0])

                    target10[0] = self.position[0] - number_sign(difference[0]) * 10
                    target10[1] = head_y(*coordinates, target10[0])

                    wheel_move = 1

                    for car in System.cars:
                        if car == self:
                            continue
                        if car.queue == self.queue and car.lane == self.lane:
                            if car.position == target1:
                                m = 0
                                break
                            elif car.position == target2:
                                m = 0
                                break
                            elif car.position == target3:
                                m = 0
                                break
                            elif car.position == target4:
                                m = 0
                                break
                            elif car.position == target5:
                                m = 0
                                break
                            elif car.position == target6:
                                m = 0
                                break
                            elif car.position == target7:
                                m = 0
                                break
                            elif car.position == target8:
                                m = 0
                                break
                            elif car.position == target9:
                                m = 0
                                break
                            elif car.position == target10:
                                m = 0
                                break

                    if wheel_move:
                        self.position[0] = target1[0]
                        self.position[1] = target1[1]
                    else:
                        self.lane = (self.lane + 1) % System.lanes[self.queue]

                else:
                    target1[1] = self.position[1] - number_sign(difference[1])
                    target1[0] = head_x(*coordinates, target1[1])

                    target2[1] = self.position[1] - number_sign(difference[1]) * 2
                    target2[0] = head_x(*coordinates, target2[1])

                    target3[1] = self.position[1] - number_sign(difference[1]) * 3
                    target3[0] = head_x(*coordinates, target3[1])

                    target4[1] = self.position[1] - number_sign(difference[1]) * 4
                    target4[0] = head_x(*coordinates, target4[1])

                    target5[1] = self.position[1] - number_sign(difference[1]) * 5
                    target5[0] = head_x(*coordinates, target5[1])

                    target6[1] = self.position[1] - number_sign(difference[1]) * 6
                    target6[0] = head_x(*coordinates, target6[1])

                    target7[1] = self.position[1] - number_sign(difference[1]) * 7
                    target7[0] = head_x(*coordinates, target7[1])

                    target8[1] = self.position[1] - number_sign(difference[1]) * 8
                    target8[0] = head_x(*coordinates, target8[1])

                    target9[1] = self.position[1] - number_sign(difference[1]) * 9
                    target9[0] = head_x(*coordinates, target9[1])

                    target10[1] = self.position[1] - number_sign(difference[1]) * 10
                    target10[0] = head_x(*coordinates, target10[1])

                    wheel_move = 1

                    for car in System.cars:
                        if car == self:
                            continue
                        if car.queue == self.queue and car.l == self.l:
                            if car.position == target1:
                                m = 0
                                break
                            elif car.position == target2:
                                m = 0
                                break
                            elif car.position == target3:
                                m = 0
                                break
                            elif car.position == target4:
                                m = 0
                                break
                            elif car.position == target5:
                                m = 0
                                break
                            elif car.position == target6:
                                m = 0
                                break
                            elif car.position == target7:
                                m = 0
                                break
                            elif car.position == target8:
                                m = 0
                                break
                            elif car.position == target9:
                                m = 0
                                break
                            elif car.position == target10:
                                m = 0
                                break

                    if wheel_move:
                        self.position[0] = target1[0]
                        self.position[1] = target1[1]
                    else:
                        self.lane = (self.lane + 1) % System.lanes[self.queue]

            elif System.lights[self.queue].state:
                sequence = []

                for i in range(len(System.level)):
                    if System.level[i][0:2] == coordinates[2:4] and System.locked_roads[i] == 0:
                        sequence.append(i)

                if sequence:
                    rand = random.choice(sequence)

                    self.queue = rand
                    self.lane = 0
                    self.current_max_velocity = Settings.covers[System.road_types[rand]][0]
                    self.velocity = 0

            if self.velocity > 0:
                self.velocity = 0

            self.update_position()
        else:
            self.velocity += 1

    def destruct(self):
        canvas.delete(self.id)


# light class
class Light:
    def __init__(self, road_id, red_time, green_time, tick):
        self.pause = red_time * 16, green_time * 16
        self.road_id = road_id
        self.state = 0
        self.tick = tick

    def init(self):
        if self.tick >= self.pause[1]:
            self.circle_id = canvas.create_oval(*self.location(), fill="#00FF00")
        else:
            self.circle_id = canvas.create_oval(*self.location(), fill="#FF0000")

    def update_state(self):
        if self.tick >= self.pause[0] + self.pause[1]:
            self.tick = 0
            self.state = 0

            canvas.itemconfig(self.circle_id, fill="#FF0000")
        else:
            self.tick += 1
            if self.tick == self.pause[1]:
                self.state = 1

                canvas.itemconfig(self.circle_id, fill="#00FF00")

        canvas.coords(self.circle_id, *self.location())

    def location(self):
        x = System.position[0] + System.level[self.road_id][2] * System.scale
        y = System.position[1] + System.level[self.road_id][3] * System.scale

        return x - System.scale * 5, y - System.scale * 5, x + System.scale * 5, y + System.scale * 5


class ExecutableCommand:
    def __init__(self, name, instructions):
        self.instructions = instructions.split(", ")

        trigger_menu.add_command(label=name, command=self.run)

    def run(self):
        for line in self.instructions:
            line = line.split()

            if line[0] == "clear":
                System.remove_cars()
            elif line[0] == "spawncars":
                for i in range(int(line[1])):
                    System.spawn_concrete_place_car()
            elif line[0] == "scale":
                System.scale = float(line[1])
                System.update_lines()
            elif line[0] == "delay":
                time.sleep(int(line[1]) / 1000)
            elif line[0] == "timestop":
                stop_time()
            elif line[0] == "continue":
                resume_time()
            elif line[0] == "speed":
                Settings.pause = int(line[1])
            elif line[0] == "lock":
                lock_road(int(line[1]))


# terminate function
def terminate():
    Settings.is_terminable = True
    exit()


# default speed function
def default_speed():
    Settings.pause = 240

    speed_menu.entryconfigure(0, label="Speed: %s Ticks" % Settings.pause)


# increase speed function
def increase_speed(boost=False):
    if boost:
        Settings.pause += 90
    Settings.pause += 30

    speed_menu.entryconfigure(0, label="Speed: %s Ticks" % Settings.pause)


# decrease speed function
def decrease_speed(boost=False):
    if boost:
        Settings.pause -= 90
    Settings.pause -= 30

    if Settings.pause < 10:
        Settings.pause = 10

    speed_menu.entryconfigure(0, label="Speed: %s Ticks" % Settings.pause)


# fullscreen function
def set_fullscreen():
    Settings.is_fullscreen = not Settings.is_fullscreen
    root.attributes("-fullscreen", Settings.is_fullscreen)

    canvas.config(width=root.winfo_width(), height=root.winfo_height())


# time functions
def stop_time():
    Settings.is_moving = False


# time functions
def resume_time():
    Settings.is_moving = True


speed_menu = Menu(menu, tearoff=0)
speed_menu.add_command(label="Speed: 240 Ticks")
speed_menu.add_command(label="Default Speed", command=default_speed)
speed_menu.add_separator()
speed_menu.add_command(label="Time Stop", command=stop_time)
speed_menu.add_command(label="Time Resume", command=resume_time)
speed_menu.add_separator()
speed_menu.add_command(label="Speed Up", command=increase_speed)
speed_menu.add_command(label="Slow Down", command=decrease_speed)
speed_menu.add_separator()
speed_menu.add_command(label="Super Speed Up", command=lambda: increase_speed(True))
speed_menu.add_command(label="Super Slow Down", command=lambda: decrease_speed(True))

car_menu = Menu(menu, tearoff=0)
car_submenu = Menu(car_menu, tearoff=0)

car_colors = [
    "Black", "Dark Gray", "Light Gray", "White",
    "Red", "Dark Red", "Green", "Dark Green",
    "Blue", "Dark Blue", "Yellow", "Orange",
    "Pink", "Purple", "Light Blue", "Mint"
]

color_convert = [
    0x000000, 0x505050, 0xA0A0A0, 0xFFFFFF,
    0xFF0000, 0xA00000, 0x00FF00, 0x00A000,
    0x0000FF, 0x0000A0, 0xFFFF00, 0xFF8000,
    0xFF40FF, 0xA000FF, 0x00FFFF, 0xC0FFEE
]

selected_color = IntVar()
count = 0

for color in car_colors:
    car_submenu.add_radiobutton(label=color, value=count, variable=selected_color)
    count += 1

car_menu.add_cascade(label="Car Color", menu=car_submenu)
car_menu.add_separator()
car_menu.add_command(label="Add Car", command=System.spawn_random_place_car)
car_menu.add_command(label="Remove All Cars", command=System.remove_cars)

menu.add_command(label="File", command=System.open_db_file)
menu.add_cascade(label="Speed", menu=speed_menu)
menu.add_cascade(label="Cars", menu=car_menu)
menu.add_cascade(label="Triggers", menu=trigger_menu)
menu.add_command(label="FullScreen", command=set_fullscreen)
menu.add_command(label="Exit", command=terminate)

root.bind_all("<Prior>", System.scale_up)
root.bind_all("<Next>", System.scale_down)
root.bind_all("<Home>", System.scale_reset)
root.bind_all("<End>", System.goto_home)

root.bind_all("<MouseWheel>", System.mouse_wheel)
root.bind_all("<Button-1>", System.mouse_press)
root.bind_all("<B1-Motion>", System.hold_motion)

canvas.pack()


# ============================
System.load_db_file(os.getenv("DEFAULT_DB_FILE_NAME"))
# System.cars.append(Car(0, 20, 0xffffff))
# System.cars.append(Car(1, 10, 0x000000))
# ============================

def loop():
    while not Settings.is_terminable:
        if Settings.is_moving:
            System.move_entities()
        clock.tick(Settings.pause)


thread = threading.Thread(target=loop)
thread.start()

root.config(menu=menu)
root.mainloop()

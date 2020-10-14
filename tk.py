# tk init
from egg import windll
from egg import sys
import egg

from tkinter import filedialog
from tkinter import *
import random, lib
import threading
from pygame.time import Clock

root = Tk()
root.title("App")

if len(sys.argv) > 1:
	from os.path import isfile

	if not isfile(sys.argv[1]):
		sys.exit(1)

	path = sys.argv[1]

root.geometry("1024x576")
root.resizable(0, 0)

c = Canvas(root, width=1024, height=576, highlightthickness=0)
clock = Clock()

pause = 240

TERMINATE = False
FULLSCREEN = 0
MOVE = 1

covers = {
	0: 0,
	1: 1,
	2: 3,
	3: 6,
	4: 10,
	5: 15
}
covcol = {
	0: "#000000",
	1: "#FF0000",
	2: "#FF8000",
	3: "#FFFF00",
	4: "#80FF20",
	5: "#00FF00"
}

# system object
class System:
	level = []
	rtype = []

	pos = [0, 0]

	scale = 1.0
	lines = []

	cars = []
	currentFile = None

	lights = []

	@classmethod
	def load(self, db):
		roads = lib.loadFile(db)
		self.new()

		count = 0
		for road in roads:
			if road.covering in covers:
				self.rtype.append(road.covering)
			else:
				self.rtype.append(0)
			self.level.append([road.x1, road.y1, road.x2, road.y2])
			self.lights.append(Light(count, road.lr, road.lg, road.lt, road.lv))
			count += 1

		count = 0
		for road in self.level:
			self.lines.append(c.create_line(*road, fill=covcol[self.rtype[count]]))
			count += 1

	@classmethod
	def loads(self, roads):
		self.new()

		for road in roads:
			if road.covering in covers:
				self.rtype.append(road.covering)
			else:
				self.rtype.append(0)
			self.level.append([road.x1, road.y1, road.x2, road.y2])

		count = 0
		for road in self.level:
			self.lines.append(c.create_line(*road, fill=covcol[self.rtype[count]]))
			count += 1

	@classmethod
	def update(self):
		for i in range(len(self.lines)):
			c.coords(self.lines[i], *self.road(i))
		self.place(*self.pos)

	@classmethod
	def home(self, evt):
		for i in range(len(self.lines)):
			c.coords(self.lines[i], *self.road(i))
		self.pos = [0, 0]

	@classmethod
	def press(self, evt):
		self.start = evt.x, evt.y

	@classmethod
	def bmotion(self, evt):
		self.place(evt.x - self.start[0], evt.y - self.start[1])
		self.pos[0] += evt.x - self.start[0]
		self.pos[1] += evt.y - self.start[1]
		self.start = evt.x, evt.y

	@classmethod
	def place(self, dx, dy):
		for i in range(len(self.lines)):
			c.move(self.lines[i], dx, dy)
		for car in self.cars:
			car.update()

	@classmethod
	def down(self, evt):
		self.scale /= 1.2
		self.mpos = evt.x - self.pos[0], evt.y - self.pos[1]
		self.update()

	@classmethod
	def up(self, evt):
		self.scale *= 1.2
		self.mpos = evt.x - self.pos[0], evt.y - self.pos[1]
		self.update()

	@classmethod
	def reset(self, evt):
		self.scale = 1
		self.mpos = evt.x - self.pos[0], evt.y - self.pos[1]
		self.update()

	@classmethod
	def road(self, index):
		return (self.level[index][0] * self.scale,
			self.level[index][1] * self.scale,
			self.level[index][2] * self.scale,
			self.level[index][3] * self.scale)

	@classmethod
	def get(self, x, y):
		return self.pos[0] + x * self.scale, self.pos[1] + y * self.scale

	@classmethod
	def mouse(self, evt):
		val = abs(evt.delta // 120)
		if evt.delta > 0:
			for t in range(val):
				self.up(evt)
		else:
			for t in range(val):
				self.down(evt)

	@classmethod
	def new(self):
		self.clearcar()
		for road in self.lines:
			c.delete(road)
		self.lines = []
		self.level = []
		self.rtype = []
		self.lights = []

	@classmethod
	def open(self):

		path = filedialog.askopenfilename(initialdir = "/", title = "Select file", filetypes = (("Data Bases", "*.db"),))
		if path:
			try:
				self.load(path)
				self.currentFile = path
			except:
				windll.user32.MessageBoxW(0, "File %s does not exist" % path, "Oops!", 0x10)

	@classmethod
	def save(self):
		if self.currentFile:
			try:
				lib.saveFile(self.currentFile, self.level, self.rtype)
			except:
				windll.user32.MessageBoxW(0, "Couldn't write to file %s" % self.currentFile, "Oops!", 0x10)

	@classmethod
	def saveas(self):
		path = filedialog.asksaveasfilename(initialdir = "/", title = "Select file", filetypes = (("Data Bases", "*.db"),))
		if path:
			try:
				lib.saveFile(path, self.level, self.rtype)
			except:
				windll.user32.MessageBoxW(0, "Couldn't write to file %s" % path, "Oops!", 0x10)

	@classmethod
	def move(self):
		for light in self.lights:
			light.update()
		for car in self.cars:
			car.move()

	@classmethod
	def randcar(self):
		if self.level:
			road = random.randrange(len(self.level))
			speed = random.randint(16, 36)

			self.cars.append(Car(road, speed, colconv[selcolor.get()]))

	@classmethod
	def clearcar(self):
		for car in self.cars:
			car.destruct()
		self.cars.clear()

# scale root function
def q(n):
	return int(n ** 0.75) * 5

# angle calculation functions
def headx(x, y, dx, dy, qy):
	if y == dy:
		return y
	return round((qy - y) * (dx - x) / (dy - y) + x)

def heady(x, y, dx, dy, qx):
	if x == dx:
		return x
	return round((qx - x) * (dy - y) / (dx - x) + y)

# get number's sign
def sign(n):
	if n > 0:
		return 1
	elif n < 0:
		return -1
	return 0

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
targeta = [0, 0]

# car class
class Car:
	def __init__(self, index, mv, col):
		self.mv = mv # to load
		self.v = 0

		self.index = index # to load
		self.pos = list(System.road(index)[0:2]) # to load

		self.id = c.create_oval(int(self.pos[0]) + System.pos[0] - q(System.scale),
			int(self.pos[1]) + System.pos[1] - q(System.scale),
			int(self.pos[0]) + System.pos[0] + q(System.scale),
			int(self.pos[1]) + System.pos[1] + q(System.scale), fill="#%06x" % col)

		self.queue = [index] # to load
		self.cm = covers[System.rtype[index]]

	def update(self):
		c.coords(self.id, int(self.pos[0]) * System.scale + System.pos[0] - q(System.scale),
			int(self.pos[1]) * System.scale + System.pos[1] - q(System.scale),
			int(self.pos[0]) * System.scale + System.pos[0] + q(System.scale),
			int(self.pos[1]) * System.scale + System.pos[1] + q(System.scale))

	def move(self):
		if self.cm > self.mv:
			v = self.cm
		else:
			v = self.mv
		if self.v >= v:
			if self.queue:
				cd = System.level[self.queue[0]]
				df = cd[0] - cd[2], cd[1] - cd[3]

				if abs(df[0]) >= abs(df[1]):
					target1[0] = self.pos[0] - sign(df[0])
					target1[1] = heady(*cd, target1[0])

					target2[0] = self.pos[0] - sign(df[0]) * 2
					target2[1] = heady(*cd, target2[0])

					target3[0] = self.pos[0] - sign(df[0]) * 3
					target3[1] = heady(*cd, target3[0])

					target4[0] = self.pos[0] - sign(df[0]) * 4
					target4[1] = heady(*cd, target4[0])

					target5[0] = self.pos[0] - sign(df[0]) * 5
					target5[1] = heady(*cd, target5[0])

					target6[0] = self.pos[0] - sign(df[0]) * 6
					target6[1] = heady(*cd, target6[0])

					target7[0] = self.pos[0] - sign(df[0]) * 7
					target7[1] = heady(*cd, target7[0])

					target8[0] = self.pos[0] - sign(df[0]) * 8
					target8[1] = heady(*cd, target8[0])

					target9[0] = self.pos[0] - sign(df[0]) * 9
					target9[1] = heady(*cd, target9[0])

					targeta[0] = self.pos[0] - sign(df[0]) * 10
					targeta[1] = heady(*cd, targeta[0])

					m = 1
					for car in System.cars:
						if car == self:
							continue
						if car.pos == target1:
							m = 0
							break
						elif car.pos == target2:
							m = 0
							break
						elif car.pos == target3:
							m = 0
							break
						elif car.pos == target4:
							m = 0
							break
						elif car.pos == target5:
							m = 0
							break
						elif car.pos == target6:
							m = 0
							break
						elif car.pos == target7:
							m = 0
							break
						elif car.pos == target8:
							m = 0
							break
						elif car.pos == target9:
							m = 0
							break
						elif car.pos == targeta:
							m = 0
							break

					if m:
						self.pos[0] = target1[0]
						self.pos[1] = target1[1]
				else:
					target1[1] = self.pos[1] - sign(df[1])
					target1[0] = headx(*cd, target1[1])

					target2[1] = self.pos[1] - sign(df[1]) * 2
					target2[0] = headx(*cd, target2[1])

					target3[1] = self.pos[1] - sign(df[1]) * 3
					target3[0] = headx(*cd, target3[1])

					target4[1] = self.pos[1] - sign(df[1]) * 4
					target4[0] = headx(*cd, target4[1])

					target5[1] = self.pos[1] - sign(df[1]) * 5
					target5[0] = headx(*cd, target5[1])

					target6[1] = self.pos[1] - sign(df[1]) * 6
					target6[0] = headx(*cd, target6[1])

					target7[1] = self.pos[1] - sign(df[1]) * 7
					target7[0] = headx(*cd, target7[1])

					target8[1] = self.pos[1] - sign(df[1]) * 8
					target8[0] = headx(*cd, target8[1])

					target9[1] = self.pos[1] - sign(df[1]) * 9
					target9[0] = headx(*cd, target9[1])

					targeta[1] = self.pos[1] - sign(df[1]) * 10
					targeta[0] = headx(*cd, targeta[1])

					m = 1
					for car in System.cars:
						if car == self:
							continue
						if car.pos == target1:
							m = 0
							break
						elif car.pos == target2:
							m = 0
							break
						elif car.pos == target3:
							m = 0
							break
						elif car.pos == target4:
							m = 0
							break
						elif car.pos == target5:
							m = 0
							break
						elif car.pos == target6:
							m = 0
							break
						elif car.pos == target7:
							m = 0
							break
						elif car.pos == target8:
							m = 0
							break
						elif car.pos == target9:
							m = 0
							break
						elif car.pos == targeta:
							m = 0
							break

					if m:
						self.pos[0] = target1[0]
						self.pos[1] = target1[1]

				if cd[2:4] == self.pos:
					self.queue.pop(0)

					seq = []
					for i in range(len(System.level)):
						if System.level[i][0:2] == cd[2:4]:
							seq.append(i)

					if seq:
						g = random.choice(seq)
						self.queue.append(g)
						self.cm = covers[System.rtype[g]]
						self.v = -40
				if self.v > 0:
					self.v = 0
				self.update()
		else:
			self.v += 1

	def save(self):
		pass

	def load(self, obj):
		pass

	def destruct(self):
		c.delete(self.id)

# light class
class Light:
	def __init__(self, i, r, g, t, v):
		self.pause = r, g
		self.i = i
		self.v = v
		self.state = 0
		self.t = t
		if t >= g:
			self.id = c.create_oval(*self.loc(), fill="#00FF00")
		else:
			self.id = c.create_oval(*self.loc(), fill="#FF0000")

	def update(self):
		if self.t >= self.pause[0] + self.pause[1]:
			self.t = 0
			self.s = 0
			c.itemconfig(self.id, fill="#FF0000")
		else:
			self.t += 1
			if t == self.pause[1]:
				self.s = 1
				c.itemconfig(self.id, fill="#00FF00")
		c.coords(self.id, *self.loc())

	def loc(self):
		x = System.pos[0] + System.level[self.i][2] * System.scale
		y = heady(*System.level[self.i], x)
		return x - 10, y - 10, x + 10, y + 10

# null function
def null(*args, **kwargs):
	pass

# terminate function
def terminate():
	global TERMINATE
	TERMINATE = True
	exit()

# default speed function
def defspeed():
	global pause
	pause = 240

	speedmenu.entryconfigure(0, label="Speed: %s Ticks" % pause)

# increase speed function
def incspeed(super=0):
	global pause

	if super:
		pause += 60
	pause += 20

	speedmenu.entryconfigure(0, label="Speed: %s Ticks" % pause)

# decrease speed function
def decspeed(super=0):
	global pause

	if super:
		pause -= 60
	pause -= 20

	if pause < 20:
		pause = 20

	speedmenu.entryconfigure(0, label="Speed: %s Ticks" % pause)

# fullscreen function
def setFullscreen():
	global FULLSCREEN
	FULLSCREEN = not FULLSCREEN
	root.attributes("-fullscreen", FULLSCREEN)

	c.config(width=root.winfo_width(), height=root.winfo_height())

# time functions
def timestop():
	global MOVE
	MOVE = 0

# time functions
def timeresume():
	global MOVE
	MOVE = 1

# main loop setup
menu = Menu(root)

filemenu = Menu(menu, tearoff=0)
filemenu.add_command(label="New", command=System.new)
filemenu.add_command(label="Open", command=System.open)
filemenu.add_command(label="Save", command=System.save)
filemenu.add_command(label="Save As", command=System.saveas)

speedmenu = Menu(menu, tearoff=0)
speedmenu.add_command(label="Speed: 240 Ticks")
speedmenu.add_command(label="Default Speed", command=defspeed)
speedmenu.add_separator()
speedmenu.add_command(label="Time Stop", command=timestop)
speedmenu.add_command(label="Time Resume", command=timeresume)
speedmenu.add_separator()
speedmenu.add_command(label="Speed Up", command=incspeed)
speedmenu.add_command(label="Slow Down", command=decspeed)
speedmenu.add_separator()
speedmenu.add_command(label="Super Speed Up", command=lambda: incspeed(1))
speedmenu.add_command(label="Super Slow Down", command=lambda: decspeed(1))

carmenu = Menu(menu, tearoff=0)
carsub = Menu(carmenu, tearoff=0)
carcols = [
	"Black", "Dark Gray", "Light Gray", "White",
	"Red", "Dark Red", "Green", "Dark Green",
	"Blue", "Dark Blue", "Yellow", "Orange",
	"Pink", "Purple", "Light Blue", "Mint"
]
colconv = [
	0x000000, 0x505050, 0xA0A0A0, 0xFFFFFF,
	0xFF0000, 0xA00000, 0x00FF00, 0x00A000,
	0x0000FF, 0x0000A0, 0xFFFF00, 0xFF8000,
	0xFF40FF, 0xA000FF, 0x00FFFF, 0xC0FFEE
]
selcolor = IntVar()
count = 0
for color in carcols:
	carsub.add_radiobutton(label=color, value=count, variable=selcolor)
	count += 1
carmenu.add_cascade(label="Car Color", menu=carsub)
carmenu.add_separator()
carmenu.add_command(label="Add Car", command=System.randcar)
carmenu.add_command(label="Remove All Cars", command=System.clearcar)

menu.add_cascade(label="File", menu=filemenu)
menu.add_cascade(label="Speed", menu=speedmenu)
menu.add_cascade(label="Cars", menu=carmenu)
menu.add_command(label="Fullscreen", command=setFullscreen)
menu.add_command(label="Exit", command=terminate)

root.bind_all("<Prior>", System.up)
root.bind_all("<Next>", System.down)
root.bind_all("<Home>", System.reset)
root.bind_all("<End>", System.home)

root.bind_all("<MouseWheel>", System.mouse)
root.bind_all("<Button-1>", System.press)
root.bind_all("<B1-Motion>", System.bmotion)

c.pack()
# ============================
System.load("tour.db")
System.cars.append(Car(0, 20, 0xffffff))
System.cars.append(Car(1, 10, 0x000000))
# ============================

def loop():
	global pause
	while not TERMINATE:
		if MOVE:
			System.move()
		clock.tick(pause)

thread = threading.Thread(target=loop)
thread.start()

root.config(menu=menu)
root.mainloop()
# tk init
from tkinter import *
import random
import threading, lib
from pygame.time import Clock

root = Tk()
root.title("App")

root.geometry("1024x576")
root.resizable(0, 0)

c = Canvas(root, width=1024, height=576, highlightthickness=0)
clock = Clock()

pause = 100

TERMINATE = False
FULLSCREEN = 0
MOVE = 1

covers = {
	0: 30,
	1: 60,
	2: 90,
	3: 120,
	4: 150,
	5: 180
}
covcol = {
	0: "#B08440",
	1: "#1020FF",
	2: "#209040",
	3: "#E8E010",
	4: "#FF9020",
	5: "#FF2040"
}

# system object
class System:
	roads = lib.Road.select()
	level = []
	rtype = []

	for road in roads:
		if road.covering in covers:
			rtype.append(road.covering)
		else:
			rtype.append(0)
		level.append([road.x1, road.y1, road.x2, road.y2])

	print(level)

	size = 5, 5
	pos = [0, 0]

	scale = 1.0
	lines = []

	cars = []

	count = 0
	for road in level:
		lines.append(c.create_line(*road, fill=covcol[rtype[count]]))
		count += 1

	del count, roads

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
		self.update()

	@classmethod
	def up(self, evt):
		self.scale *= 1.2
		self.update()

	@classmethod
	def reset(self, evt):
		self.scale = 1
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
				self.up(None)
		else:
			for t in range(val):
				self.down(None)

	@classmethod
	def new(self, evt):
		# new file
		pass

	@classmethod
	def open(self, evt):
		# open file
		pass

	@classmethod
	def save(self, evt):
		# save file
		pass

	@classmethod
	def saveas(self, evt):
		# save as file
		pass

	@classmethod
	def move(self):
		for car in self.cars:
			car.move()

# scale root function
def q(n):
	return int(n ** 0.75) * 5

# angle calculation functions
def headx(x, y, dx, dy, qy):
	if x == dx:
		return x
	return round((qy - y) * (dx - x) / (dy - y) + x)

def heady(x, y, dx, dy, qx):
	if y == dy:
		return y
	return round((qx - x) * (dy - y) / (dx - x) + y)

# get number's sign
def sign(n):
	if n > 0:
		return 1
	elif n < 0:
		return -1
	return 0

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

	def update(self):
		c.coords(self.id, int(self.pos[0]) * System.scale + System.pos[0] - q(System.scale),
			int(self.pos[1]) * System.scale + System.pos[1] - q(System.scale),
			int(self.pos[0]) * System.scale + System.pos[0] + q(System.scale),
			int(self.pos[1]) * System.scale + System.pos[1] + q(System.scale))

	def move(self):
		if self.v == self.mv:
			if self.queue:
				cd = System.level[self.queue[0]]
				df = cd[0] - cd[2], cd[1] - cd[3]

				if abs(df[0]) >= abs(df[1]):
					self.pos[0] -= sign(df[0])
					self.pos[1] = heady(*cd, self.pos[0])
				else:
					self.pos[1] -= sign(df[1])
					self.pos[0] = headx(*cd, self.pos[1])

				if cd[2:4] == self.pos:
					self.queue.pop(0)

					seq = []
					for i in range(len(System.level)):
						if System.level[i][0:2] == cd[2:4]:
							seq.append(i)

					if seq:
						self.queue.append(random.choice(seq))
						if random.randrange(8) == 0:
							self.v = -random.randint(pause, pause * 2)
				self.v = 0
				self.update()
		else:
			self.v += 1

	def save(self):
		pass

	def load(self, obj):
		pass

# append some cars
System.cars.append(Car(0, 20, 0xffffff))
System.cars.append(Car(0, 10, 0x000000))

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
	pause = 160

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

# main loop setup
menu = Menu(root)

filemenu = Menu(menu, tearoff=0)
filemenu.add_command(label="New", command=System.new)
filemenu.add_command(label="Open", command=System.open)
filemenu.add_command(label="Save", command=System.save)
filemenu.add_command(label="Save As", command=System.saveas)

speedmenu = Menu(menu, tearoff=0)
speedmenu.add_command(label="Speed: 160 Ticks")
speedmenu.add_command(label="Default Speed", command=defspeed)
speedmenu.add_separator()
speedmenu.add_command(label="Speed Up", command=incspeed)
speedmenu.add_command(label="Slow Down", command=decspeed)
speedmenu.add_separator()
speedmenu.add_command(label="Super Speed Up", command=lambda: incspeed(1))
speedmenu.add_command(label="Super Slow Down", command=lambda: decspeed(1))

menu.add_cascade(label="File", menu=filemenu)
menu.add_cascade(label="Speed", menu=speedmenu)
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
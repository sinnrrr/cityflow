from os import system
from sys import argv
from sys import exit

from threading import Thread

def run():
	print("Python Injector v1.1")

	while 1:
		inp = input("> ")
		if inp.rstrip() == "break":
			break
		elif inp.rstrip() == "clear":
			system("cls")
		try:
			exec(inp, globals())
		except BaseException as exp:
			print("%s: %s" % (type(exp).__name__, exp))

t = Thread(target=run)
t.start()

with open(argv[1]) as f:
	exec(f.read())
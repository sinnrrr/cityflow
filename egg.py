from ctypes import windll
import sys, os
string = "Oh. You found me. Please, activate me:\x00"
code = ""

if ord(string[38]):
	while code != "01110001":
		res = windll.user32.MessageBoxW(0, "Please enter the code\nCurrent code: " + code, "Entry", 0x13)
		if res == 2:
			if len(code) == 0:
				sys.exit(113)
			code = code[:-1]
		elif res == 7:
			code += "0"
		else:
			code += "1"
	if windll.user32.MessageBoxW(0, "Access granted!\nContinue?", "Are you sure?", 0x34) == 6:
		pass
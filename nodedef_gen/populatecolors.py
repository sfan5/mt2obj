#!/usr/bin/env python
import sys
from PIL import Image

def avg2(a, b):
	return int((a + b) / 2.0)

def avg2t3i0(a, b):
	return tuple(avg2(t[0], t[1]) for t in zip(a[:3], b[:3]))

def avgcolor(name):
	inp = Image.open(name)
	inp = inp.convert('RGBA')
	ind = inp.load()
	avgc = -1
	for x in range(inp.size[0]):
		for y in range(inp.size[1]):
			pxl = ind[x, y]
			if pxl[3] < 128:
				continue
			if avgc == -1:
				avgc = pxl[:3]
			else:
				avgc = avg2t3i0(avgc, pxl)
	if avgc == -1:
		return "0 0 0"
	else:
		return "%d %d %d" % avgc

if len(sys.argv) <= 2:
	print("Usage: %s <in> <out>" % sys.argv[0])
else:
	fin = open(sys.argv[1], "r")
	fout = open(sys.argv[2], "w")
	for line in fin:
		line = line[:-1] # cut off the \n
		# nodename modelname r g b params texture
		#                    ^ ^ ^        ^^^^^^^
		a = line.split(" ")
		fout.write("%s %s %s %s\n" % (a[0], a[1], avgcolor(a[6]), a[5]))
	fin.close()
	fout.close()
		


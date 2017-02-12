#!/usr/bin/env python3
import sys
from PIL import Image

def mix(a, b):
	return (
		(a[0] + b[0]) / 2,
		(a[1] + b[1]) / 2,
		(a[2] + b[2]) / 2
	)

def avgcolor(name):
	inp = Image.open(name).convert('RGBA')
	ind = inp.load()
	avgc = None
	for x in range(inp.size[0]):
		for y in range(inp.size[1]):
			pxl = ind[x, y]
			if pxl[3] < 128:
				continue
			pxl = pxl[:3]
			avgc = pxl if avgc is None else mix(avgc, pxl)
	if avgc is None:
		return "0 0 0"
	else:
		return "%d %d %d" % avgc

if len(sys.argv) <= 2:
	print("Usage: %s <in> <out>" % sys.argv[0])
else:
	fin = open(sys.argv[1], "r")
	fout = open(sys.argv[2], "w")
	for line in fin:
		line = line.rstrip("\n")
		# nodename modelname r g b params texture
		#                    ^ ^ ^        ^^^^^^^
		a = line.split(" ")
		fout.write("%s %s %s %s\n" % (a[0], a[1], avgcolor(a[6]), a[5]))
	fin.close()
	fout.close()
		


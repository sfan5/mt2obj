#!/usr/bin/env python3
import zlib
import struct
import sys
import time
import getopt
import re

# mt2obj - MTS schematic to OBJ converter
# Copyright (C) 2014 sfan5
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

def convert(desc, vals):
	out = tuple()
	i = 0
	for val in vals:
		if val is None:
			i += 1
			continue
		c = desc[i]
		if c == '0': # skip
			pass
		elif c == 'x': # copy
			out += val,
		elif c == 's': # string
			out += str(val),
		elif c == 'i': # int
			out += int(val),
		elif c == 'f': # float
			out += float(val),
		elif c == 'h': # hexadecimal int
			out += int(val, 16),
		elif c == 'b': # bool
			out += val.strip().lower() in ['1', 'true', 'yes'],
		i += 1
	return out
			
def pp_new(var, strip_empty=False):
	return ({'if_state': 0, '_strip_empty': strip_empty}, var)

def pp_process(ctx, line):
	for k in ctx[1]:
		line = line.replace('{' + k + '}', ctx[1][k])
	if ctx[0]['_strip_empty'] and line.strip() == '':
		return None
	elif line.startswith('# '): # e.g.: # comment
		return None
	elif line.startswith('#define'): # e.g.: #define name value that may contain spaces
		tmp = line.split(' ')
		if len(tmp) < 3:
			raise Exception('missing something...')
		ctx[1][tmp[1]] = ' '.join(tmp[2:])[:-1] # [:-1] to cut off the \n at the end
		return None
	elif line.startswith('#if'): #e.g.: #if {name}
		tmp = line.split(' ')
		if len(tmp) < 2:
			raise Exception('Missing something..')
		tmp = tmp[1]
		if tmp.strip().lower() in ['1', 'true', 'yes']:
			ctx[0]['if_state'] = 1 # don't ignore current lines, expecting #else or #endif
		else:
			ctx[0]['if_state'] = 2 # ignore current lines, expecting #else or #endif
		return None
	elif line.startswith('#ifdef'): #e.g.: #ifdef name
		tmp = line.split(' ')
		if len(tmp) < 2:
			raise Exception('Missing something..')
		tmp = tmp[1]
		if tmp in ctx[1].keys():
			ctx[0]['if_state'] = 1 # don't ignore current lines, expecting #else or #endif
		else:
			ctx[0]['if_state'] = 2 # ignore current lines, expecting #else or #endif
		return None
	elif line.startswith('#else') and ctx[0]['if_state'] == 1:
		ctx[0]['if_state'] = 4 # ignore current lines, expecting #endif
	elif line.startswith('#else') and ctx[0]['if_state'] == 2:
		ctx[0]['if_state'] = 3 # don't ignore current lines, expecting #endif
	elif line.startswith('#endif'):
		if ctx[0]['if_state'] not in [3, 4]:
			raise Exception('stray #endif')
		ctx[0]['if_state'] = 0 # no #if in sight
	else:
		if ctx[0]['if_state'] in [2, 4]:
			pass # ignore, see above
		else:
			return line
	return None

def parse_arglist(s):
	if s == ':':
		return {}
	state = 1
	tmp1 = ''
	tmp2 = ''
	out = {}
	for c in s:
		if state == 1: # part before =
			if c == ':':
				if tmp1 == '':
					raise Exception('name must be non-empty')
				out[tmp1] = '1' # set to '1' if no value given, e.g. 'foo=1:bar:cats=yes' would set bar to '1'
			elif c == '=':
				state = 2
			else:
				tmp1 += c
		elif state == 2: # part after =
			if c == ':':
				if tmp1 == '':
					raise Exception('name must be non-empty')
				out[tmp1] = tmp2
			else:
				tmp2 += c
	if tmp1 != '' and state == 1:
		out[tmp1] = '1'
	elif tmp1 != '' and state == 2:
		out[tmp1] = tmp2
	return out
			

nodetbl = {}

r_entry = re.compile(r'^(\S+) (\S+) (\d+) (\d+) (\d+) (\S+)(?: (\d+))?$')

f = open("nodes.txt", "r")
for l in f:
	m = r_entry.match(l)
	nodetbl[m.group(1)] = convert('siiisi', m.groups()[1:])
f.close()

optargs, args = getopt.getopt(sys.argv[1:], 't')

if len(args) < 1:
	print("Usage: %s <.mts schematic>" % sys.argv[0])
	print("Converts .mts schematics to Wavefront .obj geometry files")
	print("")
	print("Output files are written into directory of source file.")
	print('')
	print('Options:')
	print('\t-t\t\tEnable textures')
	exit(1)
else:
	sch = open(args[0], "rb")
	if sch.read(4) != b"MTSM":
		print("This file does not look like an MTS schematic..")
		exit(1)
	v = struct.unpack("!H", sch.read(2))[0]
	if v != 3:
		print("Wrong file version: got %d, expected %d" % (v, 3))
		exit(1)
	width, height, depth = struct.unpack("!HHH", sch.read(6))
	sch.seek(height, 1)
	nodecount = struct.unpack("!H", sch.read(2))[0]
	nodemap = {}
	for i in range(nodecount):
		l = struct.unpack("!H", sch.read(2))[0]
		name = sch.read(l).decode('ascii')
		nodemap[i] = name
	# TODO use zlib.decompressobj() instead of decompressing everything at once
	cdata = sch.read()
	sch.close()
	data = zlib.decompress(cdata)
	del cdata
	filepart = args[0][:args[0].find(".")]
	obj = open(filepart + ".obj", "w")
	obj.write("# Exported by mt2obj\nmtllib %s\n\n\n" % (filepart + ".mtl", ))
	i = 0
	foundnodes = []
	unknownnodes = []
	for x in range(width):
		for y in range(height):
			for z in range(depth):
				off = (x + y*width + z*width*height) * 2
				nid = struct.unpack("!H", data[off:off + 2])[0]
				nname = nodemap[nid]
				if nname == "air":
					continue
				if not nname in nodetbl.keys():
					if not nname in unknownnodes:
						unknownnodes.append(nname)
					continue
				else:
					if not nname in foundnodes:
						foundnodes.append(nname)
				obj.write("o node%d\n" % i)
				obj.write("usemtl %s\n" % nname.replace(":", "__"))
				objd = open("models/" + nodetbl[nname][0] + ".obj", 'r')
				tmp = parse_arglist(nodetbl[nname][4])
				tmp['TEXTURES'] = str(('-t', '') in optargs)
				ppctx = pp_new(tmp, strip_empty=True)
				for line in objd:
					line = pp_process(ppctx, line)
					if line is None:
						continue
					if line.startswith("v "):
						tmp = line.split(" ")
						vx, vy, vz = float(tmp[1]), float(tmp[2]), float(tmp[3])
						vx += x
						vy += y
						vz += z
						obj.write("v %f %f %f\n" % (vx, vy, vz))
					else:
						obj.write(line)
				del ppctx
				objd.close()
				obj.write("\n")
				i += 1
	obj.close()
	mtl = open(filepart + ".mtl", "w")
	mtl.write("# Generated by mt2obj\n\n\n")
	for node in foundnodes:
		mtl.write("newmtl %s\n" % node.replace(":", "__"))
		c = nodetbl[node]
		mtld = open("models/" + nodetbl[node][0] + ".mtl", 'r')
		if len(c) > 5: # if there is transparency
			tmp1 = c[5]/255
		else:
			tmp1 = 1.0
		tmp = {
			'r': str(c[1]/255),
			'g': str(c[2]/255),
			'b': str(c[3]/255),
			'a': str(tmp1),
			'TEXTURES': str(('-t', '') in optargs),
		}
		tmp.update(parse_arglist(nodetbl[node][4]))
		ppctx = pp_new(tmp, strip_empty=True)
		for line in mtld:
			line = pp_process(ppctx, line)
			if line is None:
				continue
			mtl.write(line)
		del ppctx
		mtl.write("\n")
		mtld.close()
	mtl.close()
	if len(unknownnodes) > 0:
		print("There were some unknown nodes that were ignored during the conversion:")
		for e in unknownnodes:
			print(e)


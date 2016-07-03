#!/usr/bin/env python3
# mt2obj - MTS schematic to OBJ converter
# Copyright (C) 2014-16 sfan5
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

import zlib
import struct
import sys
import time
import getopt
import re

def str2bool(text):
	return text.strip().lower() in ["1", "true", "yes"]

def splitinto(text, delim, n):
	ret = text.split(delim)
	if len(ret) <= n:
		return ret
	else:
		return ret[:n-1] + [delim.join(ret[n-1:]),]

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
			out += str2bool(val),
		i += 1
	return out

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

class PreprocessingException(Exception):
	pass

class Preprocessor():
	def __init__(self, omit_empty=False):
		self.state = 0
		# 0: default state
		# 1: expecting #else or #endif
		# 2: discard input, expecting #else or #endif
		# 3: expecting #endif
		# 4: discard input, expecting #endif
		self.vars = {}
		self.omit_empty = omit_empty
	def _splitinto(self, text, delim, n):
		r = splitinto(text, delim, n)
		if len(r) < n:
			raise PreprocessingException("Further input missing")
	def _assertne(self, text):
		if text.strip("\t ") == "":
			raise PreprocessingException("Further input missing")
	def setvar(self, var, value):
		self.vars[var] = value
	def getvar(self, var):
		return self.vars[var]
	def addvars(self, vars):
		self.vars.update(vars)
	def process(self, line):
		# comments
		if line.startswith("# "):
			return None
		# replacements
		tmp = ""
		last = 0
		for m in re.finditer(r'{([a-zA-Z0-9_-]+)}', line):
			name = m.group(1)
			if name not in self.vars.keys():
				tmp += line[last:m.start()] + "???"
				last = m.end()
				continue
				#raise PreprocessingException("Undefined variable '%s'" % name)
			tmp += line[last:m.start()] + self.vars[name]
			last = m.end()
		if len(tmp) > 0:
			line = tmp
		# omit empty
		if self.omit_empty and line.strip("\t ") == "":
			return None
		# instructions
		if line.startswith("#"):
			inst = re.match(r'#([a-zA-Z0-9_]+)(?: (.*))?', line)
			if inst is None:
				raise PreprocessingException("Invalid syntax")
			inst, args = inst.group(1), inst.group(2)
			if inst == "define":
				args = self._splitinto(args, " ", 2)
				self.vars[args[0]] = args[1]
				return None
			elif inst == "if":
				self._assertne(args)
				self.state = 1 if str2bool(args) else 2
			elif inst == "ifdef":
				self._assertne(args)
				self.state = 1 if args in self.vars.keys() else 2
			elif inst == "else":
				if self.state not in (1, 2):
					raise PreprocessingException("Stray #else")
				self.state = 4 if self.state == 1 else 3
			elif inst == "endif":
				if self.state not in (3, 4):
					raise PreprocessingException("Stray #endif")
				self.state = 0
			return None
		# normal lines
		if self.state in (2, 4):
			return None
		return line

nodetbl = {}

r_entry = re.compile(r'^(\S+) (\S+) (\d+) (\d+) (\d+) (\S+)(?: (\d+))?$')

f = open("nodes.txt", "r")
for l in f:
	m = r_entry.match(l)
	nodetbl[m.group(1)] = convert('siiisi', m.groups()[1:])
f.close()

optargs, args = getopt.getopt(sys.argv[1:], 't')

# TODO: structure code below
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
	if v != 4:
		print("Wrong file version: got %d, expected %d" % (v, 4))
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
				pp = Preprocessor(omit_empty=True)
				pp.addvars(parse_arglist(nodetbl[nname][4]))
				pp.setvar("TEXTURES", str(('-t', '') in optargs))
				for line in objd:
					line = pp.process(line[:-1])
					if line is None:
						continue
					if line.startswith("v "):
						tmp = line.split(" ")
						vx, vy, vz = float(tmp[1]), float(tmp[2]), float(tmp[3])
						vx += x
						vy += y
						vz += z
						obj.write("v %.1f %.1f %.1f\n" % (vx, vy, vz))
					else:
						obj.write(line + "\n")
				del pp
				objd.close()
				obj.write("\n")
				i += 1
	obj.close()
	mtl = open(filepart + ".mtl", "w")
	mtl.write("# Generated by mt2obj\n\n")
	for node in foundnodes:
		mtl.write("newmtl %s\n" % node.replace(":", "__"))
		c = nodetbl[node]
		mtld = open("models/" + nodetbl[node][0] + ".mtl", 'r')
		pp = Preprocessor(omit_empty=True)
		pp.addvars(parse_arglist(nodetbl[node][4]))
		pp.addvars({
			'r': str(c[1]/255),
			'g': str(c[2]/255),
			'b': str(c[3]/255),
			'a': str(c[5]/255 if len(c) > 5 else 1.0),
			'TEXTURES': str(('-t', '') in optargs),
		})
		for line in mtld:
			line = pp.process(line[:-1])
			if line is None:
				continue
			mtl.write(line + "\n")
		del pp
		mtl.write("\n")
		mtld.close()
	mtl.close()
	if len(unknownnodes) > 0:
		print("There were some unknown nodes that were ignored during the conversion:")
		for e in unknownnodes:
			print(e)


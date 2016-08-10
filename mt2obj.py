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

def getarg(optargs, name, default=None):
	for a in optargs:
		if a[0] == name:
			return a[1]
	return default

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
		elif c == 'A': # special: arglist
			out += parse_arglist(val),
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

class MtsReader():
	def __init__(self):
		self.dim = (0, 0, 0) # W x H x D
		self.namemap = {}
		self.data = b""
	def decode(self, f):
		assert(f.mode == "rb")
		if f.read(4) != b"MTSM":
			raise Exception("Incorrect magic value, this isn't a schematic!")
		ver = struct.unpack("!H", f.read(2))[0]
		if ver not in (3, 4):
			raise Exception("Wrong file version: got %d, expected 3 or 4" % ver)
		self.dim = struct.unpack("!HHH", f.read(6))
		f.seek(self.dim[1], 1) # skip some stuff
		count = struct.unpack("!H", f.read(2))[0]
		for i in range(count):
			l = struct.unpack("!H", f.read(2))[0]
			self.namemap[i] = f.read(l).decode("ascii")
		self.data = zlib.decompress(f.read())
	def dimensions(self):
		return self.dim
	def getnode(self, x, y, z):
		off = (x + y*self.dim[0] + z*self.dim[0]*self.dim[1]) * 2
		nid = struct.unpack("!H", self.data[off:off+2])[0]
		return self.namemap[nid]

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
				# TODO: this is currently required as undefined vars can
				#       occur in ifdef sections (which are processed later)
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

def usage():
	print("Usage: %s <.mts schematic>" % sys.argv[0])
	print("Converts .mts schematics to Wavefront .obj geometry files")
	print("Output files are written into directory of source file.")
	print("")
	print("Options:")
	print("  -t    Enable textures")
	print("  -n    Set path to nodes.txt")
	exit(1)


optargs, args = getopt.getopt(sys.argv[1:], 'tn:')
if len(args) != 1:
	usage()

nodetbl = {}
r_entry = re.compile(r'(\S+) (\S+) (\d+) (\d+) (\d+) (\S+)(?: (\d+))?')
with open(getarg(optargs, "-n", default="nodes.txt"), "r") as f:
	for line in f:
		m = r_entry.match(line)
		nodetbl[m.group(1)] = convert('siiiAi', m.groups()[1:])

schem = MtsReader()
with open(args[0], "rb") as f:
	try:
		schem.decode(f)
	except Exception as e:
		print(str(e), file=sys.stderr)
		exit(1)

filepart = ".".join(args[0].split(".")[:-1])
objfile = filepart + ".obj"
mtlfile = filepart + ".mtl"

nodes_seen = set()
with open(objfile, "w") as obj:
	obj.write("# Exported by mt2obj (https://github.com/sfan5/mt2obj)\nmtllib %s\n\n\n" % mtlfile)
	i = 0
	for x in range(schem.dimensions()[0]):
		for y in range(schem.dimensions()[1]):
			for z in range(schem.dimensions()[2]):
				node = schem.getnode(x, y, z)
				if node == "air":
					continue
				nodes_seen.add(node)
				if node not in nodetbl.keys():
					continue
				obj.write("o node%d\nusemtl %s\n" % (i, node.replace(":", "__")))
				with open("models/%s.obj" % nodetbl[node][0], "r") as objdef:
					pp = Preprocessor(omit_empty=True)
					pp.addvars(nodetbl[node][4])
					pp.setvar("TEXTURES", "1" if getarg(optargs, "-t") == "" else "0")
					for line in objdef:
						line = pp.process(line.rstrip("\r\n"))
						if line is None:
							continue
						# Translate vertice coordinates
						if line.startswith("v "):
							vx, vy, vz = (float(e) for e in line.split(" ")[1:])
							vx += x
							vy += y
							vz += z
							obj.write("v %.1f %.1f %.1f\n" % (vx, vy, vz))
						else:
							obj.write(line)
							obj.write("\n")
				obj.write("\n")
				i += 1

with open(mtlfile, "w") as mtl:
	mtl.write("# Generated by mt2obj (https://github.com/sfan5/mt2obj)\n\n")
	for node in nodes_seen:
		if node not in nodetbl.keys():
			continue
		mtl.write("newmtl %s\n" % node.replace(":", "__"))
		c = nodetbl[node]
		with open("models/%s.mtl" % c[0], "r") as mtldef:
			pp = Preprocessor(omit_empty=True)
			pp.addvars(c[4])
			pp.addvars({
				"r": str(c[1]/255),
				"g": str(c[2]/255),
				"b": str(c[3]/255),
				"a": str(c[5]/255 if len(c) > 5 else 1.0),
				"TEXTURES": "1" if getarg(optargs, "-t") == "" else "0",
			})
			for line in mtldef:
				line = pp.process(line.rstrip("\r\n"))
				if line is None:
					continue
				mtl.write(line + "\n")
		mtl.write("\n")

nodes_unknown = nodes_seen - set(nodetbl.keys())
if len(nodes_unknown) > 0:
	print("There were some unknown nodes that were ignored during conversion:")
	for node in nodes_unknown:
		print("  " + node)



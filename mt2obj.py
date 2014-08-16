#!/usr/bin/env python3
import zlib
import struct
import sys
import time
import getopt

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

# sed -re 's/(.+?) (.+?) (.+?) (.+?)/\t"\1": ("cube", \2, \3, \4),/' < colors.txt
colors = {
	"nether:brick": ("cube", 40, 18, 18),
	"nether:portal": ("cube", 0, 0, 0),
	"nether:sand": ("cube", 40, 21, 21),
	"nether:glowstone": ("cube", 221, 197, 141),
	"nether:rack": ("cube", 40, 16, 16),
	"beds:bed_top_red": ("cube", 131, 22, 22),
	"beds:bed_bottom_blue": ("cube", 10, 11, 122),
	"beds:bed_bottom_grey": ("cube", 147, 147, 147),
	"beds:bed_bottom_white": ("cube", 215, 215, 215),
	"beds:bed_bottom_green": ("cube", 12, 92, 10),
	"beds:bed_bottom_orange": ("cube", 217, 123, 10),
	"beds:bed_top_blue": ("cube", 11, 12, 122),
	"beds:bed_bottom_violet": ("cube", 129, 10, 180),
	"beds:bed_top_green": ("cube", 13, 92, 11),
	"beds:bed_bottom_black": ("cube", 10, 10, 10),
	"beds:bed_bottom_yellow": ("cube", 215, 214, 0),
	"beds:bed_bottom_red": ("cube", 131, 21, 21),
	"beds:bed_top_white": ("cube", 215, 215, 215),
	"beds:bed_top_yellow": ("cube", 215, 214, 0),
	"beds:bed_top_violet": ("cube", 129, 11, 180),
	"beds:bed_top_grey": ("cube", 147, 147, 147),
	"beds:bed_top_black": ("cube", 11, 11, 11),
	"beds:bed_top_orange": ("cube", 216, 123, 11),
	"nuke:hardcore_mese_tnt": ("cube", 173, 173, 0),
	"nuke:iron_tnt": ("cube", 158, 158, 157),
	"nuke:hardcore_iron_tnt": ("cube", 158, 158, 157),
	"nuke:mese_tnt": ("cube", 173, 173, 0),
	"christmas:present_green_violet": ("cube", 189, 36, 157),
	"christmas:present_blue_green": ("cube", 62, 186, 50),
	"christmas:present_orange_green": ("cube", 62, 186, 50),
	"christmas:tree": ("cube", 45, 36, 24),
	"christmas:present_orange_violet": ("cube", 189, 36, 157),
	"christmas:present_blue_orange": ("cube", 245, 207, 20),
	"christmas:present_blue_violet": ("cube", 189, 36, 157),
	"christmas:star": ("cube", 236, 252, 55),
	"christmas:present_green_orange": ("cube", 245, 207, 20),
	"christmas:leaves": ("cube", 33, 54, 30),
	"snow:moss": ("cube", 51, 64, 29),
	"snow:snow5": ("cube", 225, 227, 255),
	"snow:snow3": ("cube", 225, 227, 255),
	"snow:needles_decorated": ("cube", 7, 50, 19),
	"snow:needles": ("cube", 6, 49, 18),
	"snow:snow8": ("cube", 225, 227, 255),
	"snow:star": ("cube", 214, 142, 0),
	"snow:snow": ("cube", 225, 227, 255),
	"snow:xmas_tree": ("cube", 87, 88, 28),
	"snow:sapling_pine": ("cube", 3, 54, 20),
	"snow:snow6": ("cube", 225, 227, 255),
	"snow:snow_block": ("cube", 225, 227, 255),
	"snow:snow7": ("cube", 225, 227, 255),
	"snow:snow_brick": ("cube", 223, 225, 253),
	"snow:dirt_with_snow": ("cube", 225, 227, 255),
	"snow:snow4": ("cube", 225, 227, 255),
	"snow:snow2": ("cube", 225, 227, 255),
	"snow:ice": ("cube", 155, 155, 254),
	"stairs:stair_wood_tile_full": ("cube", 78, 64, 44),
	"stairs:stair_mossycobble": ("cube", 102, 116, 85),
	"stairs:slab_jungle_wood": ("cube", 51, 35, 12),
	"stairs:slab_wood_tile_center": ("cube", 128, 100, 57),
	"stairs:stair_wood_tile": ("cube", 78, 65, 44),
	"stairs:stair_cobble": ("cube", 133, 133, 133),
	"stairs:slab_invisible": ("cube", 0, 0, 0),
	"stairs:stair_stonebrick": ("cube", 104, 100, 99),
	"stairs:slab_iron_glass": ("cube", 222, 222, 222),
	"stairs:stair_wood": ("cube", 128, 100, 57),
	"stairs:stair_stone": ("cube", 91, 88, 87),
	"stairs:stair_obsidian": ("cube", 16, 16, 16),
	"stairs:stair_copperblock": ("cube", 110, 86, 60),
	"stairs:stair_super_glow_glass": ("cube", 255, 255, 120),
	"stairs:slab_iron_stone": ("cube", 134, 134, 134),
	"stairs:stair_stone_tile": ("cube", 97, 97, 97),
	"stairs:stair_desert_stone": ("cube", 122, 74, 57),
	"stairs:slab_bronzeblock": ("cube", 116, 70, 26),
	"stairs:stair_goldblock": ("cube", 126, 116, 35),
	"stairs:stair_iron_checker": ("cube", 142, 142, 142),
	"stairs:stair_steelblock": ("cube", 153, 153, 153),
	"stairs:slab_coal_stone": ("cube", 70, 70, 70),
	"stairs:slab_obsidian_glass": ("cube", 16, 17, 17),
	"stairs:stair_sandstone": ("cube", 180, 162, 121),
	"stairs:stair_iron_stone": ("cube", 134, 134, 134),
	"stairs:slab_steelblock": ("cube", 153, 153, 153),
	"stairs:stair_split_stone_tile": ("cube", 97, 97, 97),
	"stairs:stair_brick": ("cube", 156, 157, 151),
	"stairs:stair_sandstonebrick": ("cube", 160, 144, 108),
	"stairs:slab_mossycobble": ("cube", 102, 116, 85),
	"stairs:stair_glass": ("cube", 192, 192, 227),
	"stairs:slab_cactus_checker": ("cube", 130, 138, 130),
	"stairs:slab_jungletree": ("cube", 120, 106, 78),
	"stairs:stair_coal_stone": ("cube", 70, 70, 70),
	"stairs:slab_junglewood": ("cube", 51, 35, 12),
	"stairs:stair_jungletree": ("cube", 120, 106, 78),
	"stairs:slab_wood": ("cube", 128, 100, 57),
	"stairs:stair_iron_stone_bricks": ("cube", 104, 98, 97),
	"stairs:stair_coal_checker": ("cube", 133, 133, 133),
	"stairs:stair_plankstone": ("cube", 66, 51, 23),
	"stairs:stair_obsidian_glass": ("cube", 16, 17, 17),
	"stairs:slab_desert_stone": ("cube", 122, 74, 57),
	"stairs:slab_iron_stone_bricks": ("cube", 104, 98, 97),
	"stairs:slab_glass": ("cube", 192, 192, 227),
	"stairs:stair_bronzeblock": ("cube", 116, 70, 26),
	"stairs:slab_desert_stonebrick": ("cube", 105, 64, 49),
	"stairs:slab_tree": ("cube", 66, 52, 35),
	"stairs:slab_stone": ("cube", 91, 88, 87),
	"stairs:stair_cactus_checker": ("cube", 130, 138, 130),
	"stairs:slab_diamondblock": ("cube", 103, 195, 201),
	"stairs:slab_super_glow_glass": ("cube", 255, 255, 120),
	"stairs:slab_cobble": ("cube", 133, 133, 133),
	"stairs:stair_tree": ("cube", 66, 52, 35),
	"stairs:slab_wood_tile": ("cube", 78, 65, 44),
	"stairs:slab_glow_glass": ("cube", 255, 226, 114),
	"stairs:slab_wood_tile_full": ("cube", 78, 64, 44),
	"stairs:stair_coal_stone_bricks": ("cube", 79, 76, 75),
	"stairs:slab_coal_glass": ("cube", 130, 130, 130),
	"stairs:stair_coal_glass": ("cube", 130, 130, 130),
	"stairs:slab_brick": ("cube", 156, 157, 151),
	"stairs:slab_stone_tile": ("cube", 97, 97, 97),
	"stairs:slab_goldblock": ("cube", 126, 116, 35),
	"stairs:slab_plankstone": ("cube", 66, 51, 23),
	"stairs:slab_coal_stone_bricks": ("cube", 79, 76, 75),
	"stairs:stair_jungle_wood": ("cube", 51, 35, 12),
	"stairs:stair_circle_stone_bricks": ("cube", 91, 88, 87),
	"stairs:slab_iron_checker": ("cube", 142, 142, 142),
	"stairs:stair_wood_tile_center": ("cube", 128, 100, 57),
	"stairs:slab_stonebrick": ("cube", 104, 100, 99),
	"stairs:slab_sandstonebrick": ("cube", 160, 144, 108),
	"stairs:stair_invisible": ("cube", 0, 0, 0),
	"stairs:stair_iron_glass": ("cube", 222, 222, 222),
	"stairs:stair_desert_stonebrick": ("cube", 105, 64, 49),
	"stairs:stair_diamondblock": ("cube", 103, 195, 201),
	"stairs:slab_sandstone": ("cube", 180, 162, 121),
	"stairs:slab_copperblock": ("cube", 110, 86, 60),
	"stairs:stair_glow_glass": ("cube", 255, 226, 114),
	"stairs:stair_junglewood": ("cube", 51, 35, 12),
	"stairs:slab_circle_stone_bricks": ("cube", 91, 88, 87),
	"stairs:slab_obsidian": ("cube", 16, 16, 16),
	"stairs:slab_coal_checker": ("cube", 133, 133, 133),
	"stairs:slab_split_stone_tile": ("cube", 97, 97, 97),
	"mg:savannawood": ("cube", 128, 113, 57),
	"mg:pineleaves": ("cube", 16, 30, 14),
	"mg:savannasapling": ("cube", 32, 36, 13),
	"mg:pinewood": ("cube", 120, 93, 66),
	"mg:pinetree": ("cube", 26, 21, 14),
	"mg:savannaleaves": ("cube", 70, 62, 41),
	"mg:pinesapling": ("cube", 12, 12, 5),
	"mg:savannatree": ("cube", 52, 51, 37),
	"mg:dirt_with_dry_grass": ("cube", 114, 99, 53),
	"bones:bones": ("cube", 74, 74, 74),
	"default:glass": ("cube", 192, 192, 227, 64),
	"default:water_flowing": ("cube", 39, 66, 106, 128),
	"default:junglesapling": ("cube", 37, 34, 14),
	"default:sandstonebrick": ("cube", 160, 144, 108),
	"default:furnace_active": ("cube", 97, 93, 91),
	"default:sign_wall": ("cube", 163, 141, 106),
	"default:lava_source": ("cube", 255, 100, 0),
	"default:goldblock": ("cube", 126, 116, 35),
	"default:obsidian_glass 16 17": ("cube", 17, 64, 16),
	"default:stone_with_copper": ("cube", 91, 88, 87),
	"default:grass_1": ("cube", 72, 109, 32),
	"default:papyrus": ("cube", 98, 173, 32),
	"default:ice": ("cube", 155, 155, 254),
	"default:wood": ("cube", 128, 100, 57),
	"default:stone_with_mese": ("cube", 91, 88, 87),
	"default:diamondblock": ("cube", 103, 195, 201),
	"default:coalblock": ("cube", 58, 58, 58),
	"default:stone_with_gold": ("cube", 91, 88, 87),
	"default:apple": ("cube", 50, 0, 0),
	"default:grass_4": ("cube", 73, 112, 33),
	"default:dirt_with_grass_footsteps": ("cube", 101, 138, 35),
	"default:desert_stonebrick": ("cube", 105, 64, 49),
	"default:cloud": ("cube", 255, 255, 255),
	"default:stone_with_iron": ("cube", 91, 88, 87),
	"default:bronzeblock": ("cube", 116, 70, 26),
	"default:dirt_with_snow": ("cube", 225, 227, 255),
	"default:fence_wood": ("cube", 128, 100, 57),
	"default:desert_sand": ("cube", 209, 165, 97),
	"default:steelblock": ("cube", 153, 153, 153),
	"default:rail": ("cube", 114, 82, 33),
	"default:nyancat_rainbow": ("cube", 58, 19, 128),
	"default:lava_flowing": ("cube", 255, 100, 0),
	"default:sapling": ("cube", 63, 59, 40),
	"default:snow": ("cube", 225, 227, 255),
	"default:furnace": ("cube", 97, 93, 91),
	"default:desert_stone": ("cube", 122, 74, 57),
	"default:tree": ("cube", 66, 52, 35),
	"default:jungletree": ("cube", 120, 106, 78),
	"default:cactus": ("cube", 132, 143, 108),
	"default:water_source": ("cube", 39, 66, 106, 128),
	"default:mese": ("cube", 200, 202, 0),
	"default:stone_with_coal": ("cube", 91, 88, 87),
	"default:nyancat": ("cube", 38, 16, 66),
	"default:snowblock": ("cube", 225, 227, 255),
	"default:stonebrick": ("cube", 104, 100, 99),
	"default:jungleleaves": ("cube", 18, 25, 14),
	"default:sandstone": ("cube", 180, 162, 121),
	"default:dirt_with_grass": ("cube", 72, 107, 44),
	"default:brick": ("cube", 156, 157, 151),
	"default:junglegrass": ("cube", 82, 133, 35),
	"default:cobble": ("cube", 133, 133, 133),
	"default:grass_3": ("cube", 71, 109, 32),
	"default:stone": ("cube", 91, 88, 87),
	"default:sand": ("cube", 219, 209, 167),
	"default:obsidian": ("cube", 16, 16, 16),
	"default:bookshelf": ("cube", 128, 100, 57),
	"default:leaves": ("cube", 30, 47, 28),
	"default:grass_5": ("cube", 73, 112, 33),
	"default:ladder": ("cube", 153, 109, 39),
	"default:dirt": ("cube", 122, 83, 58),
	"default:mossycobble": ("cube", 102, 116, 85),
	"default:stone_with_diamond": ("cube", 91, 88, 87),
	"default:grass_2": ("cube", 71, 109, 32),
	"default:chest": ("cube", 238, 219, 171),
	"default:gravel": ("cube", 92, 84, 76),
	"default:torch": ("cube", 213, 154, 84),
	"default:clay": ("cube", 178, 178, 178),
	"default:chest_locked": ("cube", 238, 219, 171),
	"default:copperblock": ("cube", 110, 86, 60),
	"default:dry_shrub": ("cube", 117, 75, 14),
	"default:junglewood": ("cube", 51, 35, 12),
	"signs:sign_yard": ("cube", 163, 141, 106),
	"signs:sign_post": ("cube", 4, 2, 0),
	"junglegrass:shortest": ("cube", 55, 92, 21),
	"junglegrass:short": ("cube", 49, 89, 15),
	"junglegrass:medium": ("cube", 83, 135, 36),
	"doors:door_wood_t_2": ("cube", 87, 64, 30),
	"doors:door_wood_b_1": ("cube", 87, 64, 30),
	"doors:door_wood_t_1": ("cube", 87, 64, 30),
	"doors:door_steel_t_1": ("cube", 162, 162, 162),
	"doors:door_steel_t_2": ("cube", 162, 162, 162),
	"doors:door_steel_b_1": ("cube", 162, 162, 162),
	"doors:door_wood_b_2": ("cube", 87, 64, 30),
	"doors:door_steel_b_2": ("cube", 162, 162, 162),
	"poisonivy:climbing": ("cube", 91, 143, 24),
	"poisonivy:sproutling": ("cube", 111, 166, 30),
	"poisonivy:seedling": ("cube", 127, 190, 34),
	"wool:magenta": ("cube", 210, 3, 121),
	"wool:blue": ("cube", 0, 78, 152),
	"wool:cyan": ("cube", 0, 142, 150),
	"wool:orange": ("cube", 220, 91, 24),
	"wool:grey": ("cube", 141, 141, 141),
	"wool:dark_grey": ("cube", 65, 65, 65),
	"wool:pink": ("cube", 255, 144, 144),
	"wool:white": ("cube", 228, 228, 228),
	"wool:violet": ("cube", 96, 2, 177),
	"wool:black": ("cube", 33, 33, 33),
	"wool:green": ("cube", 99, 230, 28),
	"wool:brown": ("cube", 95, 49, 0),
	"wool:yellow": ("cube", 253, 237, 16),
	"wool:dark_green": ("cube", 36, 109, 0),
	"wool:red": ("cube", 180, 20, 20),
	"fire:basic_flame": ("cube", 147, 47, 11),
	"vessels:glass_bottle": ("cube", 211, 212, 211),
	"vessels:steel_bottle": ("cube", 109, 109, 109),
	"vessels:drinking_glass": ("cube", 220, 220, 220),
	"flowers:rose": ("cube", 159, 9, 0),
	"flowers:potted_tulip": ("cube", 114, 41, 22),
	"flowers:viola": ("cube", 108, 83, 106),
	"flowers:tulip": ("cube", 91, 146, 5),
	"flowers:geranium": ("cube", 54, 72, 184),
	"flowers:potted_dandelion_yellow": ("cube", 116, 43, 22),
	"flowers:waterlily": ("cube", 46, 108, 0),
	"flowers:waterlily_225": ("cube", 49, 110, 2),
	"flowers:dandelion_yellow": ("cube", 147, 178, 3),
	"flowers:potted_geranium": ("cube", 76, 60, 124),
	"flowers:dandelion_white": ("cube", 136, 179, 95),
	"flowers:potted_rose": ("cube", 115, 40, 22),
	"flowers:waterlily_675": ("cube", 165, 194, 103),
	"flowers:waterlily_45": ("cube", 150, 179, 101),
	"flowers:potted_dandelion_white": ("cube", 116, 43, 25),
	"flowers:seaweed": ("cube", 28, 112, 11),
	"flowers:potted_viola": ("cube", 115, 41, 24),
	"farming:wheat_6": ("cube", 165, 151, 74),
	"farming:cotton_4": ("cube", 58, 46, 27),
	"farming:cotton_7": ("cube", 194, 189, 185),
	"farming:soil_wet": ("cube", 73, 40, 19),
	"farming:cotton_3": ("cube", 57, 48, 27),
	"farming:wheat_1": ("cube", 130, 186, 84),
	"farming:wheat_7": ("cube", 178, 159, 81),
	"farming:cotton_5": ("cube", 65, 49, 31),
	"farming:soil": ("cube", 110, 75, 53),
	"farming:wheat_8": ("cube", 177, 160, 81),
	"farming:wheat_2": ("cube", 142, 190, 86),
	"farming:wheat_4": ("cube", 168, 186, 83),
	"farming:wheat_5": ("cube", 177, 166, 79),
	"farming:wheat_3": ("cube", 148, 185, 83),
	"farming:cotton_1": ("cube", 66, 61, 31),
	"farming:cotton_2": ("cube", 59, 51, 28),
	"farming:cotton_6": ("cube", 75, 60, 44),
	"farming:cotton_8": ("cube", 228, 226, 225),
}

optargs, args = getopt.getopt(sys.argv[1:], '')

if len(args) < 1:
	print("Usage: %s <.mts schematic>" % sys.argv[0])
	print("Converts .mts schematics to Wavefront .obj geometry files")
	print("")
	print("Output files are written into directory where the source file lays.")
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
	# TODO use zlib.compressobj
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
				if not nname in colors.keys():
					if not nname in unknownnodes:
						unknownnodes.append(nname)
					continue
				else:
					if not nname in foundnodes:
						foundnodes.append(nname)
				obj.write("o node%d\n" % i)
				obj.write("usemtl %s\n" % nname.replace(":", "__"))
				objd = open("models/" + colors[nname][0] + ".obj", 'r')
				for line in objd:
					if line.strip() == "":
						pass
					elif line.startswith("#"):
						pass # comment
					elif line.startswith("v "):
						tmp = line.split(" ")
						vx, vy, vz = float(tmp[1]), float(tmp[2]), float(tmp[3])
						vx += x
						vy += y
						vz += z
						obj.write("v %f %f %f\n" % (vx, vy, vz))
					else:
						obj.write(line)
				objd.close()
				obj.write("\n")
				i += 1
	obj.close()
	mtl = open(filepart + ".mtl", "w")
	mtl.write("# Generated by mt2obj\n\n\n")
	for node in foundnodes:
		mtl.write("newmtl %s\n" % node.replace(":", "__"))
		c = colors[node]
		mtld = open("models/" + colors[node][0] + ".mtl", 'r')
		for line in mtld:
			if line.strip() == "":
				pass
			elif line.startswith("#"):
				pass # comment
			else:
				if len(c) > 4: # if there is transparency
					tmp1 = c[4]/255
				else:
					tmp1 = 1.0
				tmp2 = line.replace("{r}", str(c[1]/255)).replace("{g}", str(c[2]/255)).replace("{b}", str(c[3]/255)).replace("{a}", str(tmp1))
				mtl.write(tmp2)
		mtl.write("\n")
		mtld.close()
	mtl.close()
	if len(unknownnodes) > 0:
		print("There were some unknown nodes that were ignored during the conversion:")
		for e in unknownnodes:
			print(e)


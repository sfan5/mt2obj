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

# sed -re 's/(.+?) (.+?) (.+?) (.+?)/\t"\1": (\2, \3, \4),/' < colors.txt
colors = {
	"nether:brick": (40, 18, 18),
	"nether:portal": (0, 0, 0),
	"nether:sand": (40, 21, 21),
	"nether:glowstone": (221, 197, 141),
	"nether:rack": (40, 16, 16),
	"beds:bed_top_red": (131, 22, 22),
	"beds:bed_bottom_blue": (10, 11, 122),
	"beds:bed_bottom_grey": (147, 147, 147),
	"beds:bed_bottom_white": (215, 215, 215),
	"beds:bed_bottom_green": (12, 92, 10),
	"beds:bed_bottom_orange": (217, 123, 10),
	"beds:bed_top_blue": (11, 12, 122),
	"beds:bed_bottom_violet": (129, 10, 180),
	"beds:bed_top_green": (13, 92, 11),
	"beds:bed_bottom_black": (10, 10, 10),
	"beds:bed_bottom_yellow": (215, 214, 0),
	"beds:bed_bottom_red": (131, 21, 21),
	"beds:bed_top_white": (215, 215, 215),
	"beds:bed_top_yellow": (215, 214, 0),
	"beds:bed_top_violet": (129, 11, 180),
	"beds:bed_top_grey": (147, 147, 147),
	"beds:bed_top_black": (11, 11, 11),
	"beds:bed_top_orange": (216, 123, 11),
	"nuke:hardcore_mese_tnt": (173, 173, 0),
	"nuke:iron_tnt": (158, 158, 157),
	"nuke:hardcore_iron_tnt": (158, 158, 157),
	"nuke:mese_tnt": (173, 173, 0),
	"christmas:present_green_violet": (189, 36, 157),
	"christmas:present_blue_green": (62, 186, 50),
	"christmas:present_orange_green": (62, 186, 50),
	"christmas:tree": (45, 36, 24),
	"christmas:present_orange_violet": (189, 36, 157),
	"christmas:present_blue_orange": (245, 207, 20),
	"christmas:present_blue_violet": (189, 36, 157),
	"christmas:star": (236, 252, 55),
	"christmas:present_green_orange": (245, 207, 20),
	"christmas:leaves": (33, 54, 30),
	"snow:moss": (51, 64, 29),
	"snow:snow5": (225, 227, 255),
	"snow:snow3": (225, 227, 255),
	"snow:needles_decorated": (7, 50, 19),
	"snow:needles": (6, 49, 18),
	"snow:snow8": (225, 227, 255),
	"snow:star": (214, 142, 0),
	"snow:snow": (225, 227, 255),
	"snow:xmas_tree": (87, 88, 28),
	"snow:sapling_pine": (3, 54, 20),
	"snow:snow6": (225, 227, 255),
	"snow:snow_block": (225, 227, 255),
	"snow:snow7": (225, 227, 255),
	"snow:snow_brick": (223, 225, 253),
	"snow:dirt_with_snow": (225, 227, 255),
	"snow:snow4": (225, 227, 255),
	"snow:snow2": (225, 227, 255),
	"snow:ice": (155, 155, 254),
	"stairs:stair_wood_tile_full": (78, 64, 44),
	"stairs:stair_mossycobble": (102, 116, 85),
	"stairs:slab_jungle_wood": (51, 35, 12),
	"stairs:slab_wood_tile_center": (128, 100, 57),
	"stairs:stair_wood_tile": (78, 65, 44),
	"stairs:stair_cobble": (133, 133, 133),
	"stairs:slab_invisible": (0, 0, 0),
	"stairs:stair_stonebrick": (104, 100, 99),
	"stairs:slab_iron_glass": (222, 222, 222),
	"stairs:stair_wood": (128, 100, 57),
	"stairs:stair_stone": (91, 88, 87),
	"stairs:stair_obsidian": (16, 16, 16),
	"stairs:stair_copperblock": (110, 86, 60),
	"stairs:stair_super_glow_glass": (255, 255, 120),
	"stairs:slab_iron_stone": (134, 134, 134),
	"stairs:stair_stone_tile": (97, 97, 97),
	"stairs:stair_desert_stone": (122, 74, 57),
	"stairs:slab_bronzeblock": (116, 70, 26),
	"stairs:stair_goldblock": (126, 116, 35),
	"stairs:stair_iron_checker": (142, 142, 142),
	"stairs:stair_steelblock": (153, 153, 153),
	"stairs:slab_coal_stone": (70, 70, 70),
	"stairs:slab_obsidian_glass": (16, 17, 17),
	"stairs:stair_sandstone": (180, 162, 121),
	"stairs:stair_iron_stone": (134, 134, 134),
	"stairs:slab_steelblock": (153, 153, 153),
	"stairs:stair_split_stone_tile": (97, 97, 97),
	"stairs:stair_brick": (156, 157, 151),
	"stairs:stair_sandstonebrick": (160, 144, 108),
	"stairs:slab_mossycobble": (102, 116, 85),
	"stairs:stair_glass": (192, 192, 227),
	"stairs:slab_cactus_checker": (130, 138, 130),
	"stairs:slab_jungletree": (120, 106, 78),
	"stairs:stair_coal_stone": (70, 70, 70),
	"stairs:slab_junglewood": (51, 35, 12),
	"stairs:stair_jungletree": (120, 106, 78),
	"stairs:slab_wood": (128, 100, 57),
	"stairs:stair_iron_stone_bricks": (104, 98, 97),
	"stairs:stair_coal_checker": (133, 133, 133),
	"stairs:stair_plankstone": (66, 51, 23),
	"stairs:stair_obsidian_glass": (16, 17, 17),
	"stairs:slab_desert_stone": (122, 74, 57),
	"stairs:slab_iron_stone_bricks": (104, 98, 97),
	"stairs:slab_glass": (192, 192, 227),
	"stairs:stair_bronzeblock": (116, 70, 26),
	"stairs:slab_desert_stonebrick": (105, 64, 49),
	"stairs:slab_tree": (66, 52, 35),
	"stairs:slab_stone": (91, 88, 87),
	"stairs:stair_cactus_checker": (130, 138, 130),
	"stairs:slab_diamondblock": (103, 195, 201),
	"stairs:slab_super_glow_glass": (255, 255, 120),
	"stairs:slab_cobble": (133, 133, 133),
	"stairs:stair_tree": (66, 52, 35),
	"stairs:slab_wood_tile": (78, 65, 44),
	"stairs:slab_glow_glass": (255, 226, 114),
	"stairs:slab_wood_tile_full": (78, 64, 44),
	"stairs:stair_coal_stone_bricks": (79, 76, 75),
	"stairs:slab_coal_glass": (130, 130, 130),
	"stairs:stair_coal_glass": (130, 130, 130),
	"stairs:slab_brick": (156, 157, 151),
	"stairs:slab_stone_tile": (97, 97, 97),
	"stairs:slab_goldblock": (126, 116, 35),
	"stairs:slab_plankstone": (66, 51, 23),
	"stairs:slab_coal_stone_bricks": (79, 76, 75),
	"stairs:stair_jungle_wood": (51, 35, 12),
	"stairs:stair_circle_stone_bricks": (91, 88, 87),
	"stairs:slab_iron_checker": (142, 142, 142),
	"stairs:stair_wood_tile_center": (128, 100, 57),
	"stairs:slab_stonebrick": (104, 100, 99),
	"stairs:slab_sandstonebrick": (160, 144, 108),
	"stairs:stair_invisible": (0, 0, 0),
	"stairs:stair_iron_glass": (222, 222, 222),
	"stairs:stair_desert_stonebrick": (105, 64, 49),
	"stairs:stair_diamondblock": (103, 195, 201),
	"stairs:slab_sandstone": (180, 162, 121),
	"stairs:slab_copperblock": (110, 86, 60),
	"stairs:stair_glow_glass": (255, 226, 114),
	"stairs:stair_junglewood": (51, 35, 12),
	"stairs:slab_circle_stone_bricks": (91, 88, 87),
	"stairs:slab_obsidian": (16, 16, 16),
	"stairs:slab_coal_checker": (133, 133, 133),
	"stairs:slab_split_stone_tile": (97, 97, 97),
	"mg:savannawood": (128, 113, 57),
	"mg:pineleaves": (16, 30, 14),
	"mg:savannasapling": (32, 36, 13),
	"mg:pinewood": (120, 93, 66),
	"mg:pinetree": (26, 21, 14),
	"mg:savannaleaves": (70, 62, 41),
	"mg:pinesapling": (12, 12, 5),
	"mg:savannatree": (52, 51, 37),
	"mg:dirt_with_dry_grass": (114, 99, 53),
	"bones:bones": (74, 74, 74),
	"default:glass": (192, 192, 227, 64),
	"default:water_flowing": (39, 66, 106, 128),
	"default:junglesapling": (37, 34, 14),
	"default:sandstonebrick": (160, 144, 108),
	"default:furnace_active": (97, 93, 91),
	"default:sign_wall": (163, 141, 106),
	"default:lava_source": (255, 100, 0),
	"default:goldblock": (126, 116, 35),
	"default:obsidian_glass 16 17": (17, 64, 16),
	"default:stone_with_copper": (91, 88, 87),
	"default:grass_1": (72, 109, 32),
	"default:papyrus": (98, 173, 32),
	"default:ice": (155, 155, 254),
	"default:wood": (128, 100, 57),
	"default:stone_with_mese": (91, 88, 87),
	"default:diamondblock": (103, 195, 201),
	"default:coalblock": (58, 58, 58),
	"default:stone_with_gold": (91, 88, 87),
	"default:apple": (50, 0, 0),
	"default:grass_4": (73, 112, 33),
	"default:dirt_with_grass_footsteps": (101, 138, 35),
	"default:desert_stonebrick": (105, 64, 49),
	"default:cloud": (255, 255, 255),
	"default:stone_with_iron": (91, 88, 87),
	"default:bronzeblock": (116, 70, 26),
	"default:dirt_with_snow": (225, 227, 255),
	"default:fence_wood": (128, 100, 57),
	"default:desert_sand": (209, 165, 97),
	"default:steelblock": (153, 153, 153),
	"default:rail": (114, 82, 33),
	"default:nyancat_rainbow": (58, 19, 128),
	"default:lava_flowing": (255, 100, 0),
	"default:sapling": (63, 59, 40),
	"default:snow": (225, 227, 255),
	"default:furnace": (97, 93, 91),
	"default:desert_stone": (122, 74, 57),
	"default:tree": (66, 52, 35),
	"default:jungletree": (120, 106, 78),
	"default:cactus": (132, 143, 108),
	"default:water_source": (39, 66, 106, 128),
	"default:mese": (200, 202, 0),
	"default:stone_with_coal": (91, 88, 87),
	"default:nyancat": (38, 16, 66),
	"default:snowblock": (225, 227, 255),
	"default:stonebrick": (104, 100, 99),
	"default:jungleleaves": (18, 25, 14),
	"default:sandstone": (180, 162, 121),
	"default:dirt_with_grass": (72, 107, 44),
	"default:brick": (156, 157, 151),
	"default:junglegrass": (82, 133, 35),
	"default:cobble": (133, 133, 133),
	"default:grass_3": (71, 109, 32),
	"default:stone": (91, 88, 87),
	"default:sand": (219, 209, 167),
	"default:obsidian": (16, 16, 16),
	"default:bookshelf": (128, 100, 57),
	"default:leaves": (30, 47, 28),
	"default:grass_5": (73, 112, 33),
	"default:ladder": (153, 109, 39),
	"default:dirt": (122, 83, 58),
	"default:mossycobble": (102, 116, 85),
	"default:stone_with_diamond": (91, 88, 87),
	"default:grass_2": (71, 109, 32),
	"default:chest": (238, 219, 171),
	"default:gravel": (92, 84, 76),
	"default:torch": (213, 154, 84),
	"default:clay": (178, 178, 178),
	"default:chest_locked": (238, 219, 171),
	"default:copperblock": (110, 86, 60),
	"default:dry_shrub": (117, 75, 14),
	"default:junglewood": (51, 35, 12),
	"signs:sign_yard": (163, 141, 106),
	"signs:sign_post": (4, 2, 0),
	"junglegrass:shortest": (55, 92, 21),
	"junglegrass:short": (49, 89, 15),
	"junglegrass:medium": (83, 135, 36),
	"doors:door_wood_t_2": (87, 64, 30),
	"doors:door_wood_b_1": (87, 64, 30),
	"doors:door_wood_t_1": (87, 64, 30),
	"doors:door_steel_t_1": (162, 162, 162),
	"doors:door_steel_t_2": (162, 162, 162),
	"doors:door_steel_b_1": (162, 162, 162),
	"doors:door_wood_b_2": (87, 64, 30),
	"doors:door_steel_b_2": (162, 162, 162),
	"poisonivy:climbing": (91, 143, 24),
	"poisonivy:sproutling": (111, 166, 30),
	"poisonivy:seedling": (127, 190, 34),
	"wool:magenta": (210, 3, 121),
	"wool:blue": (0, 78, 152),
	"wool:cyan": (0, 142, 150),
	"wool:orange": (220, 91, 24),
	"wool:grey": (141, 141, 141),
	"wool:dark_grey": (65, 65, 65),
	"wool:pink": (255, 144, 144),
	"wool:white": (228, 228, 228),
	"wool:violet": (96, 2, 177),
	"wool:black": (33, 33, 33),
	"wool:green": (99, 230, 28),
	"wool:brown": (95, 49, 0),
	"wool:yellow": (253, 237, 16),
	"wool:dark_green": (36, 109, 0),
	"wool:red": (180, 20, 20),
	"fire:basic_flame": (147, 47, 11),
	"vessels:glass_bottle": (211, 212, 211),
	"vessels:steel_bottle": (109, 109, 109),
	"vessels:drinking_glass": (220, 220, 220),
	"flowers:rose": (159, 9, 0),
	"flowers:potted_tulip": (114, 41, 22),
	"flowers:viola": (108, 83, 106),
	"flowers:tulip": (91, 146, 5),
	"flowers:geranium": (54, 72, 184),
	"flowers:potted_dandelion_yellow": (116, 43, 22),
	"flowers:waterlily": (46, 108, 0),
	"flowers:waterlily_225": (49, 110, 2),
	"flowers:dandelion_yellow": (147, 178, 3),
	"flowers:potted_geranium": (76, 60, 124),
	"flowers:dandelion_white": (136, 179, 95),
	"flowers:potted_rose": (115, 40, 22),
	"flowers:waterlily_675": (165, 194, 103),
	"flowers:waterlily_45": (150, 179, 101),
	"flowers:potted_dandelion_white": (116, 43, 25),
	"flowers:seaweed": (28, 112, 11),
	"flowers:potted_viola": (115, 41, 24),
	"farming:wheat_6": (165, 151, 74),
	"farming:cotton_4": (58, 46, 27),
	"farming:cotton_7": (194, 189, 185),
	"farming:soil_wet": (73, 40, 19),
	"farming:cotton_3": (57, 48, 27),
	"farming:wheat_1": (130, 186, 84),
	"farming:wheat_7": (178, 159, 81),
	"farming:cotton_5": (65, 49, 31),
	"farming:soil": (110, 75, 53),
	"farming:wheat_8": (177, 160, 81),
	"farming:wheat_2": (142, 190, 86),
	"farming:wheat_4": (168, 186, 83),
	"farming:wheat_5": (177, 166, 79),
	"farming:wheat_3": (148, 185, 83),
	"farming:cotton_1": (66, 61, 31),
	"farming:cotton_2": (59, 51, 28),
	"farming:cotton_6": (75, 60, 44),
	"farming:cotton_8": (228, 226, 225),
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
				obj.write("v %f %f %f\n" % (x+1, y, z))
				obj.write("v %f %f %f\n" % (x+1, y, z+1))
				obj.write("v %f %f %f\n" % (x, y, z+1))
				obj.write("v %f %f %f\n" % (x, y, z))
				obj.write("v %f %f %f\n" % (x+1, y+1, z))
				obj.write("v %f %f %f\n" % (x+1, y+1, z+1))
				obj.write("v %f %f %f\n" % (x, y+1, z+1))
				obj.write("v %f %f %f" % (x, y+1, z))
				obj.write("""
f -8 -7 -6 -5
f -4 -1 -2 -3
f -8 -4 -3 -7
f -7 -3 -2 -6
f -6 -2 -1 -5
f -4 -8 -5 -1
f -8 -7 -6
f -4 -3 -2 -1""")
				obj.write("\n\n")
				i += 1
	obj.close()
	mtl = open(filepart + ".mtl", "w")
	mtl.write("# Generated by mt2obj\n\n\n")
	for node in foundnodes:
		mtl.write("newmtl %s\n" % node.replace(":", "__"))
		c = colors[node]
		mtl.write("Kd %f %f %f\n" % (c[0]/255, c[1]/255, c[2]/255))
		if len(c) > 3: # if there is transparency
			mtl.write("d %f\n" % (c[3]/255,))
		else:
			mtl.write("d 1.0\n")
		mtl.write("Ka 1.0 1.0 1.0\nKs 0.0 0.0 0.0\nillum 1\n")
		mtl.write("\n")
	mtl.close()
	if len(unknownnodes) > 0:
		print("There were some unknown nodes that were ignored during the conversion:")
		for e in unknownnodes:
			print(e)


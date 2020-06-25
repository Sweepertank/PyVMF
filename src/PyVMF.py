from __future__ import annotations
import re
from copy import deepcopy
import sys
import time
import math
import operator
from random import randint
from .tools import num
from .importer import *
from typing import List, Tuple, Generator
import warnings
from .exceptions import *

class Convert:
	"""
	Converts strings to usable instances
	"""
	@staticmethod
	def string_to_vertex(string: str) -> Vertex:
		reg = re.sub(r'[(){}<>\[\],]', '', string).split()
		return Vertex(num(reg[0]), num(reg[1]), num(reg[2]))

	@staticmethod
	def string_to_3x_vertex(string: str) -> List[Vertex, Vertex, Vertex]:
		reg = re.sub(r'[(){}<>]', '', string).split()
		clean = []
		for i in reg:
			clean.append(num(i))

		return [Vertex(clean[0], clean[1], clean[2]),
				Vertex(clean[3], clean[4], clean[5]),
				Vertex(clean[6], clean[7], clean[8])]

	@staticmethod
	def string_to_color(string: str) -> Color:
		temp = string.split()
		return Color(int(temp[0]), int(temp[1]), int(temp[2]))

	@staticmethod
	def string_to_color_light(string: str) -> ColorLight:
		temp = string.split()
		return ColorLight(int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]))

	@staticmethod
	def string_to_uvaxis(string: str) -> UVaxis:
		reg = re.sub(r'[\[\]]', '', string).split()
		return UVaxis(*reg)


class Common:
	"""
	The parent class to all VMF classes that need to be exported to the .VMF file.
	"""

	ID = 0

	def export(self,mode="CSGO"):
		"""
		Gets all the variables than need to be exported into the .VMF file

		:return: All predefined (in `export_list`) variable names and their associated values
		:rtype: :obj:`dict`, :obj:`dict`
		"""
		d = {}
		for item in self.export_list:
			t = getattr(self, item)
			d[item] = t
		return d, self.other

	def export_children(self):
		"""
		Gets all the children classes

		:return: All predefined children classes
		:rtype: :obj:`list` of :class:`Common` instances
		"""
		return []

	def copy(self):
		"""
		Copies the class using :func:`~copy.deepcopy`

		:return: A deepcopy of itself
		:rtype: :class:`Common` instance
		"""
		c = deepcopy(self)
		c.id = self.ids()
		return c

	def ids(self):
		Common.ID += 1
		return Common.ID

	def _dic_and_children(self, dic, children):
		if dic is None:
			dic = {}
		if children is None:
			children = []
		return dic, children

	def _dic(self, dic):
		if dic is None:
			dic = {}
		return dic


class Color:
	"""
	Simple RGB color class

	:param r: Value for RED between 0 and 255
	:type r: :obj:`int`
	:param g: Value for GREEN between 0 and 255
	:type g: :obj:`int`
	:param b: Value for BLUE between 0 and 255
	:type b: :obj:`int`
	"""

	def __init__(self, r: int = 255, g: int = 255, b: int = 255):
		self.r = 0
		self.g = 0
		self.b = 0
		self.set(r, g, b)

	def __str__(self):
		return f"{self.r} {self.g} {self.b}"

	def set(self, r: int = -1, g: int = -1, b: int = -1):
		"""
		Sets the color

		:param r: Value for RED between 0 and 255, if equals to -1 keeps previous value
		:type r: :obj:`int`
		:param g: Value for GREEN between 0 and 255, if equals to -1 keeps previous value
		:type g: :obj:`int`
		:param b: Value for BLUE between 0 and 255, if equals to -1 keeps previous value
		:type b: :obj:`int`
		"""
		if r != -1 and 0 <= r < 256:
			self.r = r
		if g != -1 and 0 <= g < 256:
			self.g = g
		if b != -1 and 0 <= b < 256:
			self.b = b

	def random(self):
		"""
		Sets a random color
		"""
		self.set(randint(0, 255), randint(0, 255), randint(0, 255))

	def export(self,export_mode="CSGO") -> Tuple[int, int, int]:
		return self.r, self.g, self.b

class ColorLight(Color):
	"""
	Simple RGB color class with brightness (used for lights)

	:param r: Value for RED between 0 and 255
	:type r: :obj:`int`
	:param g: Value for GREEN between 0 and 255
	:type g: :obj:`int`
	:param b: Value for BLUE between 0 and 255
	:type b: :obj:`int`
	:param brightness: Value for brightness, above 0
	:type brightness: :obj:`int`
	"""
	def __init__(self, r: int = 255, g: int = 255, b: int = 255, brightness: int = 200):
		super(ColorLight, self).__init__(r, g, b)
		self.brightness = brightness

	def __str__(self):
		return f"{self.r} {self.g} {self.b} {self.brightness}"

	def set_brightness(self, brightness: int):
		"""
		:param brightness: New brightness value
		:type brightness: :obj:`int`
		"""
		self.brightness = brightness

	def export(self,export_mode="CSGO") -> Tuple[int, int, int, int]:
		return self.r, self.g, self.b, self.brightness


class VersionInfo(Common):
	NAME = "versioninfo"

	def __init__(self, dic: dict = None):
		dic = self._dic(dic)

		self.editorversion = dic.pop("editorversion", 400)
		self.editorbuild = dic.pop("editorbuild", 8075)
		self.mapversion = dic.pop("mapversion", 7)
		self.formatversion = dic.pop("formatversion", 100)
		self.prefab = dic.pop("prefab", 0)

		self.other = dic
		self.export_list = ["editorversion", "editorbuild", "mapversion", "formatversion", "prefab"]


class VisGroups(Common):
	NAME = "visgroups"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.other = dic
		self.export_list = []

		self.visgroup = []
		for child in children:
			self.visgroup.append(VisGroup(child.dic, child.children))

	def new_visgroup(self, name: str) -> VisGroup:
		v = VisGroup({"name": name})
		self.visgroup.append(v)
		return v

	def get_visgroups(self) -> List[VisGroup]:
		return self.visgroup

	def export_children(self) -> Tuple[VisGroup, ...]:
		return (*self.visgroup,)


class VisGroup(Common):
	NAME = "visgroup"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.name = dic.pop("name", "default")
		self.visgroupid = dic.pop("visgroupid", self.ids())[0] #visgroupid is mapped to a list in the dic. visgroupid and groupid are the only attributes in any dic where this is the case
		self.color = dic.pop("color", "0 0 0")

		self.other = dic
		self.export_list = ["name", "visgroupid", "color"]

		self.visgroup = []
		for child in children:
			if str(child) == VisGroup.NAME:
				self.visgroup.append(VisGroup(child.dic, child.children))

	def export_children(self):
		return (*self.visgroup,)

class ViewSettings(Common):
	NAME = "viewsettings"

	def __init__(self, dic: dict = None):
		dic = self._dic(dic)

		self.bSnapToGrid = dic.pop("bSnapToGrid", 1)
		self.bShowGrid = dic.pop("bShowGrid", 1)
		self.bShowLogicalGrid = dic.pop("bShowLogicalGrid", 0)
		self.nGridSpacing = dic.pop("nGridSpacing", 64)
		self.bShow3DGrid = dic.pop("bShow3DGrid", 0)

		self.other = dic
		self.export_list = ["bSnapToGrid", "bShowGrid", "bShowLogicalGrid", "nGridSpacing", "bShow3DGrid"]


class World(Common):
	NAME = "world"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.id = dic.pop("id", self.ids())
		self.mapversion = dic.pop("mapversion", 1)
		self.classname = dic.pop("classname", "worldspawn")
		self.detailmaterial = dic.pop("detailmaterial", "detail/detailsprites")
		self.detailvbsp = dic.pop("detailvbsp", "detail.vsbp")
		self.maxpropscreenwidth = dic.pop("maxpropscreenwidth", -1)
		self.skyname = dic.pop("skyname", "sky_dust")

		self.other = dic
		self.export_list = ["id", "mapversion", "classname", "detailmaterial", "detailvbsp", "maxpropscreenwidth",
							"skyname"]

		self.solids = []
		self.hidden = []
		self.group = []
		for child in children:
			if str(child) == Solid.NAME:
				self.solids.append(Solid(child.dic, child.children))

			elif str(child) == Hidden.NAME:
				self.hidden.append(Hidden(child.dic, child.children))

			elif str(child) == Group.NAME:
				self.group.append(Group(child.dic, child.children))

	def export_children(self):
		return (*self.solids, *self.hidden, *self.group)


class Vertex(Common):  # Vertex has to be above the Solid class (see: set_pos_vertex function)
	"""
	Corresponds to a single position on the Hammer grid

	:param x: x position
	:type x: :obj:`int` or :obj:`float`
	:param y: y position
	:type y: :obj:`int` or :obj:`float`
	:param z: z position
	:type z: :obj:`int` or :obj:`float`
	"""

	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z

		self.sorting = 0  # Used in solid get_3d_extremity
		self.normal = 0  # Vertices are represented differently in the VMF depending on the class

	def getX(self):
		return self.x

	def getY(self):
		return self.y
	
	def getZ(self):
		return self.z

	def __str__(self):
		if not self.normal:
			return f"{self.x} {self.y} {self.z}"
		elif self.normal == 1:
			return f"[{self.x} {self.y} {self.z}]"
		elif self.normal == 2:
			return f"({self.x} {self.y} {self.z})"

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y and self.z == other.z

	def __add__(self, other):
		return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vertex(self.x - other.x, self.y - other.y, self.z - other.z)

	def similar(self, other, accuracy=0.001) -> bool:
		"""
		Compares the current vertex with the given one to see if they are similar

		:param other:
		:type other: :class:`Vertex`
		:param accuracy: Distance from the current vertex to be considered similar (in Hammer units)
		:type accuracy: :obj:`float`
		:return: If the given vertex is within the proximity of the current vertex
		:rtype: :obj:`bool`
		"""
		return ((abs(self.x - other.x) < accuracy) and
				(abs(self.y - other.y) < accuracy) and
				(abs(self.z - other.z) < accuracy))

	def multiply(self, amount):
		"""
		Multiplies all the axes uniformly by the given amount

		:param amount: How much to multiply each axis by
		:type amount: :obj:`int` or :obj:`float`
		"""
		self.x *= amount
		self.y *= amount
		self.z *= amount

	def divide(self, amount):
		"""
		Divides all the axes uniformly by the given amount (for separate division see :func:`~Vertex.divide_separate`)

		:param amount: How much to divide each axis by
		:type amount: :obj:`int` or :obj:`float`
		"""
		self.x /= amount
		self.y /= amount
		self.z /= amount

	def divide_separate(self, x, y, z):
		"""
		Divides all the axes separatedly by the given amounts (for uniform division see :func:`~Vertex.divide`)

		:param x: Amount to divide x axis by
		:type x: :obj:`int` or :obj:`float`
		:param y: Amount to divide y axis by
		:type y: :obj:`int` or :obj:`float`
		:param z: Amount to divide z axis by
		:type z: :obj:`int` or :obj:`float`
		"""
		self.x /= x
		self.y /= y
		self.z /= z

	def diff(self, other) -> Vertex:
		"""
		:param other: The vertex to differentiate with
		:return: The difference in distance between 2 vertices
		:rtype: :class:`Vertex`
		"""
		return self - other

	def move(self, x, y, z):
		"""
		Moves the vertex by the given amount

		:param x: Amount to move the x axis by
		:type x: :obj:`int` or :obj:`float`
		:param y: Amount to move the y axis by
		:type y: :obj:`int` or :obj:`float`
		:param z: Amount to move the z axis by
		:type z: :obj:`int` or :obj:`float`
		"""
		self.x += x
		self.y += y
		self.z += z

	def set(self, x, y, z):
		"""
		Sets the vertex position to the given position

		:param x: New x position
		:type x: :obj:`int` or :obj:`float`
		:param y: New y position
		:type y: :obj:`int` or :obj:`float`
		:param z: New z position
		:type z: :obj:`int` or :obj:`float`
		"""
		self.x = x
		self.y = y
		self.z = z

	def rotate_z(self, center: Vertex, angle):
		"""
		Rotates the vertex around the z axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		a = math.radians(angle)
		new_x = center.x + (self.x - center.x) * math.cos(a) - (self.y - center.y) * math.sin(a)
		new_y = center.y + (self.x - center.x) * math.sin(a) + (self.y - center.y) * math.cos(a)
		self.set(new_x, new_y, self.z)

	def rotate_y(self, center: Vertex, angle):
		"""
		Rotates the vertex around the y axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		a = math.radians(angle)
		new_x = center.x + (self.x - center.x) * math.cos(a) - (self.z - center.z) * math.sin(a)
		new_z = center.z + (self.x - center.x) * math.sin(a) + (self.z - center.z) * math.cos(a)
		self.set(new_x, self.y, new_z)

	def rotate_x(self, center: Vertex, angle):
		"""
		Rotates the vertex around the x axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		a = math.radians(angle)
		new_y = center.y + (self.y - center.y) * math.cos(a) - (self.z - center.z) * math.sin(a)
		new_z = center.z + (self.y - center.y) * math.sin(a) + (self.z - center.z) * math.cos(a)
		self.set(self.x, new_y, new_z)

	def flip(self, x=None, y=None, z=None):
		if x is not None:
			self.x += 2 * (x - self.x)
		if y is not None:
			self.y += 2 * (y - self.y)
		if z is not None:
			self.z += 2 * (z - self.z)

	def align_to_grid(self):
		"""
		Turns x, y and z into integers
		"""
		self.x = round(self.x)
		self.y = round(self.y)
		self.z = round(self.z)

	def export(self,export_mode="CSGO") -> Tuple[int, int, int]:
		return (self.x,
				self.y,
				self.z)


class Solid(Common):
	"""
	Corresponds to an individual solid just like in Hammer
	
	:param dic: All the values to be initialized, if empty default values are used.
	:type dic: :obj:`dict` 
	:param children: The :class:`Side`\'s and :class:`Editor` to be initialized
	:type children: :obj:`list` 
	"""

	NAME = "solid"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.id = dic.pop("id", self.ids())

		self.other = dic
		self.export_list = ["id"]

		self.side = []
		self.editor = None
		for child in children:
			if str(child) == Side.NAME:
				self.side.append(Side(child.dic, child.children))

			elif str(child) == Editor.NAME:
				self.editor = Editor(child.dic)

	def add_sides(self, *args: Side):
		"""
		Adds sides to the solid, note that no checks are made for validity

		:param args: List of sides to be added
		:type args: :obj:`list` of :class:`Side`
		"""
		self.side.extend(args)

	def move(self, x, y, z):
		"""
		Moves all sides of the solid by the given amount in Hammer units

		:param x:
		:type x: :obj:`int` or :obj:`float`
		:param y:
		:type y: :obj:`int` or :obj:`float`
		:param z:
		:type z: :obj:`int` or :obj:`float`
		"""
		for side in self.side:
			for vert in side.plane:
				vert.move(x, y, z)

	def get_linked_vertices(self, vertex: Vertex, similar=0.0) -> List[Vertex, ...]:
		"""
		:param vertex: The vertex to check against
		:type vertex: :class:`Vertex`
		:param similar: Distance between vertices to be considered similar (in Hammer units)
		:type similar: :obj:`float`
		:return: All vertices that are in close proximity to the given vertex itself included
		:rtype: :obj:`list` of :class:`Vertex`
		"""
		li = []

		for vert in self.get_all_vertices():
			if similar == 0.0:
				if vertex == vert:
					li.append(vert)

			else:
				if vertex.similar(vert, similar):
					li.append(vert)

		return li

	def rotate_x(self, center: Vertex, angle):
		"""
		Rotates the solid around the x axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for side in self.side:
			side.rotate_x(center, angle)

	def rotate_y(self, center: Vertex, angle):
		"""
		Rotates the solid around the y axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for side in self.side:
			side.rotate_y(center, angle)

	def rotate_z(self, center: Vertex, angle):
		"""
		Rotates the solid around the z axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for side in self.side:
			side.rotate_z(center, angle)

	def flip(self, x=None, y=None, z=None):
		for vert in self.get_all_vertices():
			vert.flip(x, y, z)

	def scale(self, center: Vertex, x=1.0, y=1.0, z=1.0):
		"""
		Scales the solid using ratios.
		For example using the center of the solid and values of 2 makes it twice as big
		NOTE: IF THE SOLID HAS ANY DISPLACEMENT SIDES, this method will only work correctly if you scale by the same multiplier on all 3 axes.

		:param center: The point from which the scaling is based, use the center of the solid for traditional scaling
		:type center: :class:`Vertex`
		:param x: Scale ratio on the x axis
		:type x: :obj:`int` or :obj:`float`
		:param y: Scale ratio on the y axis
		:type y: :obj:`int` or :obj:`float`
		:param z: Scale ratio on the z axis
		:type z: :obj:`int` or :obj:`float`
		"""
		for side in self.get_sides():
			if side.dispinfo is not None:
				for a in range(side.dispinfo.matrix.get_size()):
					for b in range(side.dispinfo.matrix.get_size()):
						side.dispinfo.matrix.get(a,b).scale(x)
				side.dispinfo._startposition.multiply(x)
			side.uaxis.scale = str(float(side.uaxis.scale) * x)
			side.vaxis.scale = str(float(side.vaxis.scale) * x)
		x -= 1
		y -= 1
		z -= 1
		for vertex in self.get_all_vertices():
			diff = vertex.diff(center)
			fixed_diff = (diff.x * x, diff.y * y, diff.z * z)
			vertex.move(*fixed_diff)

	@property
	def center(self) -> Vertex:
		"""
		Finds the center of the solid based on the average of all vertices.
		**Can behave unpredictably** as faces only consists of 3 verticies so the center might be off by a tiny amount
		For a more reliable option see :func:`~Solid.center_geo`

		:return: The average center of the solid
		:rtype: :class:`Vertex`
		"""
		v = Vertex()
		vert_list = self.get_only_unique_vertices()
		for vert in vert_list:
			v = v + vert
		v.divide(len(vert_list))
		return v

	@center.setter
	def center(self, vertex: Vertex):
		"""
		Moves the solid based on it's center to the new position

		:param vertex: The new position assumed by the solid center
		:type vertex: :class:`Vertex`
		"""
		self.move(*vertex.diff(self.center).export())

	@property
	def center_geo(self) -> Vertex:
		"""
		Finds the center of the solid based on the extremities of all 3 axes.
		More reliable than :func:`~Solid.center`

		:return: The geometric center of the solid
		:rtype: :class:`Vertex`
		"""
		v = Vertex()

		x = self.get_axis_extremity(x=False).x
		y = self.get_axis_extremity(y=False).y
		z = self.get_axis_extremity(z=False).z

		size = self.size
		size.divide(2)

		v.set(x, y, z)
		v.move(*size.export())

		return v

	def get_axis_extremity(self, x: bool = None, y: bool = None, z: bool = None) -> Vertex:
		"""
		Finds the vertex that is the furthest on the given axis, **only 1 axis per method call**,
		see :func:`~Solid.get_3d_extremity`

		:param x: False for negative side of the axis, True for positive side
		:type x: :obj:`bool`
		:param y: False for negative side of the axis, True for positive side
		:type y: :obj:`bool`
		:param z: False for negative side of the axis, True for positive side
		:type z: :obj:`bool`
		:return: The vertex the furthest most on the given axis
		:rtype: :class:`Vertex`
		"""
		verts = self.get_only_unique_vertices()

		if x is not None:
			lx = sorted(verts, key=operator.attrgetter("x"))
			return lx[int(not x) - 1]

		elif y is not None:
			ly = sorted(verts, key=operator.attrgetter("y"))
			return ly[int(not y) - 1]

		elif z is not None:
			lz = sorted(verts, key=operator.attrgetter("z"))
			return lz[int(not z) - 1]

		raise ValueError("No axis given")

	def get_3d_extremity(self, x: bool = None, y: bool = None, z: bool = None) -> Tuple[Vertex, List[Vertex, ...]]:
		"""
		Finds the vertices that are the furthest on the given axes, as well as ties

		:param x: False for negative side of the axis, True for positive side
		:type x: :obj:`bool`
		:param y: False for negative side of the axis, True for positive side
		:type y: :obj:`bool`
		:param z: False for negative side of the axis, True for positive side
		:type z: :obj:`bool`
		:return: The vertex furthest most on the given axes, and the ties, **the champion vertex is included**
		:rtype: :class:`Vertex`, :obj:`list` of :class:`Vertex`
		"""
		verts = self.get_only_unique_vertices()

		for vert in verts:
			vert.sorting = 0
			if x is not None:
				if x:
					vert.sorting += vert.x
				else:
					vert.sorting -= vert.x
			if y is not None:
				if y:
					vert.sorting += vert.y
				else:
					vert.sorting -= vert.y
			if z is not None:
				if z:
					vert.sorting += vert.z
				else:
					vert.sorting -= vert.z

		sort = sorted(verts, key=operator.attrgetter("sorting"))
		best = sort[-1]

		ties = []
		for vert in sort:
			if vert.sorting == best.sorting:
				ties.append(vert)

		return best, ties

	def get_all_vertices(self) -> List[Vertex, ...]:
		"""
		Finds all vertices on the solid, including overlapping ones from the different sides, for only unique vertices
		use :func:`~Solid.get_only_unique_vertices`

		:return: All the vertices on the solid
		:rtype: :obj:`list` of :class:`Vertex`
		"""
		vertex_list = []
		for side in self.side:
			vertex_list.extend(side.plane)
		return vertex_list

	def get_sides(self) -> List[Side, ...]:
		"""
		:return: All the sides on the solid
		:rtype: :obj:`list` of :class:`Side`
		"""
		return self.side

	@property
	def size(self) -> Vertex:
		"""
		:return: The total size of the bounding rectangle around the solid
		:rtype: :class:`Vertex`
		"""
		x = []
		y = []
		z = []
		for vert in self.get_all_vertices():
			x.append(vert.x)
			y.append(vert.y)
			z.append(vert.z)

		return Vertex(max(x) - min(x), max(y) - min(y), max(z) - min(z))

	def get_displacement_sides(self) -> List[Side]:
		"""
		Gets the sides that have displacements, use :func:`~Solid.get_displacement_matrix_sides` to get the matrices
		directly instead

		:return: The sides with displacements on them
		:rtype: :obj:`list` of :class:`Side`
		"""
		li = []
		for side in self.side:
			if side.dispinfo is not None:
				li.append(side)
		return li

	def get_displacement_matrix_sides(self) -> List[Matrix, ...]:
		"""
		Gets the matrices from all the sides that have displacements, use :func:`~Solid.get_displacement_sides` to get
		the sides instead

		:return: The matrices from the sides with displacements on them
		:type: :obj:`list` of :class:`Matrix`
		"""
		li = []
		for side in self.get_displacement_sides():
			li.append(side.dispinfo.matrix)
		return li

	def get_texture_sides(self, name: str, exact=False) -> List[Side, ...]:
		"""
		:param name: The name of the texture including path (ex: tools/toolsnodraw)
		:type name: :obj:`string`
		:param exact: Determines if the material has to be letter for letter the same or just contain the string
		:type exact: :obj:`bool`
		:return: The sides using the given texture
		:rtype: :obj:`list` of :class:`Side`
		"""
		li = []
		for side in self.side:
			if not exact:
				if name.upper() in side.material:
					li.append(side)
			else:
				if side.material == name.upper():
					li.append(side)
		return li

	def get_only_unique_vertices(self) -> List[Vertex, ...]:
		"""
		Finds all unique vertices on the solid, **you should not use this for vertex manipulation as changing one
		doesn't change all of them**. See :func:`~Solid.get_all_vertices`

		:return: all unique vertices
		:rtype: :obj:`list` of :class:`Vertex`
		"""
		vertex_list = []
		for side in self.side:
			for vertex in side.plane:
				if vertex not in vertex_list:
					vertex_list.append(vertex)

		return vertex_list

	def has_texture(self, name: str, exact=False) -> bool:
		"""
		:param name: The name of the texture including path (ex: tools/toolsnodraw)
		:type name: :obj:`string`
		:param exact: Determines if the material has to be letter for letter the same or just contain the string
		:type exact: :obj:`bool`
		:return: if any sides of the solid contain the given texture
		:rtype: :obj:`bool`
		"""
		for side in self.side:
			if not exact:
				if name.upper() in side.material:
					return True
			else:
				if side.material == name.upper():
					return True
		return False

	def replace_texture(self, old_material: str, new_material: str):
		"""
		Checks all the sides if they have the given texture, if so replace it

		:param old_material: The texture to check
		:type old_material: :obj:`String`
		:param new_material: The texture to replace the old one with
		:type new_material: :obj:`String`
		"""
		for side in self.side:
			if side.material == old_material:
				side.material = new_material
	
	def set_texture(self, new_material: str):
		"""
		Set the texture on every side of the solid

		:param new_material: The texture to set to
		:type new_material: :obj:`String`
		"""
		for side in self.side:
			side.material = new_material

	def naive_subdivide(self, x=1, y=1, z=1) -> List[Solid, ...]:
		"""
		Naively subdivides a copy of the solid, works best for rectangular shapes. It's naive because it scales down
		the solid then creates an array from that

		:param x: Amount of cuts on the x axis
		:type x: :obj:`int`
		:param y: Amount of cuts on the y axis
		:type y: :obj:`int`
		:param z: Amount of cuts on the z axis
		:type z: :obj:`int`
		:return: Solids from a subdivided solid
		:rtype: :obj:`list` of :class:`Solid`
		"""
		li = []

		s = self.copy()

		half_size = s.size
		half_size.divide(2)

		ratio = (1 / x, 1 / y, 1 / z)

		s.scale(s.center, *ratio)

		move_amount = s.size

		s.move(-half_size.x, half_size.y, half_size.z)
		s.move(move_amount.x / 2, -move_amount.y / 2, -move_amount.z / 2)

		for iz in range(z):
			for iy in range(y):
				for ix in range(x):
					s2 = s.copy()
					s2.move(ix * move_amount.x, -iy * move_amount.y, -iz * move_amount.z)
					li.append(s2)

		return li

	def window(self, direction: Vertex = None) -> List[Solid, Solid, Solid, Solid]:
		"""
		Creates a hole in the wall, only works on 90 degree blocks

		:param direction: If set defines the direction the hole will be made, requires exactly 2 non-zero values
		:type direction: :class:`Vertex`
		:return: The 4 blocks surrounding the hole
		:rtype: :obj:`list` of :class:`Solid`
		"""
		dim = [0, 0, 0]
		div_amount = 3
		smallest_pos = 0

		if direction is None:
			size = self.size.export()
			smallest = min(size)

			cube_check = False
			for i, pos in enumerate(size):
				if pos == smallest and not cube_check:
					dim[i] = 1
					smallest_pos = i
					cube_check = True
				else:
					dim[i] = div_amount

		else:
			error = 0
			for i, pos in enumerate(direction.export()):
				if pos != 0:
					dim[i] = div_amount
					smallest_pos = i
					error += 1
				else:
					dim[i] = 1

			if error != 2:
				raise ValueError("Only 2 directions are accepted, please read the docs")

		sub = self.naive_subdivide(*dim)
		req = [sub[1], sub[3], sub[5], sub[7]]
		s1 = req[0]
		s2 = req[-1]

		if smallest_pos == 0:
			s1.scale(s1.center, 1, div_amount)
			s2.scale(s2.center, 1, div_amount)
		else:
			s1.scale(s1.center, div_amount)
			s2.scale(s2.center, div_amount)

		return req

	def is_simple_solid(self) -> bool:
		"""
		:return: A solid is considered simple if it has 6 or less sides
		:rtype: :obj:`bool`
		"""
		return len(self.side) <= 6

	def link_vertices(self, similar=0.0):
		"""
		Tries to link all the vertices that are similiar

		:param similar:
		"""
		vertex_list = []

		for side in self.get_sides():
			for i, vertex in enumerate(side.get_vertices()):
				for vertex_check in vertex_list:
					if vertex.similar(vertex_check, similar):
						side.plane[i] = vertex_check
					else:
						vertex_list.append(vertex)

	def set_texture(self, new_material: str):
		"""
		Sets the given texture on all sides

		:param new_material: The texture to replace them all
		:type new_material: :obj:`str`
		"""
		for side in self.get_sides():
			side.material = new_material

	def remove_all_displacements(self):
		"""
		Removes all displacements from the solid
		"""
		for side in self.side:
			side.remove_displacement()

	def export_children(self):
		return (*self.side, self.editor)


class Editor(Common):
	NAME = "editor"

	def __init__(self, dic: dict = None, parent_type=None):
		dic = self._dic(dic)

		self.parent_type = parent_type  # This is not used in the VMF

		self.color = dic.pop("color", "0 0 0")
		self.color = Convert.string_to_color(self.color)
		self.groupids = dic.pop("groupid", []) #Note this is an attribute for our purposes only; vmf only contains "groupid" (singular). Contains a list of all the editor's group ids
		self.visgroupids = dic.pop("visgroupid", []) #Note this is an attribute for our purposes only; vmf only contains "visgroupid" (singular). Contains a list of all the editor's visgroup ids
		self.visgroupshown = dic.pop("visgroupshown", 1)
		self.visgroupautoshown = dic.pop("visgroupautoshown", 1)
		self.logicalpos = dic.pop("logicalpos", "[0 2500]")  # Unique to Entity

		self.other = dic
		self.export_list = []

	def has_visgroup(self,visgroupid) -> bool:
		for _id in self.visgroupids:
			if _id == visgroupid:
				return True
		return False

	def add_visgroup(self,visgroupid):
		if visgroupid not in self.visgroupids:
			self.visgroupids.append(visgroupid)

	def remove_visgroup(self,visgroupid):
		if visgroupid in self.visgroupids:
			self.visgroupids.remove(visgroupid)

	def remove_all_visgroups(self):
		self.visgroupids = []

	def remove_all_groups(self):
		self.groupids = []

	def export(self,export_mode="CSGO"):
		d = {"color": self.color}
		if self.groupids is not None:
			d["groupid"] = self.groupids
		if self.visgroupids is not None:
			d["visgroupid"] = self.visgroupids
		d["visgroupshown"] = self.visgroupshown
		d["visgroupautoshown"] = self.visgroupautoshown
		if self.parent_type == "entity":
			d["logicalpos"] = self.logicalpos

		return d, self.other


class Group(Common):
	NAME = "group"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.id = dic.pop("id", self.ids())

		self.other = dic
		self.export_list = ["id"]

		self.editor = None
		for child in children:
			if str(child) == Editor.NAME:
				self.editor = Editor(child.dic)

	def export_children(self):
		return [self.editor]


class Side(Common):
	"""
	Corresponds to a face/side of a solid. Sides are defined by 3 vertices, the combination of which define an
	infinitely large plane, source calculates the intersection between these planes to determine where the edges are.
	This is not currently calculated in PyVMF, so some methods may behave unpredictably.

	:param dic: All the values to be initialized, if empty default values are used.
	:type dic: :obj:`dict`
	:param children: Holds a potential displacement :class:`DispInfo` to be initialized
	:type children: :obj:`list`
	"""

	NAME = "side"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.id = dic.pop("id", self.ids())

		p = dic.pop("plane", "(0 0 0) (0 0 0) (0 0 0)")
		self.plane = Convert.string_to_3x_vertex(p)

		self.material = dic.pop("material", "TOOLS/TOOLSNODRAW")

		self.uaxis = dic.pop("uaxis", "[1 0 0 0] 0.25")
		self.uaxis = Convert.string_to_uvaxis(self.uaxis)
		self.vaxis = dic.pop("vaxis", "[0 -1 0 0] 0.25")
		self.vaxis = Convert.string_to_uvaxis(self.vaxis)

		self.rotation = dic.pop("rotation", 0)
		self.lightmapscale = dic.pop("lightmapscale", 16)
		self.smoothing_groups = dic.pop("smoothing_groups", 0)

		self.other = dic
		self.export_list = []

		self.dispinfo = None
		for child in children:
			if str(child) == DispInfo.NAME:
				self.dispinfo = DispInfo(child.dic, child.children, self)

	def __str__(self):
		return f"({self.plane[0]}) ({self.plane[1]}) ({self.plane[2]})"

	def move(self, x, y, z):
		"""
		Moves the side by the given amount

		:param x: Amount to move the x axis by
		:type x: :obj:`int` or :obj:`float`
		:param y: Amount to move the y axis by
		:type y: :obj:`int` or :obj:`float`
		:param z: Amount to move the z axis by
		:type z: :obj:`int` or :obj:`float`
		"""
		for vertex in self.plane:
			vertex.move(x, y, z)

	def rotate_x(self, center: Vertex, angle):
		"""
		Rotates the side around the x axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for vert in self.plane:
			vert.rotate_x(center, angle)

	def rotate_y(self, center: Vertex, angle):
		"""
		Rotates the vertex around the y axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for vert in self.plane:
			vert.rotate_y(center, angle)

	def rotate_z(self, center: Vertex, angle):
		"""
		Rotates the vertex around the z axis

		:param center: The point to rotate around
		:type center: :class:`Vertex`
		:param angle: How much to rotate in degrees
		:type angle: :obj:`int` or :obj:`float`
		"""
		for vert in self.plane:
			vert.rotate_z(center, angle)

	def get_naive_rotation(self) -> int:
		"""
		Gets the rotation if and only if it's a multiple of 90, please don't use this if it's not necessary

		:return: Rotation of the face either 0, 90, 180 or 270
		:rtype: :obj:`int`
		"""
		v1, v2 = Vector.vectors_from_side(self)
		v1 = v1.angle_to_origin()
		v2 = v2.angle_to_origin()

		if v1 == 0 and v2 == 90:
			return 0

		if v1 == 90 and v2 == 0:
			return 90

		if v1 == 180 and v2 == 90:
			return 180

		if v1 == 90 and v2 == 180:
			return 270

		warnings.warn("Unable to determine rotation, default to 0")
		return 0

	def flip(self, x=None, y=None, z=None):
		raise ValueError("The flip function doesn't currently work")
		for vert in self.plane:
			vert.flip(x, y, z)

	def get_vertices(self) -> List[Vertex, Vertex, Vertex]:
		"""
		:return: All 3 vertices that define the plane
		:rtype: :obj:`list` of :class:`Vertex`
		"""
		return self.plane

	def get_displacement(self) -> DispInfo:
		"""
		:return: The current displacement, only 1 per side
		:rtype: :class:`DispInfo` or :obj:`None`
		"""
		return self.dispinfo

	def get_vector(self):
		raise ValueError("Vectors not implemented yet")

	def set_texture(self, new_material: str):
		"""
		Sets the texture on all sides to the given material

		:param new_material: The texture to use
		:type new_material: :obj:`str`
		"""
		self.material = new_material

	def remove_displacement(self):
		"""
		Removes the diplacement from the side
		"""
		self.dispinfo = None

	def export(self,export_mode="CSGO"):
		d = {"id": self.id,
			 "plane": self.__str__(),
			 "material": self.material,
			 "uaxis": self.uaxis,
			 "vaxis": self.vaxis,
			 "rotation": self.rotation,
			 "lightmapscale": self.lightmapscale,
			 "smoothing_groups": self.smoothing_groups}

		return d, self.other

	def export_children(self):
		return [self.dispinfo]


class DispInfo(Common):
	"""
	Keeps track of all the different displacement settings and values
	"""

	NAME = "dispinfo"

	def __init__(self, dic: dict = None, children: list = None, parent_side: Side = None):
		dic, children = self._dic_and_children(dic, children)

		self.power = dic.pop("power", 3)
		"""The displacement power, can only be 2, 3 or 4"""

		_startposition = dic.pop("startposition", "[0 0 0]")
		self._startposition = Convert.string_to_vertex(_startposition)
		self._startposition.normal = 1
		self.flags = dic.pop("flags", 0)
		self.elevation = dic.pop("elevation", 0)
		self.subdiv = dic.pop("subdiv", 0)

		self.parent_side = parent_side
		self.size = 0
		self.matrix_size_fix = 0

		if self.power == 2 or self.power == 4:
			self.matrix_size_fix = self.power ** 2
			self.size = self.matrix_size_fix + 1
		else:
			self.size = self.power ** 2
			self.matrix_size_fix = self.size - 1

		self.matrix = Matrix(self.size)

		self.other = dic
		self.export_list = ["power", "startposition", "flags", "elevation", "subdiv"]

		self._normals = None
		self._distances = None
		self._offsets = None
		self._offset_normals = None
		self._alphas = None
		self._triangle_tags = None
		self._allowed_verts = None

		for child in children:
			if str(child) == Normals.NAME:
				self._normals = Normals(self.matrix, child.dic)
			if str(child) == Distances.NAME:
				self._distances = Distances(self.matrix, child.dic)
			if str(child) == Offsets.NAME:
				self._offsets = Offsets(self.matrix, child.dic)
			if str(child) == OffsetNormals.NAME:
				self._offset_normals = OffsetNormals(self.matrix, child.dic)
			if str(child) == Alphas.NAME:
				self._alphas = Alphas(self.matrix, child.dic)
			if str(child) == TriangleTags.NAME:
				self._triangle_tags = TriangleTags(self.matrix, child.dic)
			if str(child) == AllowedVerts.NAME:
				self._allowed_verts = AllowedVerts(self.matrix, child.dic)

	@property
	def startposition(self):
		return self._startposition

	@startposition.setter
	def startposition(self, value: Vertex):
		self._startposition = value
		self._startposition.normal = 1

	def is_flipped(self) -> bool:
		"""
		Finds out if the displacement has been flipped, might not work if the face is non rectangular

		:return: If the displacement has been flipped
		:rtype: :obj:`bool`
		"""
		v1, v2 = Vector.vectors_from_side(self.parent_side)
		if self.parent_side.plane[1].copy() + v1 + v2 == self.startposition:
			return False

		if self.parent_side.plane[1].copy() + v1 == self.startposition:
			return True

		warnings.warn("Unable to determine if flipped, default to False")
		return False

	def export_children(self):
		return self._normals, self._distances, self._offsets, self._offset_normals, self._alphas, \
			   self._triangle_tags, self._allowed_verts


class DispVert(Common):
	"""
	Keeps track of each individual displacement vertex
	"""

	def __init__(self):
		self.normal = Vertex()
		self.distance = 0
		self.offset = Vertex()
		self.offset_normal = Vertex(0, 0, 1)
		self.alpha = 0
		self.triangle_tag = None

	def __str__(self):
		return f"{self.normal} {self.distance}"

	def set(self, normal: Vertex, distance: int):
		"""
		Sets the normal direction and distance

		:param normal: The normal direction (x, y and z)
		:type normal: :class:`Vertex`
		:param distance: How far to go in the normal direction
		:type distance: :obj:`int`
		"""
		self.normal.set(*normal.export())
		self.distance = distance

	def scale(self, scale: float):
		"""
		Scale relevant vert data by the given multiplier just as the Hammer transform option would. ONLY USE IF YOU'RE SCALING BY THE SAME MULTIPLIER ON ALL 3 AXES
		"""
		self.normal.multiply(scale)
		self.offset.multiply(scale)
		self.offset_normal.multiply(scale)

	def set_alpha(self, amount: int):
		"""
		Sets the alpha, used by blend textures, 0 is the first texture, 255 is the second texture, 127 is both

		:param amount: The alpha amount, between 0 and 255
		:type amount: :obj:`int`
		"""
		if amount < 0 or amount > 255:
			raise ValueError(f"Error: {amount} not in range [0, 255]")
		else:
			self.alpha = amount


class TriangleTag(Common):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return f"{self.x} {self.y}"


class Matrix(Common):
	"""
	A grid for keeping track of the displacement values.

	:param size: The size of the 2 dimensional grid
	:type size: :obj:`int`
	"""

	def __init__(self, size: int):
		self.size = size
		self.matrix = [[DispVert() for y in range(self.size)] for x in range(self.size)]

	def __str__(self):
		return str(self.matrix)

	def get_size(self):
		return self.size

	def get(self, x: int, y: int) -> DispVert:
		"""
		:param x: Position x in the matrix
		:type x: :obj:`int`
		:param y: Position y in the matrix
		:type y: :obj:`int`
		:return: Displacement information at the given position
		:rtype: :class:`DispVert`
		"""
		return self.matrix[x][y]

	def row(self, y: int) -> List[DispVert, ...]:
		"""
		:param y: The row to get
		:type y: :obj:`int`
		:return: All the disp verts on the given row
		:rtype: :obj:`list` of :class:`DispVert`
		"""
		li = []
		for x in range(self.size):
			li.append(self.matrix[x][y])
		return li

	def column(self, x: int) -> List[DispVert, ...]:
		"""
		:param x: The column to get
		:type x: :obj:`int`
		:return: All the disp verts on the given column
		:rtype: :obj:`list` of :class:`DispVert`
		"""
		return self.matrix[x]

	def rect(self, x: int, y: int, w: int, h: int) -> Generator[DispVert, ...]:
		"""
		:param x: Position x in the matrix
		:param y: Position y in the matrix
		:param w: Width of the rectangle
		:param h: Height of the rectangle
		:return: Yields all the disp verts inside the given rectangle
		:rtype: :obj:`generator` of :class:`DispVert`
		"""
		for y2 in range(y, y + h):
			for x2 in range(x, x + w):
				yield x2, y2, self.get(x2, y2)

	def inv_rect(self, x, y, w, h, step):
		for y2 in range(y, y + h, step):
			for x2 in range(x, x + w, step):
				yield x2, y2, self.get(x2, self.size - y2 - 1)

	def extract_dic(self, dic, a_var=1, triangle=False):
		"""
		Extracts the data from the .VMF file string, you shouldn't need to use this

		:param dic: Holds all the rows
		:type dic: :obj:`dict` of :obj:`str`: :obj:`str`
		:param a_var: How many variables to group, use 3 to group the 'x y z' format, if single int use 1
		:type a_var: :obj:`int`
		:param triangle: :class:`TriangleTags` holds 1 less value than all other displacement variables
		:type triangle: :obj:`bool`
		:return: The x and y position in the matrix and the values
		:rtype: :obj:`int`, :obj:`int`, :obj:`list` of :obj:`str`
		"""
		for y in range(self.size - triangle):
			t = dic.pop(f"row{y}").split(" ")
			for x in range((self.size - triangle) * a_var):
				yield x, y, t

	def export_attr(self, attribute):
		"""
		Exports the data in .VMF file ready format, used when exporting the PyVMF, you shouldn't need to use this

		:param attribute: Which of the attributes to export (normals, distances, ...)
		:type attribute: :obj:`str`
		:return: Row to values association
		:rtype: :obj:`dict` of :obj:`str`: :obj:`str`
		"""
		e = {}
		for y in range(self.size):
			current_row = f"row{y}"
			temp = getattr(self.row(y)[0], attribute)
			if temp is not None:
				e[current_row] = f"{temp}"
			for row in self.row(y)[1:]:
				temp = getattr(row, attribute)
				if temp is not None:
					e[current_row] += f" {temp}"

		return e


class Normals(Common):
	NAME = "normals"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix
		a_var = 3
		i = 0
		for x, y, t in self.matrix.extract_dic(dic, a_var):
			if i == 0:
				self.matrix.get(x // a_var, y).normal.x = num(t[x])
			elif i == 1:
				self.matrix.get(x // a_var, y).normal.y = num(t[x])
			else:
				self.matrix.get(x // a_var, y).normal.z = num(t[x])
				i = -1
			i += 1

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("normal"), self.other


class Distances(Common):
	NAME = "distances"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix
		for x, y, t in self.matrix.extract_dic(dic):
			self.matrix.get(x, y).distance = num(t[x])

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("distance"), self.other


class Offsets(Common):
	NAME = "offsets"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix
		a_var = 3
		i = 0
		for x, y, t in self.matrix.extract_dic(dic, a_var):
			if i == 0:
				self.matrix.get(x // a_var, y).offset.x = num(t[x])
			elif i == 1:
				self.matrix.get(x // a_var, y).offset.y = num(t[x])
			else:
				self.matrix.get(x // a_var, y).offset.z = num(t[x])
				i = -1
			i += 1

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("offset"), self.other


class OffsetNormals(Common):
	NAME = "offset_normals"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix
		a_var = 3
		i = 0
		for x, y, t in self.matrix.extract_dic(dic, a_var):
			if i == 0:
				self.matrix.get(x // a_var, y).offset_normal.x = num(t[x])
			elif i == 1:
				self.matrix.get(x // a_var, y).offset_normal.y = num(t[x])
			else:
				self.matrix.get(x // a_var, y).offset_normal.z = num(t[x])
				i = -1
			i += 1

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("offset_normal"), self.other


class Alphas(Common):
	NAME = "alphas"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix
		for x, y, t in self.matrix.extract_dic(dic):
			self.matrix.get(x, y).alpha = num(t[x])

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("alpha"), self.other


class TriangleTags(Common):
	NAME = "triangle_tags"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.matrix = matrix  # TriangleTags is 1 row and column smaller than the others
		a_var = 2
		i = 0
		t1 = 0
		for x, y, t in self.matrix.extract_dic(dic, a_var, True):
			if i == 0:
				t1 = num(t[x])
			else:
				self.matrix.get(x // a_var, y).triangle_tag = TriangleTag(t1, num(t[x]))
				i = -1
			i += 1

		self.other = dic
		self.export_list = []

	def export(self,export_mode="CSGO"):
		return self.matrix.export_attr("triangle_tag"), self.other


class AllowedVerts(Common):
	NAME = "allowed_verts"

	def __init__(self, matrix, dic: dict = None):
		dic = self._dic(dic)

		self.other = dic
		self.export_list = []


class UVaxis(Common):
	def __init__(self, x, y, z, offset, scale):
		self.x = x
		self.y = y
		self.z = z
		self.offset = offset
		self.scale = scale

	def __str__(self):
		return f"[{self.x} {self.y} {self.z} {self.offset}] {self.scale}"

	def localize(self, side):
		pass

	def export(self,export_mode="CSGO"):
		return (self.x,
				self.y,
				self.z,
				self.offset,
				self.scale)


class Vector(Common):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self):
		return f"{self.x} {self.y} {self.z}"

	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

	def __mul__(self, other):
		return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

	def dot(self, other):
		t = self * other
		return t.x + t.y + t.z

	def cross(self, other):
		return Vector((self.y * other.z - self.z * other.y),
					  (self.z * other.x - self.x * other.z),
					  (self.x * other.y - self.y * other.x))

	def normalize(self):
		m = self.mag()
		self.x /= m
		self.y /= m
		self.z /= m

	def mag(self):
		return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

	def angle(self, other):
		return math.degrees(math.acos(self.dot(other) / (self.mag() * other.mag())))

	def angle_to_origin(self):
		return Vector(-1, 0, 0).angle(self)

	def to_vertex(self):
		return Vertex(self.x, self.y, self.z)

	@classmethod
	def vector_from_2_vertices(cls, v1: Vertex, v2: Vertex):
		return Vector(*(v2 - v1).export())

	@classmethod
	def vectors_from_side(cls, side: Side) -> Tuple[Vector, Vector]:
		return cls.vector_from_2_vertices(side.plane[1], side.plane[0]), \
			   cls.vector_from_2_vertices(side.plane[1], side.plane[2])


class Hidden(Common):
	NAME = "hidden"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.other = dic
		self.export_list = []

		self.entity = None
		self.solids = None #TODO pretty sure this can just be called "solid" since a hidden section can have at most one entity or one solid
		for child in children:

			#TODO make this whole section a Common class method so we can update it in one place instead of both load_vmf and here
			if str(child) == Entity.NAME:
				classname = child.dic["classname"]
				if classname == Light.SUBNAME:
					e = Light(child.dic, child.children)
				elif classname == PropStatic.SUBNAME:
					e = PropStatic(child.dic, child.children)
				elif classname == PropDynamic.SUBNAME:
					e = PropDynamic(child.dic, child.children)
				elif classname == SkyCamera.SUBNAME:
					e = SkyCamera(child.dic, child.children)
				elif classname == EnvFogController.SUBNAME:
					e = EnvFogController(child.dic, child.children)
				elif classname == FuncDetail.SUBNAME:
					e = FuncDetail(child.dic, child.children)
				elif classname == FuncBrush.SUBNAME:
					e = FuncBrush(child.dic, child.children)
				else:
					e = Entity(child.dic, child.children)
				self.entity = e

			elif str(child) == Solid.NAME:
				self.solids = Solid(child.dic, child.children)

	def export_children(self):
		return self.entity, self.solids


class Entity(Common):
	NAME = "entity"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.id = dic.pop("id", self.ids())
		self.classname = dic.pop("classname", "info_player_terrorist")
		self.origin = Convert.string_to_vertex(dic.pop("origin","0 0 0"))

		self.other = dic
		self.export_list = ["id", "classname", "origin"]

		self.connections = []
		self.solids = []
		self.hidden = []
		self.editor = None
		for child in children:
			if str(child) == Solid.NAME:
				self.solids.append(Solid(child.dic, child.children))

			elif str(child) == Hidden.NAME:
				self.hidden.append(Hidden(child.dic, child.children))

			elif str(child) == Editor.NAME:
				self.editor = Editor(child.dic, Entity.NAME)

			elif str(child) == Connections.NAME:
				self.connections.append(Connections(child.dic))

	def getOrigin(self):
		return self.origin

	def move(self, x, y, z):
		"""
		Moves the entity by the given amounts in Hammer units on x, y, and z planes

		:param x:
		:type x: :obj:`int` or :obj:`float`
		:param y:
		:type y: :obj:`int` or :obj:`float`
		:param z:
		:type z: :obj:`int` or :obj:`float`
		"""
		self.origin += Vertex(x, y, z)

	def scale(self, vertexToScaleRelativeTo: Vertex, x=1.0, y=1.0, z=1.0):
		"""
		Scale the entity's origin by the supplied xyz multipliers, relative to the given vertex
		"""
		x -= 1
		y -= 1
		z -= 1
		diff = self.origin - vertexToScaleRelativeTo
		scaledDiff = Vertex(diff.x * x, diff.y * y, diff.z * z)
		self.origin += scaledDiff

	def export_children(self):
		return (*self.connections, *self.solids, *self.hidden, self.editor)


class Light(Entity):
	SUBNAME = "light"

	def __init__(self, dic: dict = None, children: list = None):
		super(Light, self).__init__(dic, children)

		self._constant_attn = self.other.pop("_constant_attn", 0)
		self._distance = self.other.pop("_distance", 0)
		self._fifty_percent_distance = self.other.pop("_fifty_percent_distance", 0)
		self._hardfalloff = self.other.pop("_hardfalloff", 0)
		_light = self.other.pop("_light", "255 255 255 200")
		self._light = Convert.string_to_color_light(_light)
		self._lightHDR = self.other.pop("_lightHDR", "[-1 -1 -1 1]")
		self._lightscaleHDR = self.other.pop("_lightscaleHDR", 1)
		self._linear_attn = self.other.pop("_linear_attn", 0)
		self._quadratic_attn = self.other.pop("_quadratic_attn", 1)
		self._zero_percent_distance = self.other.pop("_zero_percent_distance", 0)
		self.spawnflags = self.other.pop("spawnflags", 0)
		self.style = self.other.pop("style", 0)

		self.export_list = ["id", "classname", "_constant_attn", "_distance", "_fifty_percent_distance",
							"_hardfalloff", "_light", "_lightHDR", "_lightscaleHDR", "_linear_attn", "_quadratic_attn",
							"_quadratic_attn", "_zero_percent_distance", "spawnflags", "style", "origin"]

class PropStatic(Entity):
	SUBNAME = "prop_static"

	def __init__(self, dic: dict = None, children: list = None):
		super().__init__(dic, children)

		angles = self.other.pop("angles", "0 0 0")
		self.angles = Convert.string_to_vertex(angles)
		self.disableflashlight = self.other.pop("disableflashlight", 0)
		self.disableselfshadowing = self.other.pop("disableselfshadowing", 0)
		self.disableshadowdepth = self.other.pop("disableshadowdepth", 0)
		self.disableshadows = self.other.pop("disableshadows", 0)
		self.disablevertexlighting = self.other.pop("disablevertexlighting", 0)
		self.disableX360 = self.other.pop("disableX360", 0)
		self.drawinfastreflection = self.other.pop("drawinfastreflection", 0)
		self.enablelightbounce = self.other.pop("enablelightbounce", 0)
		self.fademaxdist = self.other.pop("fademaxdist", 0)
		self.fademindist = self.other.pop("fademindist", -1)
		self.fadescale = self.other.pop("fadescale", 1)
		self.ignorenormals = self.other.pop("ignorenormals", 0)
		self.maxcpulevel = self.other.pop("maxcpulevel", 0)
		self.maxgpulevel = self.other.pop("maxgpulevel", 0)
		self.mincpulevel = self.other.pop("mincpulevel", 0)
		self.mingpulevel = self.other.pop("mingpulevel", 0)
		self.preventpropcombine = self.other.pop("preventpropcombine", 0)
		self.renderamt = self.other.pop("renderamt", 255)
		rendercolor = self.other.pop("rendercolor", "255 255 255")
		self.rendercolor = Convert.string_to_color(rendercolor)
		self.screenspacefade = self.other.pop("screenspacefade", 0)
		self.shadowdepthnocache = self.other.pop("shadowdepthnocache", 0)
		self.skin = self.other.pop("skin", 0)
		self.solid = self.other.pop("solid", 6)
		self.uniformscale = self.other.pop("uniformscale", 1)
		self.model = self.other.pop("model", "")

		#TF2-specific stuff (or at least, non-CSGO stuff)
		self.generatelightmaps = self.other.pop("generatelightmaps", 0)
		self.lightmapresolutionx = self.other.pop("lightmapresolutionx", 32)
		self.lightmapresolutiony = self.other.pop("lightmapresolutiony", 32)
		self.maxdxlevel = self.other.pop("maxdxlevel", 0)
		self.mindxlevel = self.other.pop("mindxlevel", 0)


		self.export_list = ["id", "classname", "angles", "disableflashlight", "disableselfshadowing",
							"disableshadowdepth", "disableshadows", "disablevertexlighting", "disableX360",
							"drawinfastreflection", "enablelightbounce", "fademaxdist", "fademindist", "fadescale",
							"ignorenormals", "maxcpulevel", "maxgpulevel", "mincpulevel", "mingpulevel",
							"preventpropcombine", "renderamt", "rendercolor", "screenspacefade", "shadowdepthnocache",
							"skin", "solid", "uniformscale", "model", "origin"]

		#This list is a temporary fix; see comment on the export method below
		self.export_list_tf2 = ["id", "classname", "angles", "disableselfshadowing", "disableshadows",
								"disablevertexlighting", "fademaxdist", "fademindist", "fadescale",
								"ignorenormals", "screenspacefade", "skin", "solid", "model",
								"generatelightmaps","lightmapresolutionx","lightmapresolutiony",
                          		"maxdxlevel", "mindxlevel", "origin"]

	#Overriding the Common export method here is a temporary fix to prevent unnecessary CSGO prop attributes that don't exist in TF2 from being exported to TF2-based VMFs; more thorough solution to come
	def export(self,mode="CSGO"): #TODO cleanup
		"""
		Gets all the variables than need to be exported into the .VMF file

		:return: All predefined (in `export_list`) variable names and their associated values
		:rtype: :obj:`dict`, :obj:`dict`
		"""
		d = {}
		if "preventpropcombine" in self.other: #Following up on the fact that editor builds can't be used to reliably discern what game the VMF is for,
			mode = "CSGO" #checking if a CSGO-only attribute exists in the prop is the only other way I can think of to do it right now
		else:
			mode = "TF2"
		if mode == "CSGO":
			for item in self.export_list:
				t = getattr(self, item)
				d[item] = t
		elif mode == "TF2":
			for item in self.export_list_tf2:
				t = getattr(self, item)
				d[item] = t
		return d, self.other

class PropDynamic(Entity):
	SUBNAME = "prop_dynamic"

	def __init__(self, dic: dict = None, children: list = None):
		super().__init__(dic, children)

		self.model = self.other.pop("model", "")
		angles = self.other.pop("angles", "0 0 0")
		self.angles = Convert.string_to_vertex(angles)
		#We could pop more stuff from self.other but really we only need these properties to be accessible

		self.export_list = ["id", "classname", "origin", "model", "angles"]

class InfoDecal(Entity):
	SUBNAME = "infodecal"

	def __init__(self, dic: dict = None, children: list = None):
		super(InfoDecal, self).__init__(dic, children)

		self.texture = self.other.pop("texture", "tools/toolsnodraw")

		self.export_list = ["id", "classname", "texture", "origin"]

class InfoOverlay(Entity):
	SUBNAME = "info_overlay"

	def __init__(self, dic: dict = None, children: list = None):
		super(InfoOverlay, self).__init__(dic, children)

		angles = self.other.pop("angles", "0 0 0")
		self.angles = Convert.string_to_vertex(angles)
		BasisNormal = self.other.pop("BasisNormal", "0 -1 0")
		self.BasisNormal = Convert.string_to_vertex(BasisNormal)
		BasisOrigin = self.other.pop("BasisOrigin", "0 0 0")
		self.BasisOrigin = Convert.string_to_vertex(BasisOrigin)
		BasisU = self.other.pop("BasisU", "1 0 0")
		self.BasisU = Convert.string_to_vertex(BasisU)
		BasisV = self.other.pop("BasisV", "0 0 1")
		self.BasisV = Convert.string_to_vertex(BasisV)
		self.EndU = self.other.pop("EndU", 1)
		self.EndV = self.other.pop("EndV", 0)
		self.fademindist = self.other.pop("fademindist", -1)
		self.material = self.other.pop("material", "tools/toolsnodraw")
		self.sides = self.other.pop("sides", "1")
		self.StartU = self.other.pop("StartU", 0)
		self.StartV = self.other.pop("StartV", 1)
		uv0 = self.other.pop("uv0", "-128 -128 0")
		self.uv0 = Convert.string_to_vertex(uv0)
		uv1 = self.other.pop("uv1", "-128 128 0")
		self.uv1 = Convert.string_to_vertex(uv1)
		uv2 = self.other.pop("uv2", "128 128 0")
		self.uv2 = Convert.string_to_vertex(uv2)
		uv3 = self.other.pop("uv3", "128 -128 0")
		self.uv3 = Convert.string_to_vertex(uv3)

		self.export_list = ["id", "classname", "angles", "BasisNormal", "BasisOrigin", "BasisU", "BasisV",
							"EndU", "EndV", "fademindist", "material", "sides", "StartU",
							"StartV", "uv0", "uv1", "uv2", "uv3", "origin"]

	def add_sides(self, *sides: Side):
		for side in sides:
			if self.sides == "":
				self.sides = str(side.id)
			else:
				self.sides += f" {side.id}"

class SkyCamera(Entity):
	SUBNAME = "sky_camera"

	def __init__(self, dic: dict = None, children: list = None):
		super(SkyCamera, self).__init__(dic, children)

		angles = self.other.pop("angles", "0 0 0")
		self.angles = Convert.string_to_vertex(angles)
		fogcolor = self.other.pop("fogcolor","255 255 255")
		self.fogcolor = Convert.string_to_color(fogcolor)
		fogcolor2 = self.other.pop("fogcolor2","255 255 255")
		self.fogcolor2 = Convert.string_to_color(fogcolor2)
		fogdir = self.other.pop("fogdir","1 0 0")
		self.fogdir = Convert.string_to_vertex(fogdir)
		self.fogend = self.other.pop("fogend",2000.0)
		self.fogmaxdensity = self.other.pop("fogmaxdensity",1)
		self.fogstart = self.other.pop("fogstart",500.0)
		self.scale = self.other.pop("scale",16)
		self.fogblend = self.other.pop("fogblend",0)
		self.fogenable = self.other.pop("fogenable",0)
		self.use_angles = self.other.pop("use_angles",0)

		self.export_list = ["id", "classname", "angles", "origin", "fogcolor", "fogcolor2",
							"fogdir", "fogend", "fogmaxdensity", "fogstart", "scale", "fogblend",
							"fogenable", "use_angles"]

class EnvFogController(Entity):
	SUBNAME = "env_fog_controller"

	def __init__(self, dic: dict = None, children: list = None):
		super(EnvFogController, self).__init__(dic, children)

		angles = self.other.pop("angles", "0 0 0")
		self.angles = Convert.string_to_vertex(angles)
		self.farz = self.other.pop("farz",-1)
		fogcolor = self.other.pop("fogcolor","255 255 255")
		self.fogcolor = Convert.string_to_color(fogcolor)
		fogcolor2 = self.other.pop("fogcolor2","255 255 255")
		self.fogcolor2 = Convert.string_to_color(fogcolor2)
		fogdir = self.other.pop("fogdir","1 0 0")
		self.fogdir = Convert.string_to_vertex(fogdir)
		self.fogend = self.other.pop("fogend",2000.0)
		self.fogmaxdensity = self.other.pop("fogmaxdensity",1)
		self.fogstart = self.other.pop("fogstart",500.0)
		self.fogblend = self.other.pop("fogblend",0)
		self.mindxlevel = self.other.pop("mindxlevel",0)
		self.fogenable = self.other.pop("fogenable",0)
		self.maxdxlevel = self.other.pop("maxdxlevel",0)
		self.foglerptime = self.other.pop("foglerptime",0)
		self.use_angles = self.other.pop("use_angles",0)
		self.spawnflags = self.other.pop("spawnflags",0)

		self.export_list = ["id", "classname", "angles", "origin", "fogcolor", "fogcolor2",
							"fogdir", "fogend", "fogmaxdensity", "fogstart", "fogblend", "mindxlevel",
							"fogenable", "maxdxlevel", "foglerptime", "use_angles", "spawnflags", "farz"]

class FuncDetail(Entity):
	SUBNAME = "func_detail"

	def __init__(self, dic: dict = None, children: list = None):
		super(FuncDetail, self).__init__(dic, children)

		self.mindxlevel = self.other.pop("mindxlevel", 0)
		self.maxdxlevel = self.other.pop("maxdxlevel", 0)

		self.export_list = ["id", "classname", "mindxlevel", "maxdxlevel"]

	def scale(self, vertexToScaleRelativeTo: Vertex, x=1.0, y=1.0, z=1.0):
		"""
		Scale the func_detail's solids by the supplied xyz multipliers, relative to the given vertex
		"""
		for solid in self.solids:
			solid.scale(vertexToScaleRelativeTo,x,y,z)

	def getXExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the X-axis at which there is a vertex of the func_detail
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.solids[0].side[0].plane[0].getX()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getX() > furthest:
						furthest = vertex.getX()
				else:
					if vertex.getX() < furthest:
						furthest = vertex.getX()
		return furthest

	def getYExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the Y-axis at which there is a vertex of the func_detail
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.solids[0].side[0].plane[0].getY()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getY() > furthest:
						furthest = vertex.getY()
				else:
					if vertex.getY() < furthest:
						furthest = vertex.getY()
		return furthest

	def getZExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the Z-axis at which there is a vertex of the func_detail
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.solids[0].side[0].plane[0].getZ()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getZ() > furthest:
						furthest = vertex.getZ()
				else:
					if vertex.getZ() < furthest:
						furthest = vertex.getZ()
		return furthest

	def move(self, x, y, z):
		"""
		Moves the func_detail by the given amounts in Hammer units on x, y, and z planes

		:param x:
		:type x: :obj:`int` or :obj:`float`
		:param y:
		:type y: :obj:`int` or :obj:`float`
		:param z:
		:type z: :obj:`int` or :obj:`float`
		"""
		for solid in self.solids:
			solid.move(x,y,z)

class FuncBrush(Entity):
	SUBNAME = "func_brush"

	def __init__(self, dic: dict = None, children: list = None):
		super(FuncBrush, self).__init__(dic, children)

		self.disablereceiveshadows = self.other.pop("disablereceiveshadows", 0)
		self.disableshadows = self.other.pop("disableshadows", 0)
		self.InputFilter = self.other.pop("InputFilter", 0)
		self.invert_exclusion = self.other.pop("invert_exclusion", 0)
		self.renderamt = self.other.pop("renderamt", 255)
		self.rendercolor = self.other.pop("rendercolor", Color())
		self.renderfx = self.other.pop("renderfx", 0)
		self.rendermode = self.other.pop("rendermode", 0)
		self.solidbsp = self.other.pop("solidbsp", 0)
		self.Solidity = self.other.pop("Solidity", 0)
		self.spawnflags = self.other.pop("spawnflags", 2)
		self.StartDisabled = self.other.pop("StartDisabled", 0)
		self.vrad_brush_cast_shadows = self.other.pop("vrad_brush_cast_shadows", 0)

		self.export_list = ["id", "classname", "disablereceiveshadows", "disableshadows",
							"InputFilter", "invert_exclusion", "origin", "renderamt", "rendercolor",
							"renderfx", "rendermode", "solidbsp", "Solidity", "spawnflags",
							"StartDisabled", "vrad_brush_cast_shadows"]

	def scale(self, vertexToScaleRelativeTo: Vertex, x=1.0, y=1.0, z=1.0):
		"""
		Scale the func_brush's origin and solids by the supplied xyz multipliers, relative to the given vertex
		"""
		for solid in self.solids:
			solid.scale(vertexToScaleRelativeTo,x,y,z)
		super().scale(vertexToScaleRelativeTo,x,y,z)

	def getXExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the X-axis at which there is a vertex or origin of the func_brush
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.origin.getX()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getX() > furthest:
						furthest = vertex.getX()
				else:
					if vertex.getX() < furthest:
						furthest = vertex.getX()
		return furthest

	def getYExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the Y-axis at which there is a vertex or origin of the func_brush
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.origin.getY()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getY() > furthest:
						furthest = vertex.getY()
				else:
					if vertex.getY() < furthest:
						furthest = vertex.getY()
		return furthest

	def getZExtremity(self, direction: bool):
		"""
		Get the furthest coordinate on the Z-axis at which there is a vertex or origin of the func_brush
		True for the highest coordinate, False for the lowest coordinate
		"""
		furthest = self.origin.getZ()
		for solid in self.solids:
			vertices = solid.get_only_unique_vertices()
			for vertex in vertices:
				if direction:
					if vertex.getZ() > furthest:
						furthest = vertex.getZ()
				else:
					if vertex.getZ() < furthest:
						furthest = vertex.getZ()
		return furthest

	def move(self, x, y, z):
		"""
		Moves the func_brush by the given amounts in Hammer units on x, y, and z planes

		:param x:
		:type x: :obj:`int` or :obj:`float`
		:param y:
		:type y: :obj:`int` or :obj:`float`
		:param z:
		:type z: :obj:`int` or :obj:`float`
		"""
		self.origin += Vertex(x,y,z)
		for solid in self.solids:
			solid.move(x,y,z)

class Connections(Common):
	NAME = "connections"

	def __init__(self, dic: dict = None):
		dic = self._dic(dic)

		self.other = dic
		self.export_list = []


class Cameras(Common):
	NAME = "cameras"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.activecamera = dic.pop("activecamera", -1)

		self.other = dic
		self.export_list = ["activecamera"]

		self.camera = []
		for child in children:
			self.camera.append(Camera(child.dic))

	def export_children(self):
		return (*self.camera,)


class Camera(Common):
	NAME = "camera"

	def __init__(self, dic: dict = None):
		dic = self._dic(dic)

		self.position = dic.pop("position", "[0 0 0]")
		self.look = dic.pop("look", "[0 0 0]")

		self.other = dic
		self.export_list = ["position", "look"]


class Cordons(Common):
	NAME = "cordons"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.active = dic.pop("active", 0)

		self.other = dic
		self.export_list = ["active"]

		self.cordon = []
		for child in children:
			self.cordon.append(Cordon(child.dic, child.children))

	def export_children(self):
		return (*self.cordon,)


class Cordon(Common):
	NAME = "cordon"

	def __init__(self, dic: dict = None, children: list = None):
		dic, children = self._dic_and_children(dic, children)

		self.name = dic.pop("name", "default")
		self.active = dic.pop("active", 1)

		self.other = dic
		self.export_list = ["name", "active"]

		self.box = []
		for child in children:
			self.box.append(Box(child.dic))

	def export_children(self):
		return (*self.box,)


class Box(Common):
	NAME = "box"

	def __init__(self, dic: dict = None):
		dic = self._dic(dic)

		mins = dic.pop("mins", "(0 0 0)")
		self.mins = Convert.string_to_vertex(mins)
		self.mins.normal = 2
		maxs = dic.pop("maxs", "(0 0 0)")
		self.maxs = Convert.string_to_vertex(maxs)
		self.maxs.normal = 2

		self.other = dic
		self.export_list = ["mins", "maxs"]


class SolidGenerator:
	"""
	Generates solids from scratch, remember you still need to add them to :class:`VMF` using :func:`~VMF.add_solids`
	"""

	@staticmethod
	def dev_material(solid: Solid, dev: int):
		"""
		Changes the material of the solid to single color dev textures, quick and useful when testing

		:param solid: The target solid
		:type solid: :class:`Solid`
		:param dev: The target texture between 1 and 5
		:type dev: :obj:`int`
		"""
		if dev == 1:
			solid.set_texture("tools/toolsorigin")
		elif dev == 2:
			solid.set_texture("tools/toolsinvisibleladder")
		elif dev == 3:
			solid.set_texture("tools/bullet_hit_marker")
		elif dev == 4:
			solid.set_texture("tools/toolsdotted")
		elif dev == 5:
			solid.set_texture("tools/toolsblack")

	@staticmethod
	def cube(vertex: Vertex, w, h, l, center=False, dev=0) -> Solid:
		"""
		Generates a solid cube

		:param vertex: Start position from which to build the cube
		:type vertex: :class:`Vertex`
		:param w: Width of the cube
		:type w: :obj:`int`
		:param h: Height of the cube
		:type h: :obj:`int`
		:param l: Length of the cube
		:type l: :obj:`int`
		:param center: If set to True centers the solid on the vertex
		:type center: :obj:`bool`
		:param dev: If set, changes the cube texture, see :func:`~SolidGenerator.dev_material`
		:type dev: :obj:`int`
		:return: A generated solid
		:rtype: :class:`Solid`
		"""
		x, y, z = vertex.export()
		f1 = Side(dic={"plane": f"({x + w} {y} {z + l}) ({x + w} {y} {z}) ({x} {y} {z})"})
		f2 = Side(dic={"plane": f"({x + w} {y + h} {z}) ({x + w} {y + h} {z + l}) ({x} {y + h} {z + l})"})
		f3 = Side(dic={"plane": f"({x} {y} {z}) ({x} {y + h} {z}) ({x} {y + h} {z + l})"})
		f4 = Side(dic={"plane": f"({x + w} {y + h} {z}) ({x + w} {y} {z}) ({x + w} {y} {z + l})"})
		f5 = Side(dic={"plane": f"({x} {y} {z + l}) ({x} {y + h} {z + l}) ({x + w} {y + h} {z + l})"})
		f6 = Side(dic={"plane": f"({x} {y + h} {z}) ({x} {y} {z}) ({x + w} {y} {z})"})

		solid = Solid()
		solid.add_sides(f1, f2, f3, f4, f5, f6)
		solid.editor = Editor()

		if center:
			solid.center = Vertex(x, y, z)

		SolidGenerator.dev_material(solid, dev)

		return solid

	@staticmethod
	def displacement_triangle(vertex: Vertex, w, h, l, dev=0) -> Solid:
		"""
		Generates a displacement triangle (L shaped viewed from above)

		:param vertex: Start position from which to build the triangle
		:type vertex: :class:`Vertex`
		:param w: Width of the triangle
		:type w: :obj:`int`
		:param h: Height of the triangle
		:type h: :obj:`int`
		:param l: Length of the triangle
		:type l: :obj:`int`
		:param dev: If set, changes the triangle texture, see :func:`~SolidGenerator.dev_material`
		:type dev: :obj:`int`
		:return: A generated triangle
		:rtype: :class:`Solid`
		"""
		x, y, z = vertex.export()
		f1 = Side(dic={"plane": f"({x} {y} {z}) ({x} {y + h} {z}) ({x} {y + h} {z + l})"})
		f2 = Side(dic={"plane": f"({x} {y + h} {z}) ({x} {y} {z}) ({x + w} {y} {z})"})
		f3 = Side(dic={"plane": f"({x} {y} {z + l}) ({x} {y + h} {z + l}) ({x + w} {y} {z + l})"})
		f4 = Side(dic={"plane": f"({x + w} {y} {z + l}) ({x + w} {y} {z}) ({x} {y} {z})"})
		f5 = Side(dic={"plane": f"({x} {y + h} {z + l}) ({x} {y + h} {z}) ({x + w} {y} {z})"})

		solid = Solid()
		solid.add_sides(f1, f2, f3, f4, f5)
		solid.editor = Editor()

		SolidGenerator.dev_material(solid, dev)

		return solid

	@staticmethod
	def room(vertex: Vertex, w, h, l, thick: int = 64, dev=0) -> List[Solid, Solid, Solid, Solid, Solid, Solid]:
		"""
		Generates a sealed cubed room

		:param vertex: Center position of the room
		:type vertex: :class:`Vertex`
		:param w: Width of the room
		:type w: :obj:`int`
		:param h: Height of the room
		:type h: :obj:`int`
		:param l: Length of the room
		:type l: :obj:`int`
		:param thick: The thickness of the walls
		:type thick: :obj:`int`
		:param dev: If set, changes the room texture, see :func:`~SolidGenerator.dev_material`
		:type dev: :obj:`int`
		:return: A generated room
		:rtype: :obj:`list` of :class:`Solid`
		"""
		s = []

		ww = w / 2
		hh = h / 2
		ll = l / 2
		tt = thick / 2

		v = vertex.copy()
		v.move(-ww - tt, 0, 0)
		s.append(SolidGenerator.cube(v, thick, h, l, True, dev))

		v = vertex.copy()
		v.move(ww + tt, 0, 0)
		s.append(SolidGenerator.cube(v, thick, h, l, True, dev))

		v = vertex.copy()
		v.move(0, -hh - tt, 0)
		s.append(SolidGenerator.cube(v, w, thick, l, True, dev))

		v = vertex.copy()
		v.move(0, hh + tt, 0)
		s.append(SolidGenerator.cube(v, w, thick, l, True, dev))

		v = vertex.copy()
		v.move(0, 0, -ll - tt)
		s.append(SolidGenerator.cube(v, w, h, thick, True, dev))

		v = vertex.copy()
		v.move(0, 0, ll + tt)
		s.append(SolidGenerator.cube(v, w, h, thick, True, dev))

		for solid in s:
			SolidGenerator.dev_material(solid, dev)
			for side in solid.get_sides():
				vertices = side.get_vertices()
				if vertices[0].getX() == vertices[1].getX() == vertices[2].getX():
					side.uaxis = Convert.string_to_uvaxis("[0 -1 0 0] 0.25")
					side.vaxis = Convert.string_to_uvaxis("[0 0 -1 0] 0.25")
				elif vertices[0].getY() == vertices[1].getY() == vertices[2].getY():
					side.uaxis = Convert.string_to_uvaxis("[1 0 0 0] 0.25")
					side.vaxis = Convert.string_to_uvaxis("[0 0 -1 0] 0.25")
				elif vertices[0].getZ() == vertices[1].getZ() == vertices[2].getZ():
					side.uaxis = Convert.string_to_uvaxis("[1 0 0 0] 0.25")
					side.vaxis = Convert.string_to_uvaxis("[0 -1 0 0] 0.25")

		return s

	@staticmethod
	def surf_ramp(vertex: Vertex, w, h, l, top_cut=32, side_cut=32, center=False, ramp_texture="cs_italy/cobble02",
				  top_texture="cs_italy/plasterwall02a", side_texture="cs_italy/plasterwall02a") -> Solid:
		"""
		Generates a ramp (triangle viewed from above: △)

		:param vertex: Start position from which to build the ramp (bottom middle of the ramp)
		:type vertex: :class:`Vertex`
		:param w: Width of the ramp
		:type w: :obj:`int`
		:param h: Height of the ramp
		:type h: :obj:`int`
		:param l: Length of the ramp
		:type l: :obj:`int`
		:param top_cut: Width of the cut at the top
		:type top_cut: :obj:`int`
		:param side_cut: Height of the cut on the side
		:type side_cut: :obj:`int`
		:param center: If set to True centers the ramp on the vertex
		:type center: :obj:`bool`
		:param ramp_texture:
		:type ramp_texture: :obj:`str`
		:param top_texture:
		:type top_texture: :obj:`str`
		:param side_texture:
		:type side_texture: :obj:`str`
		:return: A generated ramp
		:rtype: :class:`Solid`
		"""
		ww = w / 2
		hh = h
		ll = l / 2

		top_cut /= 2

		x, y, z = vertex.export()
		f1 = Side(dic={"plane": f"({x - ww} {y} {z}) ({x - w} {y + side_cut} {z}) ({x - top_cut} {y + hh} {z})"})
		f2 = Side(dic={"plane": f"({x - ww} {y + side_cut} {z - ll}) ({x - ww} {y} {z - ll}) ({x + ww} {y} {z - ll})"})
		f3 = Side(dic={"plane": f"({x - ww} {y} {z - ll}) ({x - ww} {y + side_cut} {z - ll}) "
								f"({x - ww} {y + side_cut} {z})"})
		f4 = Side(dic={"plane": f"({x + ww} {y + side_cut} {z - ll}) ({x + ww} {y} {z - ll}) ({x + ww} {y} {z})"})
		f5 = Side(dic={"plane": f"({x - top_cut} {y + hh} {z - ll}) ({x + top_cut} {y + hh} {z - ll}) "
								f"({x + top_cut} {y + hh} {z})"})
		f6 = Side(dic={"plane": f"({x + ww} {y} {z - ll}) ({x - ww} {y} {z - ll}) ({x - ww} {y} {z})"})
		f7 = Side(dic={"plane": f"({x - ww} {y + side_cut} {z - ll}) ({x - top_cut} {y + hh} {z - ll}) "
								f"({x - top_cut} {y + hh} {z})"})
		f8 = Side(dic={"plane": f"({x + top_cut} {y + hh} {z - ll}) ({x + ww} {y + side_cut} {z - ll}) "
								f"({x + ww} {y + side_cut} {z})"})

		solid = Solid()
		f3.set_texture(side_texture)
		f4.set_texture(side_texture)
		f5.set_texture(top_texture)
		f7.set_texture(ramp_texture)
		f8.set_texture(ramp_texture)

		if side_cut == 0 and top_cut == 0:
			solid.add_sides(f1, f2, f6, f7, f8)
		elif side_cut == 0:
			print("ss")
			solid.add_sides(f1, f2, f5, f6, f7, f8)
		elif top_cut == 0:
			solid.add_sides(f1, f2, f3, f4, f6, f7, f8)
		else:
			solid.add_sides(f1, f2, f3, f4, f5, f6, f7, f8)

		solid.editor = Editor()

		if center:
			solid.center = Vertex(x, y, z)

		return solid

class EntityGenerator:
	"""
	Generates entities from scratch, remember you still need to add them to :class:`VMF` using :func:`~VMF.add_entities`
	"""

	@staticmethod
	def light(origin: Vertex, color: Color, brightness: int = 200) -> Light:
		"""
		Generates a basic light

		:param origin: The position of the light in the world
		:type origin: :class:`Vertex`
		:param color: The color of the light
		:type color: :class:`Color`
		:param brightness: The brightness of the light
		:type brightness: :obj:`int`
		:return: A generated light
		:rtype: :class:`Light`
		"""
		l = Light({"classname": Light.SUBNAME})
		l.origin = origin
		l._light = ColorLight(*color.export(), brightness)

		l.editor = Editor()

		return l

	@staticmethod
	def prop_static(origin: Vertex, model: str, angle: Vertex = Vertex(),
					color: Color = Color(255, 255, 255), scale: int = 1) -> PropStatic:
		"""
		Generates a basic prop static

		:param origin: The position of the prop in the world
		:type origin: :class:`Vertex`
		:param model: The name of the prop (ex: models/penguin/penguin.mdl)
		:type model: :obj:`str`
		:param angle: The rotation of the prop in the world
		:type angle: :class:`Vertex`
		:param color: Color of the prop
		:type color: :class:`Color`
		:param scale: Size of the prop
		:type scale: :obj:`int`
		:return: A generated prop static
		:rtype: :class:`PropStatic`
		"""
		s = PropStatic({"classname": PropStatic.SUBNAME})
		s.origin = origin
		s.model = model
		s.angles = angle
		s.rendercolor = color
		s.uniformscale = scale

		s.editor = Editor()

		return s

	@staticmethod
	def info_decal(origin: Vertex, texture: str) -> InfoDecal:
		"""
		Generates a basic decal

		:param origin: The position of the decal in the world
		:type origin: :class:`Vertex`
		:param texture: The name of the texture (ex: "tools/toolsnodraw")
		:type texture: :obj:`str`
		:return: A generated decal
		:rtype: :class:`InfoDecal`
		"""
		s = InfoDecal({"classname": InfoDecal.SUBNAME})
		s.origin = origin
		s.texture = texture

		s.editor = Editor()

		return s

	@staticmethod
	def info_overlay(origin: Vertex, texture: str, angle: Vertex = Vertex(), *sides: Side) -> InfoOverlay:
		"""
		Generates a basic overlay

		:param origin: The position of the overlay in the world
		:type origin: :class:`Vertex`
		:param texture: The name of the texture (ex: "tools/toolsnodraw")
		:type texture: :obj:`str`
		:param angle: The rotation of the overlay in the world
		:type angle: :class:`Vertex`
		:return: A generated overlay
		:rtype: :class:`InfoOverlay`
		"""
		s = InfoOverlay({"classname": InfoOverlay.SUBNAME})
		s.origin = origin
		s.texture = texture
		s.angles = angle
		s.add_sides(*sides)

		s.editor = Editor()

		return s
	
	@staticmethod
	def sky_camera(origin: Vertex, angle: Vertex = Vertex()) -> SkyCamera:
		"""
		Generates a basic sky camera

		:param origin: The position of the camera in the world
		:type origin: :class:`Vertex`
		:param angle: The rotation of the camera in the world
		:type angle: :class:`Vertex`
		:return: A generated sky camera
		:rtype: :class:`SkyCamera`
		"""
		c = SkyCamera({"classname": SkyCamera.SUBNAME})
		c.origin = origin
		c.angles = angle

		c.editor = Editor()

		return c

class VMF:
	"""
	Equivalent to a single .VMF file, holds all categories and all sub-categories
	"""

	info_in_console = False  # Prints info like "VMF loaded", progress bar, etc...

	def __init__(self):
		# EXPORT VARIABLES
		self.__indent = 0  # Keeps track of indent
		self.__size = 0  # The approximate amount of solids (used for the progress bar)
		self.__count = 0  # Progress bar variable
		self.__file = None  # The output file

		# CATEGORIES
		self.versioninfo = None
		self.visgroups = VisGroups({},[]) #TODO test this
		self.viewsettings = None
		self.world = None
		self.entity = []
		self.hidden = []
		self.cameras = None
		self.cordons = None

		# OTHER VARIABLES
		self.file = None

	def getXExtremity(self, direction: bool, visgroupsToExclude=()):
		"""
		Get the furthest coordinate on the X-axis at which there is an object in the VMF
		True for the highest coordinate, False for the lowest coordinate
		visgroupsToExclude - a tuple of visgroup names to exclude in the calculation. Objects in these visgroups will be ignored
		If there are no objects in the VMF, returns 0
		NOTE: currently only checks solids, func_brushes, func_details, prop_statics, and sky_cameras
		"""
		#Make a list of vis_ids to exclude from the visgroup names given
		excluded_vis_ids = []
		for visgroup in self.visgroups.get_visgroups():
			for name in visgroupsToExclude:
				if visgroup.name == name:
					excluded_vis_ids.append(visgroup.visgroupid)

		furthest = 0 #Maintains the running "record" for the furthest X coordinate found
		for element in self.get_solids_and_entities(True):

			#Check if the element is in an excluded visgroup; if so, move on to next element
			exclude = False
			for vis_id in excluded_vis_ids:
				if element.editor.has_visgroup(vis_id):
					exclude = True
			if exclude:
				continue
			
			if isinstance(element,(PropStatic,SkyCamera)):
				if direction:
					if element.getOrigin().getX() > furthest:
						furthest = element.getOrigin().getX()
				else:
					if element.getOrigin().getX() < furthest:
							furthest = element.getOrigin().getX()
			elif isinstance(element,Solid):
				vertices = element.get_only_unique_vertices()
				for vertex in vertices:
					if direction:
						if vertex.getX() > furthest:
							furthest = vertex.getX()
					else:
						if vertex.getX() < furthest:
								furthest = vertex.getX()
			elif isinstance(element,(FuncDetail,FuncBrush)):
				if direction:
					if element.getXExtremity(True) > furthest:
						furthest = element.getXExtremity(True)
				else:
					if element.getXExtremity(False) < furthest:
						furthest = element.getXExtremity(False)
		return furthest

	def getYExtremity(self, direction: bool, visgroupsToExclude=()):
		"""
		Get the furthest coordinate on the Y-axis at which there is an object in the VMF
		True for the highest coordinate, False for the lowest coordinate
		visgroupsToExclude - a tuple of visgroup names to exclude in the calculation. Objects in these visgroups will be ignored
		If there are no objects in the VMF, returns 0
		NOTE: currently only checks solids, func_brushes, func_details, prop_statics, and sky_cameras
		"""
		#Make a list of vis_ids to exclude from the visgroup names given
		excluded_vis_ids = []
		for visgroup in self.visgroups.get_visgroups():
			for name in visgroupsToExclude:
				if visgroup.name == name:
					excluded_vis_ids.append(visgroup.visgroupid)

		furthest = 0 #Maintains the running "record" for the furthest Y coordinate found
		for element in self.get_solids_and_entities(True):

			#Check if the element is in an excluded visgroup; if so, move on to next element
			exclude = False
			for vis_id in excluded_vis_ids:
				if element.editor.has_visgroup(vis_id):
					exclude = True
			if exclude:
				continue

			if isinstance(element,(PropStatic,SkyCamera)):
				if direction:
					if element.getOrigin().getY() > furthest:
						furthest = element.getOrigin().getY()
				else:
					if element.getOrigin().getY() < furthest:
							furthest = element.getOrigin().getY()
			elif isinstance(element,Solid):
				vertices = element.get_only_unique_vertices()
				for vertex in vertices:
					if direction:
						if vertex.getY() > furthest:
							furthest = vertex.getY()
					else:
						if vertex.getY() < furthest:
								furthest = vertex.getY()
			elif isinstance(element,(FuncDetail,FuncBrush)):
				if direction:
					if element.getYExtremity(True) > furthest:
						furthest = element.getYExtremity(True)
				else:
					if element.getYExtremity(False) < furthest:
						furthest = element.getYExtremity(False)
		return furthest

	def getZExtremity(self, direction: bool, visgroupsToExclude=()):
		"""
		Get the furthest coordinate on the Z-axis at which there is an object in the VMF
		True for the highest coordinate, False for the lowest coordinate
		visgroupsToExclude - a tuple of visgroup names to exclude in the calculation. Objects in these visgroups will be ignored
		If there are no objects in the VMF, returns 0
		NOTE: currently only checks solids, func_brushes, func_details, prop_statics, and sky_cameras
		"""
		#Make a list of vis_ids to exclude from the visgroup names given
		excluded_vis_ids = []
		for visgroup in self.visgroups.get_visgroups():
			for name in visgroupsToExclude:
				if visgroup.name == name:
					excluded_vis_ids.append(visgroup.visgroupid)

		furthest = 0 #Maintains the running "record" for the furthest Z coordinate found
		for element in self.get_solids_and_entities(True): #TODO maybe turn True into an include_hidden kwarg

			#Check if the element is in an excluded visgroup; if so, move on to next element
			exclude = False
			for vis_id in excluded_vis_ids:
				if element.editor.has_visgroup(vis_id):
					exclude = True
			if exclude:
				continue

			if isinstance(element,(PropStatic,SkyCamera)):
				if direction:
					if element.getOrigin().getZ() > furthest:
						furthest = element.getOrigin().getZ()
				else:
					if element.getOrigin().getZ() < furthest:
							furthest = element.getOrigin().getZ()
			elif isinstance(element,Solid):
				vertices = element.get_only_unique_vertices()
				for vertex in vertices:
					if direction:
						if vertex.getZ() > furthest:
							furthest = vertex.getZ()
					else:
						if vertex.getZ() < furthest:
								furthest = vertex.getZ()
			elif isinstance(element,(FuncDetail,FuncBrush)):
				if direction:
					if element.getZExtremity(True) > furthest:
						furthest = element.getZExtremity(True)
				else:
					if element.getZExtremity(False) < furthest:
						furthest = element.getZExtremity(False)
		return furthest

	def get_solids(self, include_hidden=False, include_solid_entities=True, return_copies=False) -> List[Solid, ...]:
		"""
		Gets all the solids

		:param include_hidden: Whether to include quick hidden solids (Hammer "h" hotkey) or not
		:type include_hidden: :obj:`bool`
		:param include_solid_entities: Whether to include solid entities (ex: trigger_teleport) or not
		:type include_solid_entities: :obj:`bool`
		:param return_copies: Whether to return a list of copies of all the solids (true) or a list of the original solids (false)
		:type return_copies: :obj:`bool`
		:return: Solids in the VMF
		:rtype: :obj:`list` of :class:`Solid`
		"""
		li = []

		if return_copies:
			for s in self.world.solids:
				li.append(s.copy())
		else:
			li.extend(self.world.solids)

		if include_hidden:
			for s in self.world.hidden:
				if return_copies:
					li.append(s.solids.copy())
				else:
					li.append(s.solids)

		if include_solid_entities:
			for e in self.entity:
				for s in e.solids:
					if return_copies:
						li.append(s.copy())
					else:
						li.append(s)

		if include_hidden:
			for h in self.hidden:
				if h.entity is not None:
					for s in h.entity.solids:
						if return_copies:
							li.append(s.copy())
						else:
							li.append(s)

		return li

	def get_entities(self, include_hidden=False, include_solid_entities=False, return_copies=False) -> List[Entity, ...]:
		"""
		Gets all the entities

		:param include_hidden: Whether to include quick hidden solids (Hammer "h" hotkey) or not
		:type include_hidden: :obj:`bool`
		:param include_solid_entities: Whether to include solid entities (ex: trigger_teleport) or not
		:type include_solid_entities: :obj:`bool`
		:param return_copies: Whether to return a list of copies of all the entities (true) or a list of the original entities (false)
		:type return_copies: :obj:`bool`
		:return: Entities in the VMF
		:rtype: :obj:`list` of :class:`Entity`
		"""
		li = []
		if include_hidden:
			for h in self.hidden:
				if h.entity is not None:
					if not h.entity.solids or include_solid_entities:
						if return_copies:
							li.append(h.entity.copy())
						else:
							li.append(h.entity)

		for e in self.entity:
			if not e.solids or include_solid_entities:
				if return_copies:
					li.append(e.copy())
				else:
					li.append(e)

		return li

	def get_solids_and_entities(self, include_hidden=False, return_copies=False):
		"""
		Gets all the solids and entities

		:param include_hidden: Whether to include quick hidden solids (Hammer "h" hotkey) or not
		:type include_hidden: :obj:`bool`
		:return: Solids and entities in the VMF
		:rtype: :obj:`list` of (:class:`Entity` or :class:`Solid`)
		"""
		return self.get_solids(include_hidden, False, return_copies) + self.get_entities(include_hidden, True, return_copies)

	def get_all_from_visgroup(self, name: str, include_hidden=False, return_copies=False):
		"""
		Gets everything from the visgroup

		:param name: Name of the visgroup
		:type name: :obj:`str`
		:return: Solids and entities in the visgroup
		:rtype: :obj:`list` of (:class:`Entity` or :class:`Solid`)
		"""
		v_id = None
		li = []
		for visgroup in self.visgroups.get_visgroups():
			if visgroup.name == name:
				v_id = visgroup.visgroupid

		if v_id is not None:
			for item in self.get_solids_and_entities(include_hidden, return_copies):
				if item.editor.has_visgroup(v_id):
					li.append(item)

		return li

	def get_group_center(self, group: list, geo=False) -> Vertex:
		"""
		Gets a vertex based on the average center of all the solids

		:param group: All the solids to include
		:type group: :obj:`list` of :class:`Solid`
		:param geo: Whether to use the geometric center or not, see :func:`~Solid.center` and :func:`~Solid.center_geo`
		:return: The average center position of all the solids
		:rtype: :class:`Vertex`
		"""
		v = Vertex()
		for solid in group:
			if geo:
				v = v + solid.center_geo
			else:
				v = v + solid.center
		v.divide(len(group))
		return v

	def sort_by_attribute(self, category_list: list, attr: str):
		"""
		Sorts the list based on one of their attributes

		:param category_list: All the elements to sort
		:type category_list: :obj:`list`
		:param attr: The attribute to sort by, for example `center_geo.x` for :class:`Solid`
		:return: The elements sorted in increasing order
		:rtype: :obj:`list`
		"""
		return sorted(category_list, key=operator.attrgetter(attr))

	def add_to_visgroup(self, name: str, *args):
		"""
		Adds the given elements to a visgroup, if it doesn't exist one is created

		:param name: Name of the visgroup
		:type name: :obj:`str`
		:param args: Elements to add to the visgroup
		"""
		v_id = None
		for visgroup in self.visgroups.get_visgroups():
			if visgroup.name == name:
				v_id = visgroup.visgroupid

		if v_id is None:
			v_id = self.visgroups.new_visgroup(name).visgroupid

		for item in args:
			item.editor.add_visgroup(v_id)

	def remove_all_from_visgroup(self, name: str):
		"""
		Removes all elements from the given visgroup
		Elements are not deleted, just removed from the visgroup

		:param name: Name of the visgroup
		:type name: :obj:`str`
		"""
		v_id = None
		for visgroup in self.visgroups.get_visgroups():
			if visgroup.name == name:
				v_id = visgroup.visgroupid

		if v_id is not None:
			for item in self.get_all_from_visgroup(name,True):
				item.editor.remove_visgroup(v_id)

	def delete_visgroup_contents(self, name: str):
		"""
		Deletes all contents of the given visgroup, regardless of whether hidden or not

		:param name: Name of the visgroup
		:type name: :obj:`str`
		"""
		self.delete_elements(*self.get_all_from_visgroup(name,True))

	def add_solids(self, *args: Solid):
		"""
		Adds solids to the world

		:param args: Solids to add
		"""
		self.world.solids.extend(args)

	def add_entities(self, *args: Entity):
		"""
		Adds entities to the entity list

		:param args: Entities to add
		"""
		self.entity.extend(args)

	def delete_elements(self, *args):
		"""
		Deletes all given elements (solids or entities) from the world, regardless of whether hidden or not

		:param args: Elements to delete
		"""
		for element in args:
			if element in self.world.solids:
				self.world.solids.remove(element)
				continue
			elif element in self.entity:
				self.entity.remove(element)
				continue
			for h in self.hidden: #All of these should be entities
				if h.entity is element:
					h.entity = None
					break
			for h in self.world.hidden: #All of these should be solids
				if h.solids is element: #"solids" should actually just a single Solid instance, but don't want to rename it in the Hidden class right now TODO
					h.solids = None

		#TODO get rid of this
		'''
		#self.world.solids = list(set(self.world.solids) - set(args))
		#self.entity = list(set(self.entity) - set(args))
		#self.world.hidden = list(set(self.world.solids) - set(args))
		#removeHidden = []
		for h in self.hidden:
			if h.entity in args:
				removeHidden.append(h)
				continue
			for solid in h.solids:
				if solid in args:
					removeHidden.append(h)
					break
		self.hidden = list(set(self.hidden) - set(removeHidden))
		'''


	def add_section(self, section: TempCategory):
		"""
		Adds temporary categories to the VMF, used when reading .VMF files, you shouldn't need to use this

		:param section: The temporary category to add
		:type section: :class:`importer.TempCategory`
		"""
		name = str(section)
		dic = section.dic
		children = section.children

		if name == VersionInfo.NAME:
			self.versioninfo = VersionInfo(dic)

		elif name == VisGroups.NAME:
			self.visgroups = VisGroups(dic, children)

		elif name == ViewSettings.NAME:
			self.viewsettings = ViewSettings(dic)

		elif name == World.NAME:
			self.world = World(dic, children)

		elif name == Entity.NAME:
			classname = dic["classname"]
			if classname == Light.SUBNAME:
				e = Light(dic, children)
			elif classname == PropStatic.SUBNAME:
				e = PropStatic(dic, children)
			elif classname == PropDynamic.SUBNAME:
				e = PropDynamic(dic, children)
			elif classname == SkyCamera.SUBNAME:
				e = SkyCamera(dic, children)
			elif classname == EnvFogController.SUBNAME:
				e = EnvFogController(dic, children)
			elif classname == FuncDetail.SUBNAME:
				e = FuncDetail(dic, children)
			elif classname == FuncBrush.SUBNAME:
				e = FuncBrush(dic, children)
			else:
				e = Entity(dic, children)
			self.entity.append(e)

		elif name == Hidden.NAME:
			self.hidden.append(Hidden(dic, children))

		elif name == Cameras.NAME:
			self.cameras = Cameras(dic, children)

		elif name == Cordons.NAME:
			self.cordons = Cordons(dic, children)

	def mark_vertex(self, vertex: Vertex, size: int = 32, dev: int = 1, visgroup: str = None):
		"""
		Quickly adds a solid cube at the given vertex, useful for debugging

		:param vertex: The position on which the cube is centered on
		:type vertex: :class:`Vertex`
		:param size: The size of the cube
		:type size: :obj:`int`
		:param dev: The texture given to the cube, see :func:`~SolidGenerator.dev_material`
		:type dev: :obj:`int`
		:param visgroup: Optionally adding the cube to an existing visgroup
		:type visgroup: :obj:`None` or :obj:`str`
		"""
		s = SolidGenerator.cube(vertex, size, size, size, True, dev)
		if visgroup is not None:
			self.add_to_visgroup(visgroup, s)
		self.add_solids(s)

	def blank_vmf(self):
		"""
		Generates necessary categories (overwriting existing), use :func:`~new_vmf` to generate the VMF itself
		"""
		self.versioninfo = VersionInfo()
		self.visgroups = VisGroups()
		self.viewsettings = ViewSettings()
		self.world = World()
		self.cameras = Cameras()
		self.cordons = Cordons()

	def export(self, filename: str):
		"""
		Exports the VMF to a .VMF file

		:param filename: Exported file name, use a different filename or it will overwrite the existing file
		:type filename: :obj:`str`
		"""
		self.__indent = 1  # Represents the indent of the data and not the categories (which use indent-1)

		start_time = time.time()  # To get how long the export took

		if VMF.info_in_console:
			print("Exporting VMF")

			for item in (self.versioninfo, self.visgroups, self.viewsettings, self.world,
						 *self.entity, *self.hidden, self.cameras, self.cordons):

				self._get_export_size(item)  # Gets the total amount of children

			if self.__size == 0:  # We want to avoid division by 0 in progress bar
				self.__size += 1

		# I initially wrote everything to a string, which I then added to the file, turns out writing directly to the
		# file is much faster by a long shot (the biggest file ~31mb takes about 8 seconds, before it took over 5 mins)
		with open(filename, "w+") as self.file:
			for item in (self.versioninfo, self.visgroups, self.viewsettings, self.world,
						 *self.entity, *self.hidden, self.cameras, self.cordons):
				self._nest_export(item)

		if VMF.info_in_console:
			print(f"Done in {round(time.time() - start_time, 3)} seconds")

	def _nest_export(self, category):

		#Determine which export "mode" to use (either CSGO or TF2) depending on editor version
		#The only real purpose of this is to avoid exporting entity attributes that don't exist in the Hammer build the map was created in
		#i.e. if the map was created in TF2, we don't want to export stuff like "preventpropcombine" for prop_statics since TF2 doesn't have prop combine
		#So really you can export any VMF in any export "mode"; just be warned that exporting a VMF from an older Hammer build (e.g. TF2) using a newer export mode (e.g. CSGO) will populate all your entities with a bunch of excess junk that you'll have to manually delete
		#As far as I can tell, version #7937 corresponds to TF2's most recent Hammer build
		#So for our purposes, we'll just assume that anything with a version <= 7937 is TF2, and anything greater is CSGO
		#Nevermind, just ran TF2 hammer on another computer and apparently its editorbuild is 8610, so there is literally no way to definitively distinguish VMF types by game
		#Why Valve
		#Just going to leave this here for now though
		if self.versioninfo.editorbuild <= 7950:
			export_mode = "TF2"
		else:
			export_mode = "CSGO"

		if VMF.info_in_console:
			self._progress()  # Progress bar
		if category is not None:  # Some classes export None (ex: Hidden class export_children function)
			# In the VMF it's first information (ex: id, classname, etc...) then children (ex: side, editor, etc...)
			# I don't know if it's necessary but it makes comparing the exported map to the original much easier
			# This is why I've chosen to keep the same order as the hammer generated VMF for pretty much everything
			self._format_converter(category.NAME, category.export(export_mode))

			for child in category.export_children():
				self.__count += 1  # For the progress bar
				self.__indent += 1
				self._nest_export(child)  # Recursion
				self.__indent -= 1

			# When there aren't any more children we close the curly brackets
			self.file.write("\t" * (self.__indent - 1) + "}\n")

	def _get_export_size(self, category):  # Same concept as _nest_export just without writing to file
		if category is not None:
			for child in category.export_children():
				self.__size += 1
				self._get_export_size(child)

	def _progress(self, suffix=''):  # Some progress bar I found on StackOverflow
		bar_len = 60
		filled_len = int(round(bar_len * self.__count / float(self.__size)))

		percents = round(100.0 * self.__count / float(self.__size), 1)
		bar = '=' * filled_len + '-' * (bar_len - filled_len)

		sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
		sys.stdout.flush()

	def _format_converter(self, name, info_list):
		# The category name is always one less indent from the data/children, and since self.indent keeps track of the
		# data indent and not the category indent (doesn't matter which one you track as long as it's always the same)
		t = "\t" * (self.__indent - 1)
		self.file.write(f"{t}{name}\n{t}{{\n")
		t += "\t"

		for item in info_list:
			if not item:
				continue

			if type(item) is dict:
				for i, j in item.items():
					if type(j) is list: #The only things that should ever trigger this are "visgroupid"s and "groupid"s, the only attributes that Valve decided had to be stored on multiple lines instead of on a single line, like info_overlay brush faces. As a result, we have to parse visgroupid and groupid as a key + list pair instead of a simple key + value pair
						for k in j:
							self.file.write(f"{t}\"{i}\" \"{str(k)}\"\n")
					else:
						self.file.write(f"{t}\"{i}\" \"{str(j)}\"\n")
			else:
				self.file.write(f"{t}\"{item[0]}\" \"{str(item[1])}\"\n")


def load_vmf(name: str, merge_vertices=0.0001) -> VMF:
	"""
	Loads a .VMF file

	:param name: The OS file to open, path needs to be included
	:type name: :obj:`str`
	:param merge_vertices: Vertices on a solid within this distance are merged into a single vertex class, set to 0 for no merging
	:type merge_vertices: :obj:`int` or :obj:`float`
	:return: A loaded VMF
	:rtype: :class:`VMF`
	"""
	try:
		if VMF.info_in_console:
			print("Loading VMF")

		v = VMF()
		f = file_parser(name)

		for section in f:
			v.add_section(section)

		if merge_vertices != 0:
			for solid in v.get_solids(True):
				solid.link_vertices(merge_vertices)

		if VMF.info_in_console:
			print("VMF Loaded")
			print("------------------------------")
		return v
	except Exception as e:
		raise e


def new_vmf() -> VMF:
	"""
	Generates a VMF with the necessary classes

	:return: A blank VMF
	:rtype: :class:`VMF`
	"""
	v = VMF()
	v.blank_vmf()
	return v

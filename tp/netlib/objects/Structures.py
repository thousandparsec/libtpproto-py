from types import *

import xstruct

class Structure(object):
	"""\
	This is the base class for all structures. Structures are a special type of
python property which is designed to be serialised into a binary value by the
xstruct library.

	The property protects itself from being assigned values which can not be
serialised properly (for example a string in an integer structure). This means
errors are caught at the time the assignment occurs rather then when
serialisation actually occurs (which could be in a totally different section of
code).  

	Structures also have things like a name, description and other properties
which making them even more self documenting (over normal Python code).

	"""

	def __init__(self, name=None, longname="", description="", example="", **kw):
		if name is None:
			raise ValueError("Name did not exist!")
		
		self.name = name
		self.longname = longname
		self.description = description
		self.example = example
	
	def check(self, value):
		"""\
		check(value) -> None

		This function will check if an argument is valid for this structure.
		If the argument is not valid it should throw a ValueError exception.
		"""
		raise SyntaxError("Not Implemented")

	def length(self, value):
		"""\
		length(value) -> int

		This function will return the length (number of bytes) of the encoded
		version of the value.
		"""
		raise SyntaxError("Not Implemented")

	@property
	def xstruct(self):
		"""\
		xstruct() -> string

		Returns the xstruct value for this structure.
		"""
		raise SyntaxError("Not Implemented")

	def pack(self, values):
		"""\
		pack() -> bytes

		Returns a packed version of values.
		"""
		return xstruct.pack(self.xstruct, values)		

	def unpack(self, s):
		"""
		unpack() -> values, leftover
		
		Returns the unpacked values and any data that is left over.
		"""
		a, s = xstruct.unpack(self.xstruct, s)
		if len(a) != 1:
			raise TypeError("WTF?")
		return a[0], s

	def __str__(self):
		return "<%s %s %s>" % (self.__class__.__name__.split('.')[-1], hex(id(self)), self.name)
	__repr__ = __str__

	def __set__(self, obj, value):
		self.check(value)
		setattr(obj, "__"+self.name, value)

	def __get__(self, obj, objcls):
		try:
			return getattr(obj, "__"+self.name)
		except AttributeError, e:
			raise ValueError("No value defined for %s" % self.name)

	def __delete__(self, obj):
		delattr(obj, "__"+self.name)

	def protect(self, value):
		return value

class StringStructure(Structure):
	"""\
	String structures can contain any arbitrary length UTF-8 string. 

	They are encoded in the form of <integer><bytes> where integer indicates
	the number of bytes the string takes up.
	"""
	def check(self, value):
		if not isinstance(value, StringTypes):
			raise ValueError("Value must be a string type")

	def length(self, value):
		return 4+len(value)

	xstruct = 'S'

class CharacterStructure(StringStructure):
	"""\
	Character structures are kind of like string structures but they are a
	constant length.

	As they are always of a known length, there is no need for a length
	indicated.

	"""
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			self.size = kw['size']
		else:
			self.size = 1
	
	def check(self, value):
		StringStructure.check(self, value)
		if len(value) != self.size:
			raise ValueError("Value is not the correct size! Must be length %i" % self.size)
			
	def length(self, value):
		return self.size

	@property	
	def xstruct(self):
		if self.size == 1:
			return 'c'
		return str(self.size)+'s'

class IntegerStructure(Structure):
	"""\
	Integer structure store a binary number. These numbers have various lengths
	and can be of three types.  

		* An unsigned number can only store positive values.
		* A signed number can store negative and positive values.
		* A semisigned number can store positive values and negative one.
	
	How big or small the integer can store depends on both the type and the
	number of bits being used.  
	"""

	sizes = {
		8: ('b', 'B', None), 
		16: ('h', 'H', 'n'),
		32: ('i', 'I', 'j'),
		64: ('q', 'Q', 'p'),
	}
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 32
		
		if kw.has_key('type'):
			type = kw['type']
		else:
			type = 'signed'
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size

		if not type in ("signed", "unsigned", "semisigned"):
			raise ValueError("Type can only be signed, unsigned or semisigned")
		self.type = type

	def check(self, value):
		if not isinstance(value, (IntType, LongType)):
			raise ValueError("Value must be a number, not %s" % repr(value))

		# Do a bounds check now
		if self.type == "signed":
			max = 2**(self.size-1)-1
			min = -2**(self.size-1)
		elif self.type == "unsigned":
			max = 2**self.size-1
			min = 0
		elif self.type == "semisigned":
			max = 2**self.size-2
			min = -1

		if value < min:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if value > max:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
			
	def length(self, value):
		return self.size / 8
	
	@property
	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif type == "semesigned":
			xstruct = self.sizes[self.size][2]
		return xstruct

import time
from datetime import datetime
class DateTimeStructure(Structure):
	sizes = {
		32: ('t'),
		64: ('T'),
	}

	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)
		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 64
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size
	
	def check(self, value):
		if not isinstance(value, datetime):
			raise ValueError("Value must be a datetime")

		i = time.mktime(value.timetuple())
		if i < 0:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if i > 2**self.size-1:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
	
	def length(self, value):
		return self.size / 8
	
	@property
	def xstruct(self):
		xstruct = self.sizes[self.size][0]

class EnumerationStructure(IntegerStructure):
	"""\
	Enumeration structures are exactly like integer structures but each
	value has an associated "name". This is an efficient way to encode a list
	of known values.
	"""

	def __init__(self, *args, **kw):
		IntegerStructure.__init__(self, *args, **kw)

		if kw.has_key('values'):
			values = kw['values']

			for id, name in self.values.items():
				try:
					IntegerStructure.check(self, id)
				except ValueError, e:
					raise ValueError("Id's %i doesn't meet the requirements %s" % (type(id), e))

				if not isinstance(value, StringTypes):
					raise ValueError("Name of %i must be a string!" % id)
		
	def check(self, value):
		if isinstance(value, (IntType, LongType)):
			if value in self.values.keys():
				return	

		if isinstance(value, StringTypes):
			if value in self.values.values():
				return	

		raise ValueError("Value must be a number")

	def length(self, value):
		return self.size / 8

	@property
	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif type == "semesigned":
			xstruct = self.sizes[self.size][2]
		return xstruct

class GroupStructure(Structure):
	"""\
	A group structure is a fixed length structure which contains a bunch of
	other structures. 
	
	The group structure has no actual space or encoding, it is just a container
	which allows logical grouping of other structures for access.

	It is also the convenient base for the ListStructure.
	"""

	class GroupProxy(list):
		"""\
		The group proxy is a little helper class which makes does a number of
		things. The most important being checking assignments to the group
		items.

		It also maps attributes names to the list indexes so that the groups
		elements can be accessed by their names.
		"""

		__sentinal = []
		#__slots__ = ["structures"]

		def __init__(self, structures, items):
			self.structures = structures
			list.__init__(self, [self.__sentinal]*len(self.structures))
			for i, item in enumerate(items):
				self[i] = item

		def __getitem__(self, x):
			v = list.__getitem__(self, x)
			if v is self.__sentinal:
				raise ValueError("The value is currently unset.")
			return v

		def __setitem__(self, key, item):
			if key > len(self.structures):
				raise ValueError("%s is too big!" % key)

			self.structures[key].check(item)
			list.__setitem__(self, key, self.structures[key].protect(item))

		def __setslice__(self, i, j, y):
			for x, v in zip(range(i, j), y):
				self[x] = v

		def __delitem__(self, i):
			self[i] = self.__sentinal

		def __delslice__(self, i, j):
			for x in range(i, j):
				del self[x]	

		def indexof(self, name):
			for i, structure in enumerate(self.structures):
				if structure.name.split('_')[-1] == name:
					return i
			raise AttributeError("No such attribute - %r" % name)

		def __getattr__(self, name):
			if name in ("structures",):
				return object.__getattr__(self, name)
			return self[self.indexof(name)]

		def __setattr__(self, name, value):
			if name in ("structures",):
				return object.__setattr__(self, name, value)
			self[self.indexof(name)] = value

		def __delattr__(self, name):
			del self[self.indexof(name)]

		def append(self, *args):
			raise AttributeError("Can not change the size of this structure")
		def pop(self, *args):
			raise AttributeError("Can not change the size of this structure")
		def extend(self, *args):
			raise AttributeError("Can not change the size of this structure")
		def insert(self, *args):
			raise AttributeError("Can not change the size of this structure")
		def remove(self, *args):	
			raise AttributeError("Can not change the size of this structure")
		def sort(self, *args):
			raise AttributeError("Can not change the order of this structure")

		def __repr__(self):
			s = []
			for structure, i in zip(self.structures, self):
				if len(structure.xstruct) > 0:
					x = "(%s)" % structure.xstruct
				else:
					x = ""
				s.append('%s%s: %r' % (structure.name, x, i))
			s = "[" + ", ".join(s) + "]"
			return s
		__str__ = __repr__
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('structures'):
			structures = kw['structures']
		else:
			structures = []
		
		if not isinstance(structures, (TupleType, ListType)):
			raise ValueError("Argument must be a list or tuple")

		self.structures = []
		for structure in structures:
			if not isinstance(structure, Structure):
				raise ValueError("All values in the list must be structures!")
			self.structures.append(structure)

	def check(self, values):
		if not isinstance(values, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
	
		if len(values) != len(self.structures):
			raise ValueError("Value is not the correct size, was %i must be %i" % (len(values), len(self.structures)))

		for value, structure in zip(values, self.structures):
			structure.check(value)

	def length(self, values):
		length = 0
		for value, structure in zip(values, self.structures):
			length += structure.length(value)
		return length

	@property
	def xstruct(self):
		return ''

	def pack(self, values):
		s = []
		for value, structure in zip(values, self.structures):
			s.append(structure.pack(value))
		return "".join(s)

	def unpack(self, leftover):
		v = []
		for structure in self.structures:
			r, leftover = structure.unpack(leftover)
			v.append(r)
		return v, leftover

	def __set__(self, obj, values):
		self.check(values)
		Structure.__set__(self, obj, self.protect(values))

	def protect(self, value):
		return GroupStructure.GroupProxy(self.structures, value)

GroupProxy = GroupStructure.GroupProxy

class ListStructure(GroupStructure):
	"""\
	The list structure is a Group Structure which can be repeated a number of
	times. 
	"""

	class ListProxy(list):
		"""\
		ListProxy is a little helper class which makes allows the multiple
		items to be assigned to the structure.

		It uses the GroupProxy to protect each individual item.
		"""

		def __init__(self, structures, listbase):
			list.__init__(self, listbase)
			self.structures = structures

		def __setitem__(self, key, item):
			if len(self.structures) != 1:
				if not isinstance(item, (TupleType, ListType)):
					raise ValueError("Value items must be a list or tuple not %r" % type(item))

				if len(item) != len(self.structures):
					raise ValueError("Value item was not the correct size (was %i must be %i)" % (len(item), len(self.structures)))
			
				for i in xrange(0, len(self.structures)):
					self.structures[i].check(item[i])
			else:
				self.structures[0].check(item)
			list.__setitem__(self, key, item)

		def __getitem__(self, key):
			return GroupStructure.GroupProxy(self.structures, list.__getitem__(self, key))

	def check(self, list):
		if not isinstance(list, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
	
		for item in list:
			if len(self.structures) != 1:
				if not isinstance(item, (TupleType, ListType)):
					raise ValueError("Value items must be a list or tuple not %r" % type(item))

				if len(item) != len(self.structures):
					raise ValueError("Value item was not the correct size (was %i must be %i)" % (len(item), len(self.structures)))
			
				for i in xrange(0, len(self.structures)):
					self.structures[i].check(item[i])
			else:
				self.structures[0].check(item)
	
	def protect(self, value):
		return ListStructure.ListProxy(self.structures, value)

	def length(self, list):
		length = 4
		for item in list:
			if len(self.structures) != 1:
				for i in xrange(0, len(self.structures)):
					length += self.structures[i].length(item[i])
			else:
				length += self.structures[0].length(item)
		return length

	@property
	def xstruct(self):
		xstruct = "["
		for struct in self.structures:
			xstruct += struct.xstruct
		return xstruct+"]"

	def pack(self, values):
		return xstruct.pack(self.xstruct, values)

	def unpack(self, s):
		a, s = xstruct.unpack(self.xstruct, s)
		if len(a) != 1:
			raise TypeError("WTF?")
		return a[0], s

ListProxy = ListStructure.ListProxy

__all__ = ["StringStructure", "CharacterStructure", "IntegerStructure", "DateTimeStructure", "GroupStructure", "ListStructure"]

if __name__ == "__main__":

	class Test(object):
		test = StringStructure("test")

		pos = GroupStructure("pos", structures=[IntegerStructure("x"), IntegerStructure("y")])

		list = ListStructure("list", structures=[IntegerStructure("x")])
		list2 = ListStructure("list2", structures=[IntegerStructure("x"), IntegerStructure("y")])

	t = Test()

	t.test = "Testing"
	print t.test
	del t.test
	try:
		print t.test
		assert False
	except ValueError, e:
		print e
	try:
		t.test = 12
		assert False
	except ValueError, e:
		print e

	t.test = "test"
	print t.test

	t.pos = [10, 11]
	assert t.pos == [10, 11]
	assert t.pos[0] == 10
	assert t.pos[1] == 11
	assert t.pos.x == 10
	assert t.pos.y == 11

	t.pos.x = 12
	assert t.pos == [12, 11]
	assert t.pos[0] == 12
	assert t.pos[1] == 11
	assert t.pos.x == 12
	assert t.pos.y == 11

	t.pos.y = 13
	assert t.pos == [12, 13]
	assert t.pos[0] == 12
	assert t.pos[1] == 13
	assert t.pos.x == 12
	assert t.pos.y == 13

	t.list = [1, 2, 3]

	for i in t.list:
		print i

	try:
		t.list[0] = 'test'
		assert False, "Was able to assign the wrong type"
	except ValueError, e:
		print e

	t.list2 = [[1,2], [2,3], [3,4]]
	for i in t.list2:
		print i

	try:
		t.list2[0] = 1
		assert False, "Was able to assign a single value!" 
	except ValueError, e:
		print e

	try:
		t.list2[0] = (2,3,4)
		assert False, "Was able to assign wrong length value!" 
	except ValueError, e:
		print e

	try:
		t.list2[0] = (1, "test")
		assert False, "Was able to assign wrong type!" 
	except ValueError, e:
		print e

	try:
		t.list2[0][1] = "test"
		print t.list2[0][1]
		assert False, "Was able to assign wrong type!"
	except ValueError, e:
		print e

	print t.list2[0].x
	

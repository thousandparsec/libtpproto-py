
from xstruct import pack

from Description import Description
from constants import *

# Import prebuild orders
from ObjectDesc import *
_descriptions = None
def descriptions(added=None):
	global _descriptions
 
	if _descriptions == None:
		try:
			_descriptions = import_subtype(edir(__file__), py2exe=__loader__)
		except NameError:
			try:
				import sys
				sys.frozen
				import carchive
				this = carchive.CArchive(sys.executable).openEmbeddedZlib("out1.pyz")
				_descriptions = import_subtype("tp.netlib.objects.OrderExtra", installer=this.contents())
			except NameError:
				_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
		return _descriptions

struct_map = {
	ARG_ABS_COORD:	("qqq",			3),
	ARG_TIME: 		("I",			1),
	ARG_OBJECT:		("I",			1),
	ARG_PLAYER:		("II",			2),
	ARG_REL_COORD:	("Iqqq",		3),
	ARG_RANGE:		("iiii",		4),
	ARG_LIST:		("[ISI][II]", 	2),
	ARG_STRING:		("IS",		 	2),
}

class ClassNicePrint(type):
	def __str__(self):
		return "<dynamic-class '%s' at %s>" % (self.name, hex(id(self)))
	__repr__ = __str__

from Header import Header
from Order import Order
class DynamicBaseOrder(Order):
	"""\
	An Order Type built by a OrderDesc.
	"""
	substruct = ""
	subtype = -1
	name = "Base"

	__metaclass__ = ClassNicePrint

	def __init__(self, sequence, \
			id, type, slot, turns, resources, \
			*args):
		Order.__init__(self, sequence, \
			id, type, slot, turns, resources)

		# Figure out if we are in single or multiple mode
		short = len(args) == len(self.names)

		for name, type in self.names:
			struct, size = struct_map[type]

			if short:
				size = 1

			if size == 1:
				setattr(self, name, args[0])
			else:
				if len(args) < size:
					raise ValueError("Incorrect number of arguments")
				setattr(self, name, args[0:size])

			args = args[size:]
	
			# FIXME: Need to figure out a better way to do this...
			if type in (ARG_TIME, ARG_OBJECT):
				if getattr(self, name) == 4294967295:
					setattr(self, name, -1)

		# FIXME: Need to figure out the length a better way
		self.length = len(self.__repr__()) - Header.size

	def __repr__(self):
		args = []
		for name, type in self.names:
			struct, size = struct_map[type]
			
			attr = getattr(self, name)
			if size == 1:
				args.append(attr)
			else:
				args = args + list(attr)

		output = Order.__repr__(self)
		output += apply(pack, [self.substruct,] + args)
		return output

	def __str__(self):
		return "<netlib.objects.OrderExtra.DynamicOrder - %s @ %s>" % (self.name, hex(id(self)))

class OrderDesc(Description):
	"""\
	The OrderDesc packet consists of:
		* a UInt32, order type
		* a String, name
		* a String, description
		* a list of
			* a String, argument name
			* a UInt32, argument type
			* a String, description
		* a UInt64, the last time the description was modified

	IE
	ID: 1001
	Name: Drink With Friends
	Description: Go to the pub and drink with friends.
	Arguments:
		Name: How Long
		Type: ARG_TIME
		Description: How many turns to drink for.

		Name: Who With
		Type: ARG_PLAYER
		Description: Which player to drink with.

		Name: Where
		Type: ARG_COORD
		Description: Where to go drinking.

		Name: Cargo
		Type: ARG_INT
		Description: How much beer to drink.
	"""
	no = 9
	struct="I SS [SIS] Q"

	def __init__(self, sequence, \
			id, name, description, \
			arguments, modify_time):
		Description.__init__(self, sequence, id)

		self.name = name
		self.description = description
		self.arguments = arguments
		self.modify_time = modify_time

		self.length = 4 + \
			4 + len(name) + 1 + \
			4 + len(description) + 1 + \
			4 + 8 

		for argument in arguments:
			self.length += \
				4 + len(argument[0]) + 1 + \
				4 + \
				4 + len(argument[2]) + 1

	def __repr__(self):
		output = Description.__repr__(self)
		output += pack(self.struct, \
				self.id, \
				self.name, \
				self.description, \
				self.arguments, \
				self.modify_time)

		return output

	def build(self):
		"""\
		*Internal*

		Builds a class from this description.
		"""
		class DynamicOrder(DynamicBaseOrder):
			pass

		DynamicOrder.name = self.name
		DynamicOrder.doc = self.description

		# Arguments
		DynamicOrder.names = []
		DynamicOrder.subtype = self.id
	
		for name, type, desc in self.arguments:
			struct, size = struct_map[type]

 			DynamicOrder.names.append((name, type))
			DynamicOrder.substruct += struct
			setattr(DynamicOrder, name + "__doc__", desc)

		DynamicOrder.modify_time = self.modify_time

		return DynamicOrder

	def register(self):
		descriptions(self.build())
		
__all__ = ["descriptions", "OrderDesc"]


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
		except NameError, e:
			try:
				import sys
				if sys.frozen == "macosx_app":
					raise AttributeError("macosx_app")
				print sys.frozen
				import carchive
				this = carchive.CArchive(sys.executable).openEmbeddedZlib("out1.pyz")
				_descriptions = import_subtype("tp.netlib.objects.OrderExtra", installer=this.contents())
			except AttributeError, e:
				_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
	
	return _descriptions

ARG_STRUCTMAP = {
	ARG_ABS_COORD:	("qqq",			3),
	ARG_TIME: 		("Ij",			2),
	ARG_OBJECT:		("I",			1),
	ARG_PLAYER:		("II",			2),
	ARG_REL_COORD:	("Iqqq",		3),
	ARG_RANGE:		("iiii",		4),
	ARG_LIST:		("[ISj][II]", 	2),
	ARG_STRING:		("IS",		 	2),
}

class ClassNicePrint(type):
	def __str__(self):
		return "<dynamic-class '%s' (%s) at %s>" % (self._name, self.subtype, hex(id(self)))
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

	ARG_STRUCTMAP = ARG_STRUCTMAP
	ARG_NAMEMAP   = ARG_NAMEMAP

	def __init__(self, sequence, id, slot, subtype, turns, resources, *args, **kw):
		Order.__init__(self, sequence, id, slot, subtype, turns, resources)

		assert subtype == self.subtype, "Type %s does not match this class %s" % (subtype, self.__class__)

		# Figure out if we are in single or multiple mode
		# Short mode:     NOp(*args, (0, 1))
		# Multiple Mode:  NOp(*args, 0, 1)
		short = (len(args) == len(self.names))

		for name, type in self.names:
			struct, size = ARG_STRUCTMAP[type]

			if short:
				size = 1

			if size == 1:
				setattr(self, name, args[0])
			else:
				if len(args) < size:
					raise ValueError("Incorrect number of arguments, the arguments required for %s (of type %s) are %s" % (name, type, struct))
				setattr(self, name, args[:size])

			args = args[size:]
	
		# FIXME: Need to figure out the length a better way
		self.length = len(self.__str__()) - Header.size

	def __str__(self):
		args = []
		for name, type in self.names:
			struct, size = ARG_STRUCTMAP[type]
			
			attr = getattr(self, name)
			if size == 1:
				args.append(attr)
			else:
				args += list(attr)

		output = Order.__str__(self)
		try:
			output += pack(self.substruct, *args)
			return output
		except TypeError, e:
			s = str(e)

			causedby = '%s %s' % self.names[int(s[:s.find(' ')])]
			being    = getattr(self, name)

			traceback = sys.exc_info()[2]
			while not traceback.tb_next is None:
				traceback = traceback.tb_next

			raise TypeError, '%s was %s\n%s' % (causedby, being, e), traceback


	def __repr__(self):
		return "<netlib.objects.OrderExtra.DynamicOrder - %s @ %s>" % (self._name, hex(id(self)))

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
	struct="I SS [SIS] T"

	def __init__(self, sequence, \
			id, name, description, \
			arguments, modify_time):
		Description.__init__(self, sequence, id)

		self._name = name
		self.description = description
		self.arguments = arguments
		self.modify_time = modify_time

		self.length = 4 + \
			4 + len(name) + \
			4 + len(description) + \
			4 + 8 

		for argument in arguments:
			self.length += \
				4 + len(argument[0]) + \
				4 + \
				4 + len(argument[2])

	def __str__(self):
		output = Description.__str__(self)
		output += pack(self.struct, \
				self.id, \
				self._name, \
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

		DynamicOrder._name = self._name
		DynamicOrder.doc = self.description

		# Arguments
		DynamicOrder.names = []
		DynamicOrder.subtype = self.id
	
		DynamicOrder.substruct = ""
		for name, type, desc in self.arguments:
			struct, size = ARG_STRUCTMAP[type]

 			DynamicOrder.names.append((name, type))
			DynamicOrder.substruct += struct
			setattr(DynamicOrder, name + "__doc__", desc)

		DynamicOrder.modify_time = self.modify_time
		DynamicOrder.packet = self

		return DynamicOrder

	def register(self):
		descriptions(self.build())
		
__all__ = ["descriptions", "OrderDesc"]

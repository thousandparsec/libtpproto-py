
from xstruct import pack

from Description import Description
from Constants import *

# Import prebuild orders
from ObjectDesc import *
_descriptions = None
def descriptions(added=None):
	global _descriptions
 
	if _descriptions == None:
		_descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.subtype ] = added
        return _descriptions

struct_map = {
	ARG_ABS_COORD: ("qqq", 3),
	ARG_TIME: ("I", 1),
	ARG_OBJECT: ("I", 1),
	ARG_PLAYER: ("I", 1),
	ARG_RANGE: ("I", 1),
}

from Order import Order
class DynamicDesc(Order):
	"""\
	An Order Type built by a OrderDesc.
	"""
	substruct = ""
	subtype = -1

	def __init__(self, sequence, \
			id, type, slot, turns, resources, \
			*args):
		Order.__init__(self, sequence, \
			id, type, slot, turns, resources)

		if len(self.names) != len(args):
			# FIXME: Must throw error here
			raise ValueError("Not enough arguments.")

		for name, type in self.names:
			struct, size = struct_map[size]

			setattr(self, name, args[0:size])
			args = args[size:]

	def __repr__(self):
		args = []
		for name, type in self.names:
			for attr in getattr(self, name):
				try:
					args += attr
				except:
					args.append(attr)
	
		output = Order.__repr__(self)
		output += apply(pack, (self.substruct,) + args)
		return output

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
	struct="I SS [SIS]"

	def __init__(self, sequence, \
			id, name, description, \
			arguments):
		Description.__init__(self, sequence, id)

		self.name = name
		self.description = description
		self.arguments = arguments

		descriptions(self.build())

	def __repr__(self):
		output = Description.__repr__(self)
		output += pack(self.struct, \
				self.id, \
				self.name, \
				self.description, \
				self.arguments)

		return output

	def build(self):
		"""\
		*Internal*

		Builds a class from this description.
		"""
		class C(DynamicDesc):
			pass

		C.name = self.name
		C.__doc__ = self.description

		# Arguments
		C.names = []
		C.subtype = self.id
	
		for name, type, desc in self.arguments:
			struct, size = struct_map[type]

 			C.names.append((name, type))
			C.substruct += struct
			setattr(C, name + "__doc__", desc)

		return C

__all__ = ["descriptions", "OrderDesc"]

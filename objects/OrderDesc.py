
from xstruct import pack

from Description import Description

_descriptions = None
def descriptions(added=None):
        global _descriptions
 
        if _descriptions == None:
                _descriptions = import_subtype(edir(__file__))
	
	if added != None:
		_descriptions[ added.type ] = added
        return _descriptions


# Constants
ARG_COORD = 0
ARG_TIME = 1
ARG_OBJECT = 2
ARG_PLAYER = 3  

def buildstruct(parameters):
	for name, type, desc in parameters:
 		if type == ARG_COORD:
			struct += "qqq "
 		elif type == ARG_TIME:
 			struct += "I "
		elif type == ARG_OBJECT:
			struct += "I "
		elif type == ARG_PLAYER:
			struct += "I " 
		elif type == ARG_RANGE:
 			pass
 
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
		Description.__init__(self, sequence)

		self.id = id
		self.name = name
		self.description = description
		self.arguments = arguments
	
	def __repr__(self):
		output = Description.__repr__(self)
		output += pack(self.struct, \
				self.id, \
				self.name, \
				self.description, \
				self.arguments)

		return output
	

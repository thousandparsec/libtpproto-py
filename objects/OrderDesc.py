
from xstruct import pack

from Header import Processed

# Import prebuilt orders
from ObjectDesc import *

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
 
class OrderDesc(Processed):
	"""\
	The OrderDesc packet consists of:
		* int32 order type
		* string name
		* string description
		* int32 number of parameters
		* A list of,
			* Argument Name
			* Argument Type
			* Argument Description

		IE
		Name: Drink With Friends
		Description: Go to the pub and drink with friends
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

	no = 0
	struct="L SS [SSI]"

	def __init__(self, sequence, s=""):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (32 bit integer)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(s) + 1
		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.s)

		return output


from xstruct import pack

from Header import Processed

# Where we store incoming desciptions so they can be accessed by Order
descriptions = {}

# Import prebuilt orders


# Constants
ARG_COORD = 0
ARG_TIME = 1
ARG_OBJECT = 2
ARG_PLAYER = 3  

def buildstruct(param):
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
 			
 
class OrderDesc(Processed):
	"""\
	The OrderDesc packet consists of:
		* A string 

		Argument Name
		Argument Description
		Argument Type
		Argument Extra

		IE
		Name: Drink With Friends
		Description: Go to the pub and drink with friends
		Arguments:
			Name: How Long
			Description: How many turns to drink for.
			Type: ARG_TIME

			Name: Who With
			Description: Which player to drink with.
			Type: ARG_PLAYER

			Name: Where
			Description: Where to go drinking.
			Type: ARG_COORD

			Name: Cargo
			Description: How much beer to drink.
			Type: ARG_INT

	Structure for the data:
		<uint32><uint32><int64><int64><int64><uint32>

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

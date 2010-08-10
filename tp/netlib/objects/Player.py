
from xstruct import pack

from Header import Processed

class Player(Processed):
	"""\
	The Player packet consists of:
		* a UInt32, the Player id
		* a String, the Player's name
		* a String, the Race's name
	"""
	no = 40
	struct = "ISST"

	def __init__(self, sequence, id, name, race_name, modify_time):
		Processed.__init__(self, sequence)

		self.id = id
		self.name = name
		self.race_name = race_name
		self.modify_time = modify_time

	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.id, self.name, self.race_name, self.modify_time)

		return output
	

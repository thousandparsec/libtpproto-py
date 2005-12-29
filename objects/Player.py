
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
	struct = "ISS"

	def __init__(self, sequence, id, name, race_name):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + \
			4 + len(name) + \
			4 + len(race_name)
			
		self.id = id
		self.name = name
		self.race_name = race_name

	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.name, self.race_name)

		return output
	


from xstruct import pack

from Header import Processed

class Board(Processed):
	"""\
	The Board packet consists of:
		* UInt32, ID of Board
			0 - Private system board for current player
		* A String, Name of the Board
		* A String, Description of the Board
		* UInt32, Number of messages on the Board.
	"""
	no = 17
	struct = "ISSI"

	def __init__(self, sequence, id, name, desc, number):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + \
				4 + len(name) + 1 + \
				4 + len(desc) + 1 + \
				4

		self.id = id
		self.name = name
		self.desc = desc
		self.number = number
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.name, self.desc, self.number)

		return output

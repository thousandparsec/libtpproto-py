
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
	struct = "ISSIQ"

	def __init__(self, sequence, id, name, description, number, modify_time):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + \
				4 + len(name) + \
				4 + len(description) + \
				4 + 8

		self.id = id
		self.name = name
		self.description = description
		self.number = number
		self.modify_time = modify_time
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.name, self.description, self.number, self.modify_time)

		return output

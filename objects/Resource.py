
from xstruct import pack

from Header import Processed

class Resource(Processed):
	"""\
	"""
	no = 23
	struct = ""

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


from xstruct import pack

from Header import Processed

class Category(Processed):
	"""\
	The Category packet consists of:
		* a UInt32, Category ID
		* a SInt64, the last modified time
		* a String, name of the category
		* a String, description of the category
	"""
	no = 42
	struct = "IpSS"

	def __init__(self, sequence, id, modify_time, name, description):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 8 + \
				4 + len(name) + \
				4 + len(description)

		self.id = id
		self.modify_time = modify_time
		self.name = name
		self.description = description
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.modify_time, self.name, self.description)

		return output

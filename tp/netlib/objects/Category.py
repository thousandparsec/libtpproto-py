
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
	struct = "ITSS"

	def __init__(self, sequence, id, modify_time, name, description):
		Processed.__init__(self, sequence)

		self.id = id
		self.modify_time = modify_time
		self.name = name
		self.description = description
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.id, self.modify_time, self.name, self.description)

		return output

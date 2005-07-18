
from xstruct import pack

from Header import Processed

class Category(Processed):
	"""\
	The Category packet consists of:
		* a UInt32, Category ID
		* a UInt64, the last modified time
		* a String, name of the category
		* a String, description of the category
	"""
	no = 42
	struct = "IQSS"

	def __init__(self, sequence, id, modify_time, name, desc):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 8 + \
				4 + len(name) + \
				4 + len(desc)

		self.id = id
		self.modify_time = modify_time
		self.name = name
		self.desc = desc
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.name, self.desc)

		return output

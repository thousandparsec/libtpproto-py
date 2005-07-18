
from xstruct import pack

from Header import Processed

class Property(Processed):
	"""\
	The Property packet consists of:
		* a UInt32, property ID
		* a UInt64, the last modified time
		* a list of,
			* a UInt32, category ID the property is in
		* a UInt32, rank of property
		* a String, name of property
		* a String, description of the property
		* a String, NCL "Calculate" function
	"""
	no = 59
	struct = "IQ[I]ISSS"

	def __init__(self, sequence, id, modify_time, categories, name, description, calculate):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + 8 + \
				4 + len(categories)*4 + \
				4 + len(name) + \
				4 + len(description) + \
				4 + len(calculate)

		self.id = id
		self.modify_time = modify_time
		self.categories = categories
		self.name = name
		self.description = description
		self.calculate = calculate
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.categories, self.name, self.description, self.calculate)

		return output

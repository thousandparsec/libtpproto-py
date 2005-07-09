
from xstruct import pack

from Header import Processed

class Property(Processed):
	"""\
	The Property packet consists of:
		* a UInt32, property ID
		* a list of,
			* a UInt32, category ID the property is in
		* a UInt32, rank of property
		* a String, name of property
		* a String, description of the property
		* a String, NCL "Calculate" function
	"""
	no = 59
	struct = "I[I]ISSS"

	def __init__(self, sequence, id, categories, name, description, display):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + \
				4 + len(categories)*4 + \
				4 + len(name) + \
				4 + len(description) + \
				4 + len(display) 

		self.id = id
		self.categories = categories
		self.name = name
		self.description = description
		self.display = display
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.categories, self.name, self.description, self.display)

		return output

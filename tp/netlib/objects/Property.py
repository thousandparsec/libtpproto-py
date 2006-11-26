
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
		* a String, name of property (must be a valid TPCL identifier)
		* a String, display name of property
		* a String, description of the property
		* a String, NCL "Calculate" function
		* a String, NCL "Requirements" function
		* a UInt32, a list of special attributes, possible attributes include
			* 0x000001 - Hidden, do not display this property - it is only use in calculations
	"""
	no = 59
	struct = "IQ[I]ISSSSS"

	def __init__(self, sequence, id, modify_time, categories, rank, name, display_name, description, calculate, requirements):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 8 + \
				4 + len(categories)*4 + \
				4 + \
				4 + len(name) + \
				4 + len(display_name) + \
				4 + len(description) + \
				4 + len(calculate) + \
				4 + len(requirements)

		self.id = id
		self.modify_time = modify_time
		self.categories = categories
		self.rank = rank
		self.name = name
		self.display_name = display_name
		self.description = description
		self.calculate = calculate
		self.requirements = requirements
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.modify_time, self.categories, self.rank, self.name, self.display_name, self.description, self.calculate, self.requirements)

		return output

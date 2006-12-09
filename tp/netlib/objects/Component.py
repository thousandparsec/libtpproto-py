
from xstruct import pack

from Header import Processed

class Component(Processed):
	"""\
	The Component packet consists of:
		* a UInt32, Component ID
		* a UInt64, the last modified time
		* a list of,
			* a UInt32, Category ID the Component is in
		* a String, name of component
		* a String, description of the component
		* a String, NCL "Requirements" function
		* a list of,
			* a UInt32, Property ID
			* a String, NCL "Property Value" function
	"""
	no = 55
	struct = "IT[I]SSS[IS]"

	def __init__(self, sequence, id, modify_time, categories, name, description, requirements, properties):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + 8 + \
				4 + len(categories)*4 + \
				4 + len(name) + \
				4 + len(description) + \
				4 + len(requirements) 

		for x, value in properties:
			self.length += 4 + 4 + len(value)

		self.id = id
		self.modify_time = modify_time
		self.categories = categories
		self.name = name
		self.description = description
		self.requirements = requirements
		self.properties = properties
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.modify_time, self.categories, self.name, self.description, self.requirements, self.properties)

		return output

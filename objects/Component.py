
from xstruct import pack

from Header import Processed

class Component(Processed):
	"""\
	The Component packet consists of:
	    * a UInt32, component ID
		* a UInt32, base component ID
		* a UInt32, the number of times this component is in used
		* a list of UInt32, component types
		* a String, name of component
		* a String, description of component
		* a list of,
			* a UInt32, component ID
			* a UInt32, number of the components
		* a list as described in Component Language section
		    * a UInt8, the operand
		    * a UInt32, the number of components
		    * a UInt32, the component category or ID
	"""
	no = 1046
	struct = "III[I]SS[II][BII]"

	def __init__(self, sequence, id, base, used, types, name, description, contains, language):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + 4 + \
				4 + len(types)*4 + \
				4 + len(name) + 1 + \
				4 + len(description) + 1 + \
				4 + len(contains)*(4 + 4) + \
				4 + len(language)*(1 + 4 + 4)

		self.id = id
		self.base = base
		self.used = used
		self.types = types
		self.name = name
		self.description = description
		self.contains = contains
		self.language = language
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.base, self.used, self.types, self.name, self.description, self.contains, self.language)

		return output

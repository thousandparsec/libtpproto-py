
from xstruct import pack

from Header import Processed

class Component(Processed):
	"""\
	The Component packet consists of:
	    * a UInt32, component ID
		* a UInt32, base component ID
		* a UInt32, the number of times this component is in use
		* a list of UInt32, component types
		* a String, name of component
		* a list of,
			  o a UInt32, component ID
			  o a UInt32, number of the components
		* a list as described in Component Language section
		    *  a UInt8, the operand
		    * a UInt32, the number of components
		    * a UInt32, the component category or ID
	"""
	no = 32
	struct = "III[I]S[II][BII]"

	def __init__(self, sequence, id, base, use, types, name, contains, language):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + 4 + \
				4 + len(types)*4 + \
				4 + len(name) + 1 + \
				4 + len(contains)*4 + \
				4 + len(language)*(1 + 4 + 4)

		self.id = id
		self.base = base
		self.use = use
		self.types = types
		self.name = name
		self.contains = contains
		self.language = language
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.base, self.use, self.types, self.name, self.contains, self.language)

		return output


from xstruct import pack

from Header import Processed

class Design(Processed):
	"""\
	The Design packet consists of:
	    * a UInt32, design ID
		* a list of,
			* a UInt32, category this design is in
	    * a String, name of the design
    	* a String, description of the design
		* a SInt32, number of times in use
		* a UInt32, owner of the design
		* a String, design feedback
		* a list of,
			* a UInt32, property value
			* a String, property display string
	"""
	no = 48
	struct = "I[I]SSjIS[IS]"

	def __init__(self, sequence, id, categories, name, description, use, owner, feedback, properties):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + \
				4 + len(categories)*4 \
				4 + len(name) + \
				4 + len(desc) + \
				4 + 4 + \
				4 + len(feedback)

		for value, s in properties:
			self.length += 4 + 4 + len(s)

		self.id = id
		self.categories = categories
		self.name = name
		self.description = description
		self.use = use
		self.owner = owner
		self.feedback = feedback
		self.properpties = properties
		
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.categories, self.name, self.description, self.use, self.owner, self.feedback, self.properties)

		return output

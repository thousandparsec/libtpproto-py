
from xstruct import pack

from Header import Processed

class Object_GetById(Processed):
	"""\
	The Object_Get packet consists of:
		* A uint32, ID of object to get.
	"""

	no = 5
	struct = "[I]"

	def __init__(self, sequence, ids):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - id)
		#
		self.length = 4 + 4 * len(ids)

		self.ids = ids
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.ids)

		return output


import copy
from Design import Design

class Design_Add(Design):
	no = 49
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 49
		apply(Design.__init__, (self, sequence, id,)+args, kw)
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.id, -1, self.categories, self.name, self.desc, -1, self.owner, self.components, "", [])
		return output

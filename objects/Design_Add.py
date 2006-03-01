
import copy
from Design import Design

class Design_Add(Design):
	no = 49
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 49
		apply(Design.__init__, (self, sequence, id,)+args, kw)
	
	def __str__(self):
		output1 = pack(self.struct, self.id, -1, self.categories, self.name, self.desc, -1, self.owner, self.components, "", [])
		
		self.length = len(output1)
		output2 = Processed.__str__(self)

		return output2+output1

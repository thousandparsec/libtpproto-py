
import copy
from Design import Design

class Design_Modify(Design):
	no = 50
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 50
		apply(Design.__init__, (self, sequence, id,)+args, kw)

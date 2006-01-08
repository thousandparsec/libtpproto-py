
import copy
from Design import Design

class Design_Add(Design):
	no = 49
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 49
		apply(Design.__init__, (self, sequence, id,)+args, kw)

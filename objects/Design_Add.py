
import copy
from Order import Order

class Design_Add(Order):
	no = 49
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 49
		apply(Design.__init__, (self, sequence, id,)+args, kw)

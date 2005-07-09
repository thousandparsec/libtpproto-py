
import copy
from Order import Order

class Design_Modify(Order):
	no = 50
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 50
		apply(Design.__init__, (self, sequence, id,)+args, kw)

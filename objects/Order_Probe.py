
import copy
from Order import Order

class Order_Probe(Order):
	no = 28
	def __init__(self, sequence, \
			id,	slot, type, \
			*args, **kw):
		self.no = 28
		apply(Order.__init__, (self, sequence, id, slot, type, -1, [])+args, kw)

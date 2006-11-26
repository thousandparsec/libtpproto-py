
import copy
from Order import Order

class Order_Probe(Order):
	no = 34
	def __init__(self, sequence, \
			id,	slot, type, \
			*args, **kw):
		self.no = 34
		apply(Order.__init__, (self, sequence, id, slot, type, -1, [])+args, kw)

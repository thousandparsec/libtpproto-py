
import copy
from Order import Order

class Order_Insert(Order):
	no = 12
	def __init__(self, sequence, \
			id,	slot, type, \
			*args, **kw):
		self.no = 12
		apply(Order.__init__, (self, sequence, id, slot, type, -1, [])+args, kw)

		# FIXME: This is a hack :)
		if self.slot == 4294967295:
			self.slot = -1

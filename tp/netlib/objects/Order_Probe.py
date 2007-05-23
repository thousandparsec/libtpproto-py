
import copy
from Order import Order

class Order_Probe(Order):
	no = 34
	def __init__(self, *args, **kw):
		self.no = 34
		Order.__init__(self, *args, **kw)

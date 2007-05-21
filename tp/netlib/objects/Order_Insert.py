
import copy
from Order import Order

class Order_Insert(Order):
	no = 12
	def __init__(self, *args, **kw):
		self.no = 12
		Order.__init__(self, *args, **kw)

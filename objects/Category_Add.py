
import copy
from Order import Order

class Category_Add(Order):
	no = 43
	def __init__(self, sequence, \
			id,	\
			*args, **kw):
		self.no = 43
		apply(Category.__init__, (self, sequence, id,)+args, kw)


import copy
from Component import Component

class Component_Insert(Component):
	no = 33
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 33
		apply(Component.__init__, (self, sequence, id)+args, kw)

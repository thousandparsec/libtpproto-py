
import copy
from Component import Component

class Component_Insert(Component):
	no = 1047
	def __init__(self, sequence, \
			id, \
			*args, **kw):
		self.no = 1047
		apply(Component.__init__, (self, sequence, id)+args, kw)

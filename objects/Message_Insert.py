
import copy
from Message import Message

class Message_Insert(Message):
	no = 20
	def __init__(self, sequence, \
			id,	slot, type, \
			*args, **kw):
		self.no = 20
		apply(Order.__init__, (self, sequence, id, slot)+args, kw)

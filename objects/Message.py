
from xstruct import pack

from Header import Processed

class Message(Processed):
	"""\
	The Message packet consists of:
		* UInt32, ID of Board
		* UInt32, Slot of Message
		* a list of UInt32, Type of message
		* a string, Subject of message
		* a string, Body of the message
	"""
	no = 19
	struct = "II[I]SS"

	def __init__(self, sequence, id, slot, types, subject, body):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + \
				4 + len(types)*4 + \
				4 + len(subject) + 1 + \
				4 + len(body) + 1 

		self.id = id
		self.slot = slot
		self.types = types
		self.subject = subject
		self.body = body
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.slot, self.types, self.subject, self.body)

		return output

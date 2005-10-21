
from xstruct import pack

from Header import Processed

class Message(Processed):
	"""\
	The Message packet consists of:
		* UInt32, ID of Board
		* SInt32, Slot of Message
		* a list of UInt32, Type of message
		* a string, Subject of message
		* a string, Body of the message
                * UInt32, turn number the messages was generated on
                * a list of Int32, UInt32 references
	"""
	no = 19
	struct = "Ij[I]SSI[II]"

	def __init__(self, sequence, id, slot, types, subject, body, turn, references):
		Processed.__init__(self, sequence)

		# Length is:
		#
		self.length = 4 + 4 + \
				4 + len(types)*4 + \
				4 + len(subject) + \
				4 + len(body) + \
                                4 + len(references)

		self.id = id
		self.slot = slot
		self.types = types
		self.subject = subject
		self.body = body
                self.turn = turn
                self.references = references
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.slot, self.types, self.subject, self.body, self.turn, self.references)

		return output


from warnings import warn

from xstruct import pack

from Header import Processed
import GenericRS

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
	struct = "Ij[I]SSI[iI]"

	def __init__(self, sequence, id, slot, types, subject, body, turn, references):
		Processed.__init__(self, sequence)

		if not isinstance(references, GenericRS.References):
			references = GenericRS.References(references)

		# Length is:
		#
		self.length = 4 + 4 + \
				4 + len(types)*4 + \
				4 + len(subject) + \
				4 + len(body) + \
				4 + \
				4 + len(references)*(4*4)

		self.id = id
		self.slot = slot
		self.types = types
		self.subject = subject
		self.body = body
		self.turn = turn
		self.references = references
	
	def get_types(self):
		warn("Messages.types is deperciated use the Message.references instead.", DeprecationWarning, stacklevel=2)
		return self.__types
	def set_types(self, value):
		self.__types = value
		if len(value) != 0:
			warn("Messages.types is deperciated use the Message.references instead.", DeprecationWarning, stacklevel=2)
	types = property(get_types, set_types)

	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.slot, [], self.subject, self.body, self.turn, self.references.references)

		return output

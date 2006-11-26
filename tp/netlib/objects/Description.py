
from xstruct import pack

from Header import Processed

class DescriptionError(Exception):
	"""\
	Thrown by objects which can't find the description which describes
	them.
	"""
	pass

class Describable(Processed):
	"""\
	The Describable packet uses other packets to describe "extra" details
	about the packet.
	"""
	pass

class Description(Processed):
	"""\
	The Description packet contains the description of another type of
	packet.

	The id is equal to the subtype.
	"""
	def __init__(self, sequence, id):
		Processed.__init__(self, sequence)
		self.id = id


from xstruct import pack, unpack
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
	substruct = ""

	def __process__(self, data, **kw):
		# Unpack the first lot of data
		args, leftover = unpack(self.struct, data)
		self.__init__(self.sequence, *args, **kw)

		# Unpack the second lot of data
		moreargs, leftover = unpack(self.substruct, leftover)
		if len(leftover) > 0:
			raise ValueError("Data: %s Structure: %s Extra Data found: %s" % (repr(data), self.substruct, repr(leftover)))

		self.__init__(self.sequence, *(args + moreargs))

class Description(Processed):
	"""\
	The Description packet contains the description of another type of
	packet.

	The id is equal to the subtype.
	"""
	def __init__(self, sequence, id):
		Processed.__init__(self, sequence)
		self.id = id



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

		if hasattr(self.__class__, "__process__"):
			return self.__class__.__process__(self, leftover, **kw)

		# Unpack the second lot of data
		try:
			moreargs, leftover2 = unpack(self.substruct, leftover)
			if len(leftover2) > 0:
				raise ValueError("\nError when processing %s.\nClass Structure: %s, Given Data: %r\nExtra data found: %r " % (self.__class__, self.substruct, leftover, leftover2))
		except TypeError, e:
			raise ValueError("\nError when processing %s.\nClass Structure: %s, Given Data: %r\nNot enough data found: %s" % (self.__class__, self.substruct, leftover, e))

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


